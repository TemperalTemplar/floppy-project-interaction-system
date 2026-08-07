from __future__ import annotations
import hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load_cli():
 spec=importlib.util.spec_from_file_location("floppyctl_fs12",ROOT/"tools/floppyctl.py"); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module); return module
CLI=load_cli()
def load_validator():
 spec=importlib.util.spec_from_file_location("validate_floppy_fs12",ROOT/"tools/validate_floppy.py"); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module); return module
VALIDATOR=load_validator()
def git(root,*args):
 p=subprocess.run(["git","-c",f"safe.directory={root.as_posix()}","-C",str(root),*args],text=True,capture_output=True); assert p.returncode==0,p.stdout+p.stderr; return p.stdout.strip()
def canonical(v): return (json.dumps(v,sort_keys=True,separators=(",",":"))+"\n").encode()
class Fixture:
 def __init__(self,state="LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE",migration="NONE"):
  self.t=tempfile.TemporaryDirectory(); self.root=Path(self.t.name)/"repo"; self.root.mkdir(); self.branch="fixture"; self._write(state,migration); git(self.root,"init","-b",self.branch); git(self.root,"config","user.email","fs12@example.invalid"); git(self.root,"config","user.name","FS12 Tests"); git(self.root,"add","."); git(self.root,"commit","-m","fixture"); self.refresh()
 def _write(self,state,migration):
  dims={"roadmap":"ACCEPTED","work_package":"NOT_ACCEPTED","authority":"NO_ACTIVE_WORK_AUTHORIZATION","implementation":"NOT_STARTED","verification":"COMPLETE" if migration!="NONE" else "NOT_STARTED","acceptance":"PENDING","closeout":"APPLIED","migration":migration,"final_closure":"OPEN"}
  files={".floppy/lifecycle-state.json":canonical({"state_id":state,"section":None,"authorization_id":None,"base_checkpoint":"0"*40,"dimensions":dims,"active_implementation_sections":[],"evidence":["fixture"]}),".floppy/manifest.json":json.dumps({"status":state,"active_work_authorization":None,"active_control_work_authorization":None,"repository_writer":None,"writer_authorization_reference":None,"authority":{"authority_state":"NO_ACTIVE_WORK_AUTHORIZATION"}},indent=2).encode()+b"\n",".floppy/orchestrator-registry.json":canonical({"current_assignments":{"current_section_working_model":None,"repository_writer":None,"writer_authorization_reference":None},"rules":{"maximum_repository_writers":1,"writer_requires_exact_authorization_reference":True,"status_or_role_grants_write_authority":False},"orchestrators":[{"id":"PROJECT_ORCHESTRATOR","status":"ACTIVE"}]}),".floppy/roadmap/roadmap.json":json.dumps({"lifecycle_state":state,"sections":[{"id":"FS-%02d"%i,"status":"CLOSED"} for i in range(1,14)]},indent=2).encode()+b"\n"}
  for p in [".floppy/README.md",".floppy/START-HERE.md",".floppy/floppies/Floppy-D-Project-Map.md",".floppy/floppies/Floppy-E-Current-Section.md",".floppy/roadmap/roadmap.md"]: files[p]=b"fixture\n"
  for p,b in files.items(): q=self.root/p; q.parent.mkdir(parents=True,exist_ok=True); q.write_bytes(b)
 def refresh(self): self.head=git(self.root,"rev-parse","HEAD")
 def plan(self,action="propose",**kw): return CLI._fs12_final_closure_operation(self.root,mode="dry-run",action=action,expected_branch=self.branch,expected_head=self.head,evidence=kw.pop("evidence",["FS-13 closeout"]),**kw)
 def apply(self,plan,action="propose",**kw): return CLI._fs12_final_closure_operation(self.root,mode="apply",action=action,expected_branch=self.branch,expected_head=self.head,evidence=kw.pop("evidence",["FS-13 closeout"]),plan_sha256=plan["plan_sha256"],**kw)
 def close(self): CLI._FS12_TEST_HOOK=None; self.t.cleanup()
