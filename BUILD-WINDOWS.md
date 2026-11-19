# NMS 3D Base Aligner — Creating and Publishing a Portable Windows Release

## v1.0.0 build on November 12, 2026

The successful local build produced `dist\NMS-Base-Aligner-Windows-x64-Portable_v1.0.0.zip` (212,407,029 bytes). The archive contains one top-level `NMS-Base-Aligner` folder with `NMS-Base-Aligner.exe`, `_internal` (including the HTML viewer and Qt WebEngine helper), `LICENSE`, `README-Windows.md`, and `How_to_activate_models.md`. The optional app-level `models` folder is distributed separately.

The repository’s `.venv` was verified with Windows x64 Python 3.14.2, PySide6 6.10.2, and PyInstaller 6.19.0. The original November 12 ZIP predates EXE version stamping. Its EXE has blank **File version** and **Product version** fields. The ZIP inspection confirms the package contents. Complete the launch and export checks below and confirm the source commit before publishing. Rebuild from the intended commit if the saved ZIP’s source is uncertain.

SHA-256 of the inspected November 12 ZIP: `803D3F52F6AB148546A6C645B3C58A6BE1DAA47DBA309F2A79F49CD9AEA3F045`.

## 1. Prepare the stable release source

1. In GitHub Desktop, select **No-Mans-Sky-3D-Base-Aligner**. Merge any intended changes from `develop` into `main`, then switch to `main`, fetch, and pull.
2. Review and commit any local changes intended for the release, including build-script or bundled documentation changes. Push the intended release commit to GitHub.
3. Record the commit you will build and tag. In PowerShell at the repository root, use `git status --short --branch` and `git rev-parse HEAD`. Review the working tree before building so local edits to build inputs do not accidentally become part of the ZIP.

## 2. Build the ZIP

### A. Set up `.venv` only when needed

**Already have a working `.venv` with the current build dependencies? Skip to B.** The `.venv` folder persists across PowerShell sessions and Windows restarts. The build script uses it automatically, so activation is optional.

For first-time setup, install Windows x64 Python 3.14 with the `py` launcher. Open a PowerShell window, or reuse one that is already open. Paste the entire block below and press **Enter** if the final line is still at the prompt.

```powershell
Set-Location -LiteralPath 'G:\Code_Repositories\No-Mans-Sky-3D-Base-Aligner'
py -3.14 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Creating .venv failed.' }
```

**Keep this PowerShell window open for the dependency install below.**

Install the dependencies after creating `.venv`. If `.venv` already exists, start with the block below when `requirements-windows.txt` changes or the build reports missing dependencies. Use the PowerShell window you already opened, or open one if needed. Paste the entire block and press **Enter** if the final line is still at the prompt.

```powershell
Set-Location -LiteralPath 'G:\Code_Repositories\No-Mans-Sky-3D-Base-Aligner'
& .\.venv\Scripts\python.exe -m pip install -r .\requirements-windows.txt
if ($LASTEXITCODE -ne 0) { throw 'Installing Windows build dependencies failed.' }
```

**Keep this PowerShell window open for Step 2.B.**

If `.venv` points to a removed Python installation or the script reports the wrong architecture, move the existing `.venv` folder aside, then repeat setup using Windows x64 Python.

### B. Run the build script

Set `-Version` to the GitHub tag you intend to publish. The example uses `v1.0.0`. For another release, copy the entire block into a text editor and replace `v1.0.0` on the last line with that release’s tag. Use a stable version such as `v1.0.1`.

**The script replaces an existing ZIP with the same versioned filename.** Move the existing ZIP out of `dist` before building if you want to preserve it, including the original November 12 archive.

Reuse the PowerShell window from Step 2.A, or open a PowerShell window if you skipped setup. Paste the entire block, with the version you chose, and press **Enter** if the final line is still at the prompt. The execution policy applies only to this PowerShell session and expires when you close the window.

```powershell
Set-Location -LiteralPath 'G:\Code_Repositories\No-Mans-Sky-3D-Base-Aligner'
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\build-windows.ps1 -Version v1.0.0
```

**Keep this PowerShell window open for the checksum in Step 2.C.**

The script uses `.venv\Scripts\python.exe` by default, checks for `win-amd64`, and verifies the required imports. To specify the interpreter explicitly, add `-Python .\.venv\Scripts\python.exe` to the build command.

