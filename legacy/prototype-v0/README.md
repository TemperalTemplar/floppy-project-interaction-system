# Original Prototype Archive

This directory preserves the exact ZIP supplied as the prototype point of origin for the Floppy Project Interaction System.

The archive is stored as ordered Base64 text parts because this repository was initialized through a text-oriented GitHub interface. The parts are preservation data, not active project files.

## Reconstruct the original ZIP

From this directory on macOS or Linux:

```bash
cat archive/Floppy_Project_Interactions.zip.b64.part* | base64 -d > Floppy_Project_Interactions.zip
```

On Windows PowerShell, concatenate the parts as text and decode the combined Base64 value:

```powershell
$base64 = (Get-Content .\archive\Floppy_Project_Interactions.zip.b64.part* -Raw) -join ''
[IO.File]::WriteAllBytes('.\Floppy_Project_Interactions.zip', [Convert]::FromBase64String($base64))
```

## Integrity check

```text
SHA-256: db11b8437bc0046d3542db3c029c223d458865a4b1da2c6aac80759c336cbe96
```

Do not use this archive as an active project repository. It is retained only for provenance, recovery, and comparison with the current source system.