class FinalClosureTests(unittest.TestCase):
 def tearDown(self):
  if hasattr(self,"f"): self.f.close()
 def test_schema_registers_both_no_migration_states(self):
  s=json.loads((ROOT/"schemas/bce/1.2.0/bce-lifecycle-state.schema.json").read_text()); enum=s["$defs"]["lifecycle_state_identifier"]["enum"]; self.assertIn("LC-PROJECT-CLOSURE-PROPOSED-NO-MIGRATION",enum); self.assertIn("LC-PROJECT-FINALLY-CLOSED-NO-MIGRATION",enum)
 def test_no_migration_dry_run_is_deterministic(self):
  self.f=Fixture(); self.assertEqual(self.f.plan(),self.f.plan())
 def test_no_migration_proposal_preserves_none(self):
  self.f=Fixture(); p=self.f.plan(); self.f.apply(p); life=json.loads((self.f.root/".floppy/lifecycle-state.json").read_text()); self.assertEqual(life["state_id"],"LC-PROJECT-CLOSURE-PROPOSED-NO-MIGRATION"); self.assertEqual(life["dimensions"]["migration"],"NONE")
 def test_migration_applied_proposal_uses_tr014(self):
  self.f=Fixture("LC-MIGRATION-APPLIED-VERIFICATION-COMPLETE","APPLIED_VERIFICATION_COMPLETE"); p=self.f.plan(); self.assertEqual(p["transition"],"TR-014-PROPOSE-FINAL-CLOSURE")
 def test_proposal_requires_final_evidence(self):
  self.f=Fixture();
  with self.assertRaises(CLI.CliError): self.f.plan(evidence=[])
 def test_proposal_rejects_open_section(self):
  self.f=Fixture(); r=json.loads((self.f.root/".floppy/roadmap/roadmap.json").read_text()); r["sections"][-1]["status"]="INACTIVE"; (self.f.root/".floppy/roadmap/roadmap.json").write_text(json.dumps(r,indent=2)+"\n"); git(self.f.root,"add","."); git(self.f.root,"commit","-m","open"); self.f.refresh();
  with self.assertRaises(CLI.CliError): self.f.plan()
 def test_proposal_rejects_active_authority(self):
  self.f=Fixture(); m=json.loads((self.f.root/".floppy/manifest.json").read_text()); m["active_work_authorization"]={"authorization_id":"X"}; (self.f.root/".floppy/manifest.json").write_text(json.dumps(m,indent=2)+"\n"); git(self.f.root,"add","."); git(self.f.root,"commit","-m","auth"); self.f.refresh();
  with self.assertRaises(CLI.CliError): self.f.plan()
 def _proposal_commit(self):
  self.f=Fixture(); p=self.f.plan(); self.f.apply(p); git(self.f.root,"add","."); git(self.f.root,"commit","-m","propose"); self.f.refresh(); m=json.loads((self.f.root/".floppy/manifest.json").read_text()); return m["final_closure_proposal"]["proposal_sha256"]
 def test_application_requires_exact_authority(self):
  d=self._proposal_commit();
  with self.assertRaises(CLI.CliError): self.f.plan(action="apply",proposal_sha256=d)
 def test_application_requires_reviewed_digest(self):
  d=self._proposal_commit();
  with self.assertRaises(CLI.CliError): self.f.plan(action="apply",proposal_sha256="0"*64,authorization_reference="FINAL_CLOSURE_APPLICATION")
 def test_no_migration_application_reaches_distinct_final_state(self):
  d=self._proposal_commit(); p=self.f.plan(action="apply",proposal_sha256=d,authorization_reference="FINAL_CLOSURE_APPLICATION"); self.f.apply(p,action="apply",proposal_sha256=d,authorization_reference="FINAL_CLOSURE_APPLICATION"); life=json.loads((self.f.root/".floppy/lifecycle-state.json").read_text()); self.assertEqual(life["state_id"],"LC-PROJECT-FINALLY-CLOSED-NO-MIGRATION"); self.assertEqual(life["dimensions"]["migration"],"NONE")
 def test_tampered_proposal_is_rejected(self):
  d=self._proposal_commit(); path=self.f.root/CLI._FS12_FINAL_RECORD; path.write_text(path.read_text().replace("FS-13 closeout","tampered")); git(self.f.root,"add","."); git(self.f.root,"commit","-m","tamper"); self.f.refresh();
  with self.assertRaises(CLI.CliError): self.f.plan(action="apply",proposal_sha256=d,authorization_reference="FINAL_CLOSURE_APPLICATION")
 def test_cross_route_application_is_rejected(self):
  d=self._proposal_commit(); life=json.loads((self.f.root/".floppy/lifecycle-state.json").read_text()); life["state_id"]="LC-PROJECT-CLOSURE-PROPOSED"; life["dimensions"]["migration"]="APPLIED_VERIFICATION_COMPLETE"; (self.f.root/".floppy/lifecycle-state.json").write_bytes(canonical(life)); git(self.f.root,"add","."); git(self.f.root,"commit","-m","route"); self.f.refresh();
  with self.assertRaises(CLI.CliError): self.f.plan(action="apply",proposal_sha256=d,authorization_reference="FINAL_CLOSURE_APPLICATION")
 def test_partial_write_failure_restores_every_path(self):
  self.f=Fixture(); before={p:((self.f.root/p).read_bytes() if (self.f.root/p).exists() else None) for p in CLI._FS12_FINAL_PATHS}; p=self.f.plan()
  def hook(name,ctx):
   if name=="after_replace" and ctx["count"]==3: raise RuntimeError("injected")
  CLI._FS12_TEST_HOOK=hook
  with self.assertRaises(CLI.CliError): self.f.apply(p)
  after={p:((self.f.root/p).read_bytes() if (self.f.root/p).exists() else None) for p in CLI._FS12_FINAL_PATHS}; self.assertEqual(before,after)
 def test_boot_package_contains_schema_120(self): self.assertIn("schemas/bce/1.2.0/bce-lifecycle-state.schema.json",CLI.BOOT_PACKAGE_FILE_PATHS)