PyInstaller creates the portable folder at `dist\NMS-Base-Aligner`. The script checks for the EXE, HTML viewer, and Qt WebEngine helper, rejects an app-level `models` folder, removes a conflicting bundled `icuuc.dll` if present, and copies the license and user guides.

The `-Version` value sets both the EXE’s **File version** and **Product version** and the ZIP filename. For `-Version v1.0.0`, both EXE fields are `1.0.0`, and the script creates `dist\NMS-Base-Aligner-Windows-x64-Portable_v1.0.0.zip`. The script checks both EXE fields before packaging. If the build reports an error, fix it and rerun before using its output.

### C. Verify the release ZIP and EXE version

Confirm that `dist` contains the ZIP named for the version you passed in Step 2.B. In File Explorer, right-click `dist\NMS-Base-Aligner\NMS-Base-Aligner.exe`, choose **Properties → Details**, and check **File version** and **Product version**. Both should match the release version without the leading `v`.

Reuse the PowerShell window from Step 2.B. If you built a different version, replace `v1.0.0` in the path below with that version. Paste the entire block and press **Enter** if the command is still at the prompt. Record the SHA-256 with your test results.

```powershell
Get-FileHash -LiteralPath '.\dist\NMS-Base-Aligner-Windows-x64-Portable_v1.0.0.zip' -Algorithm SHA256
```

## 3. Test the ZIP you will upload

1. Extract the entire versioned ZIP to a fresh folder outside the repository. Open the extracted `NMS-Base-Aligner` folder and launch `NMS-Base-Aligner.exe` with `_internal` beside it.
2. On a Windows x64 machine or VM without the development Python environment, confirm the viewer starts without the optional models. Open a sample `.nmsbase` in single-base mode and try a manual edit. Then open a known Before/After pair and run the measured correction workflow.
3. Use **Save adjusted base** to export to a new file. Reopen the export and verify the expected adjustment. Repeat the launch and export while offline. For process-level network verification, monitor the EXE and its Qt WebEngine helper during launch, viewing, and export and check for unexpected connections.
4. Record the ZIP filename, SHA-256, source commit, and test results. If you rebuild, repeat the checks on the replacement ZIP.

## 4. Publish the GitHub Release

1. Open the repository’s **Releases** page and choose **Draft a new release**. Check for an existing `v1.0.0` tag or release before creating one.
2. Choose the `v1.0.0` tag if it already points to the tested commit. If you create it in the release form, choose `main` as **Target** only while its remote tip is the tested commit. If `main` has advanced, create and push `v1.0.0` on the recorded commit, then choose that existing tag. If the tag already points elsewhere, resolve the version before publishing.
3. Use **NMS 3D Base Aligner v1.0.0** as the title. Leave **This is a pre-release** unchecked. Select **Set as latest release** if this should be the primary stable download.
4. Add the changes and Windows x64 download instructions to the release notes. Tell users to download `NMS-Base-Aligner-Windows-x64-Portable_v1.0.0.zip` under **Assets**, extract the entire archive, and run `NMS-Base-Aligner.exe` with `_internal` beside it. Optional 3D models are separate. GitHub also provides **Source code (zip)** and **Source code (tar.gz)** from the tagged commit.
5. Upload the exact tested versioned ZIP to the draft. Confirm the tag, asset filename, and release notes, then select **Publish release**. Open the published page, download the asset, and compare its SHA-256 with the tested local file.

[Repository releases](https://github.com/ebaleytherogue/No-Mans-Sky-3D-Base-Aligner/releases) · [GitHub release instructions](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)

## Branches, tags, and releases

- `develop` is the development branch. A future test build can have its own version tag on the tested development commit and be marked as a GitHub pre-release.
- `main` is the stable source branch. A Git tag identifies a specific commit. The repository-level GitHub Release uses that tag and holds the release notes and uploaded ZIP.
- Merging `develop` into `main` integrates source changes. Existing tags still point to their original commits, and published pre-releases and their assets stay available. A stable release has its own tag and tested ZIP.
- Keep compiled archives under `dist` and upload them as release assets. This repository ignores `.venv`, `build`, `dist`, and this local guide.
- If a published package needs a correction, publish a new version with a new tag and tested ZIP. GitHub permits asset edits on mutable releases. With immutable releases, assets are locked on publication. [GitHub’s release editing rules](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository#editing-a-release)

