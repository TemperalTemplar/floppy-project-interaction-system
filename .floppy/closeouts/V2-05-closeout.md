# V2-05 Closeout Proposal

Status: `PROPOSED_NOT_APPLIED`

<!-- V2_05_CLOSEOUT_PROPOSAL_CANONICAL_BEGIN -->
{"active_implementation_authorization":null,"active_work_authorization":null,"administrator_acceptance":"ACCEPTED","administrator_acceptance_checkpoint":"8f5eb0bbea264d4f8304ca5ad0327ce8d49713e7","administrator_acceptance_tree":"65a3fbc6d10809c6898587b12a5bc18e1f276261","application_authorized_by_prior_administrator_directive":true,"application_status":"AUTHORIZED_NOT_APPLIED","application_transition":"TR-009-APPLY-SECTION-CLOSEOUT","closeout":"PROPOSED","closeout_applied":false,"complete_repository_suite":{"attempt":1,"attempt_2_authorized":false,"log_sha256":"facc18471188922f726e820612f919f4638fce7c922b59e5d11c7e3599686e6f","result_json_sha256":"6b1f6a30f19aee1b742319c0daf5887f267f4507d4120332a7b832c2a96ae923","status":"PASSED_CONSUMED","summary":"381 passed, 2 warnings, 148 subtests passed in 326.27s (0:05:26)"},"correction_checkpoint":"527ee33851f5c3ea96fba80d28d92f98fdc9bd6c","correction_tree":"d70d7f4343d3559b91bb82abe26a5e5afcf7eb54","implementation_state":"COMPLETE","lineage":{"A1":"1ea9c9627113c48354b16d0bfdd73554d7b33fa4","A2":"8f5eb0bbea264d4f8304ca5ad0327ce8d49713e7","B1":"620c252306559e54f1a368debd260e70af538c73","C1":"216df8625cb911853123f06ec8c4f9e3f3619195","I1_main":"88a0fa646973c4cb8e693cc4e7c512b537825fd2","P1":"2865fad915795a8316e0681c75852c1a8754c51d","V1":"f5fbf05727610a11dffd3041d94df8439147484c","W1":"f0a8c0e872a7ebeb82ceb74123b4f77a5ee3aed5","verified_tooling_base":"714ee17f4c45b6f6836c4e1896b34e3ccb9835cf"},"main_commit":"88a0fa646973c4cb8e693cc4e7c512b537825fd2","main_tree":"18091c741b6764dc64f84e7c7ab78d039b69b521","migration":"NONE","proposal_base_checkpoint":"527ee33851f5c3ea96fba80d28d92f98fdc9bd6c","proposal_base_tree":"d70d7f4343d3559b91bb82abe26a5e5afcf7eb54","proposal_commit_checkpoint":"THIS_COMMIT","proposal_status":"PROPOSED_NOT_APPLIED","public_release":"PUBLISHED","record_path":".floppy/closeouts/V2-05-closeout.md","repository_writer":null,"section":"V2-05","source_state":"LC-SECTION-ACCEPTED-CLOSEOUT-NOT-PROPOSED","tag":"v2.0.0","tag_target":"88a0fa646973c4cb8e693cc4e7c512b537825fd2","target_state":"LC-SECTION-ACCEPTED-CLOSEOUT-PROPOSED","transition":"TR-008-PROPOSE-SECTION-CLOSEOUT","v2_05_status":"ACCEPTED_CLOSEOUT_PROPOSED_NOT_APPLIED","v2_06":"NONEXISTENT_NOT_AUTHORIZED","validated_boot_inventory":67,"verification_state":"COMPLETE","verified_result_checkpoint":"f5fbf05727610a11dffd3041d94df8439147484c","verified_result_tree":"040645e38fc6d9a5fb27e541c600ef3bcfd528aa"}
<!-- V2_05_CLOSEOUT_PROPOSAL_CANONICAL_END -->

## Accepted terminal result

- V2-05 implementation: COMPLETE
- V2-05 verification: COMPLETE
- Administrator result acceptance: ACCEPTED
- Validated boot inventory: 67
- Complete repository suite Attempt 1: PASSED / CONSUMED
- Clean main: `88a0fa646973c4cb8e693cc4e7c512b537825fd2`
- Clean main tree: `18091c741b6764dc64f84e7c7ab78d039b69b521`
- Tag: `v2.0.0` -> `88a0fa646973c4cb8e693cc4e7c512b537825fd2`
- Public GitHub Release: PUBLISHED
- Migration: NONE
- V2-06: NONEXISTENT_NOT_AUTHORIZED

This proposal changes only the V2-05 closeout dimension from NOT_PROPOSED to
PROPOSED. It does not apply closeout and does not create any later package.
The already-issued administrator directive authorizes the later TR-009
application as a distinct commit; the transitions remain separate.

<!-- V2_05_CLOSEOUT_PROPOSAL_END -->

<!-- V2_05_CLOSEOUT_APPLICATION_BEGIN -->
## V2-05 final closeout application

{"application_status":"APPLIED","application_transition":"TR-009-APPLY-SECTION-CLOSEOUT","approved_proposal_checkpoint":"421689604f3b787846b7283b1ee32133ae3777c2","approved_proposal_sha256":"104cb8305f2788f24051c08e853da823dd381a91aa78015cc08f4caeff40e235","approved_proposal_tree":"8544d186235cacd36af94e1f38797d7113d9d223","closeout":"APPLIED","migration":"NONE","resulting_lifecycle_state":"LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE","section":"V2-05","section_status":"CLOSED","terminal_package":true,"v2_06":"NONEXISTENT_NOT_AUTHORIZED"}

V2-05 is CLOSED. The generic next-section-inactive lifecycle representation is
used only as the legal post-TR-009 state. There is no next V2 package:
`V2-06 = NONEXISTENT_NOT_AUTHORIZED`.

`main` and `v2.0.0` remain unchanged at `88a0fa646973c4cb8e693cc4e7c512b537825fd2`.
<!-- V2_05_CLOSEOUT_APPLICATION_END -->