class SourceFixture:
 def __init__(self):
  self.t=tempfile.TemporaryDirectory(); self.root=Path(self.t.name)/"repo"; self.branch="feature/ctrl-02-verification-only-lifecycle"
  shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns(".git","__pycache__","*.pyc","*.pyo"))
  git(self.root,"init","-b",self.branch); git(self.root,"config","user.email","fs12-source@example.invalid"); git(self.root,"config","user.name","FS12 Source Tests"); git(self.root,"config","core.autocrlf","false"); git(self.root,"add","-A"); git(self.root,"commit","-m","source fixture baseline"); git(self.root,"branch","main")
  self.head=git(self.root,"rev-parse","HEAD"); self.main=git(self.root,"rev-parse","main")
 def close(self): self.t.cleanup()
 def _env(self,operation="FINAL_CLOSURE_PROPOSAL_CONTROL",expected_head=None,include_branch=True):
  env=os.environ.copy()
  for key in ("FLOPPY_AUTHORIZATION_REFERENCE","FLOPPY_REPOSITORY_WRITER","FLOPPY_EXPECTED_HEAD","FLOPPY_SCOPE_COMMIT","FLOPPY_CONTROL_OPERATION","FLOPPY_CONTROL_SCOPE","FLOPPY_CONTROL_BRANCH","FLOPPY_EXPECTED_PROJECT_ROOT"):
   env.pop(key,None)
  env["PYTHONDONTWRITEBYTECODE"]="1"
  if operation is not None: env["FLOPPY_CONTROL_OPERATION"]=operation
  env["FLOPPY_EXPECTED_HEAD"]=self.head if expected_head is None else expected_head
  if include_branch: env["FLOPPY_CONTROL_BRANCH"]=self.branch
  return env
 def validate_source(self,operation="FINAL_CLOSURE_PROPOSAL_CONTROL",expected_head=None,include_branch=True):
  return subprocess.run([sys.executable,"-B",str(self.root/"tools/validate_floppy.py"),str(self.root),"--mode","source"],text=True,capture_output=True,env=self._env(operation,expected_head,include_branch),cwd=str(self.root))
 def apply_proposal(self):
  plan=CLI._fs12_final_closure_operation(self.root,mode="dry-run",action="propose",expected_branch=self.branch,expected_head=self.head,evidence=["FS-13 terminal closeout complete"])
  applied=CLI._fs12_final_closure_operation(self.root,mode="apply",action="propose",expected_branch=self.branch,expected_head=self.head,evidence=["FS-13 terminal closeout complete"],plan_sha256=plan["plan_sha256"])
  return plan,applied
 def set_migration_applied_baseline(self):
  table=json.loads((self.root/"specs/lifecycle-transition-table.json").read_text(encoding="utf-8")); states={item["id"]:item for item in table["states"]}; target=states["LC-MIGRATION-APPLIED-VERIFICATION-COMPLETE"]
  life=json.loads((self.root/".floppy/lifecycle-state.json").read_text(encoding="utf-8")); life["state_id"]=target["id"]; life["section"]=None; life["authorization_id"]=None; life["dimensions"]=target["dimensions"]; life["active_implementation_sections"]=[]; life["evidence"]=list(life.get("evidence") or [])+["TEST:MIGRATION_APPLIED_VERIFIED"]; (self.root/".floppy/lifecycle-state.json").write_bytes(canonical(life))
  manifest=json.loads((self.root/".floppy/manifest.json").read_text(encoding="utf-8")); manifest["status"]=target["id"]; (self.root/".floppy/manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
  roadmap=json.loads((self.root/".floppy/roadmap/roadmap.json").read_text(encoding="utf-8")); roadmap["lifecycle_state"]=target["id"]; (self.root/".floppy/roadmap/roadmap.json").write_text(json.dumps(roadmap,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
  git(self.root,"add","--",".floppy/lifecycle-state.json",".floppy/manifest.json",".floppy/roadmap/roadmap.json"); git(self.root,"commit","-m","migration-applied fixture"); self.head=git(self.root,"rev-parse","HEAD")

class FinalClosureSourceValidationTests(unittest.TestCase):
 def setUp(self): self.s=SourceFixture()
 def tearDown(self): self.s.close()
 def assertPasses(self,result): self.assertEqual(result.returncode,0,result.stdout+result.stderr)
 def assertFails(self,result): self.assertNotEqual(result.returncode,0,result.stdout+result.stderr)
 def test_source_validation_accepts_pending_tr021_no_migration_candidate(self):
  self.s.apply_proposal(); result=self.s.validate_source(); self.assertPasses(result); life=json.loads((self.s.root/".floppy/lifecycle-state.json").read_text()); self.assertEqual(life["state_id"],"LC-PROJECT-CLOSURE-PROPOSED-NO-MIGRATION"); self.assertEqual(life["dimensions"]["migration"],"NONE")
 def test_source_validation_rejects_pending_tr021_without_final_closure_operation(self):
  self.s.apply_proposal(); self.assertFails(self.s.validate_source(operation=None))
 def test_source_validation_rejects_pending_tr021_with_wrong_expected_head(self):
  self.s.apply_proposal(); result=self.s.validate_source(expected_head="0"*40); self.assertFails(result); self.assertIn("GIT_INTEGRITY_FINAL_CLOSURE_HEAD_MISMATCH",result.stdout+result.stderr)
 def test_source_validation_rejects_pending_tr021_without_control_branch(self):
  self.s.apply_proposal(); result=self.s.validate_source(include_branch=False); self.assertFails(result); self.assertIn("GIT_INTEGRITY_FINAL_CLOSURE_BRANCH_MISSING",result.stdout+result.stderr)
 def test_final_closure_integrity_counts_untracked_proposal_record(self):
  self.s.apply_proposal(); status=git(self.s.root,"status","--porcelain=v1","--untracked-files=all").splitlines(); self.assertIn("?? .floppy/closeouts/FINAL-PROJECT-CLOSURE.md",status); self.assertPasses(self.s.validate_source())
 def test_final_closure_integrity_rejects_extra_untracked_path(self):
  self.s.apply_proposal(); extra=self.s.root/".floppy/UNAUTHORIZED-FINAL-CLOSURE.txt"; extra.write_text("forbidden\n",encoding="utf-8",newline="\n"); result=self.s.validate_source(); self.assertFails(result); self.assertIn("GIT_INTEGRITY_FINAL_CLOSURE_PATHS_INVALID",result.stdout+result.stderr)
 def test_source_validation_uses_runtime_manifest_proposal_digest(self):
  self.s.apply_proposal(); system=json.loads((self.s.root/"system-manifest.json").read_text(encoding="utf-8")); runtime=json.loads((self.s.root/".floppy/manifest.json").read_text(encoding="utf-8")); self.assertNotIn("final_closure_proposal",system); block,digest=CLI._fs12_proposal_bytes((self.s.root/CLI._FS12_FINAL_RECORD).read_bytes()); self.assertTrue(block); self.assertEqual(runtime["final_closure_proposal"]["proposal_sha256"],digest); self.assertPasses(self.s.validate_source())
 def test_source_validation_rejects_runtime_proposal_digest_mismatch(self):
  self.s.apply_proposal(); path=self.s.root/".floppy/manifest.json"; runtime=json.loads(path.read_text(encoding="utf-8")); runtime["final_closure_proposal"]["proposal_sha256"]="0"*64; path.write_text(json.dumps(runtime,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n"); result=self.s.validate_source(); self.assertFails(result); self.assertIn("canonical final-project closure proposal digest mismatch",result.stdout+result.stderr)
 def test_source_validation_accepts_pending_tr014_migration_applied_candidate(self):
  self.s.set_migration_applied_baseline(); plan,applied=self.s.apply_proposal(); self.assertEqual(plan["transition"],"TR-014-PROPOSE-FINAL-CLOSURE"); self.assertTrue(applied["applied"]); self.assertPasses(self.s.validate_source()); life=json.loads((self.s.root/".floppy/lifecycle-state.json").read_text()); self.assertEqual(life["state_id"],"LC-PROJECT-CLOSURE-PROPOSED"); self.assertEqual(life["dimensions"]["migration"],"APPLIED_VERIFICATION_COMPLETE")
 def test_pending_tr021_does_not_apply_tr022_or_create_fs14(self):
  self.s.apply_proposal(); manifest=json.loads((self.s.root/".floppy/manifest.json").read_text()); life=json.loads((self.s.root/".floppy/lifecycle-state.json").read_text()); roadmap=json.loads((self.s.root/".floppy/roadmap/roadmap.json").read_text()); self.assertNotIn("final_closure_application",manifest); self.assertEqual(life["dimensions"]["final_closure"],"PROPOSED"); self.assertNotEqual(life["state_id"],"LC-PROJECT-FINALLY-CLOSED-NO-MIGRATION"); self.assertFalse((self.s.root/".floppy/templates/Floppy-E-FS-14.draft.md").exists()); self.assertNotIn("FS-14",[item.get("id") for item in roadmap["sections"]]); digest=manifest["final_closure_proposal"]["proposal_sha256"]
  with self.assertRaises(CLI.CliError): CLI._fs12_final_closure_operation(self.s.root,mode="dry-run",action="apply",expected_branch=self.s.branch,expected_head=self.s.head,evidence=["FS-13 terminal closeout complete"],proposal_sha256=digest)
 def test_pending_tr021_does_not_move_main_ref(self):
  before=self.s.main; self.s.apply_proposal(); self.assertEqual(git(self.s.root,"rev-parse","main"),before)

class FinalClosureValidatorContractTests(unittest.TestCase):
 def test_project_seed_validation_remains_schema_100(self):
  self.assertEqual(VALIDATOR.PROJECT_LIFECYCLE_SCHEMA,"schemas/bce/1.0.0/bce-lifecycle-state.schema.json"); system=json.loads((ROOT/"system-manifest.json").read_text(encoding="utf-8")); self.assertEqual(system["project_control_state_provisioning"]["lifecycle_state_schema"],"schemas/bce/1.0.0/bce-lifecycle-state.schema.json"); errors=[]; VALIDATOR.validate_project_seed_provisioning(ROOT,system,errors); self.assertEqual(errors,[])
if __name__=="__main__": unittest.main()
