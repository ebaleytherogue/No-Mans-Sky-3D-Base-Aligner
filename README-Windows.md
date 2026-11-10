# NMS 3D Base Aligner for Windows

Extract the portable ZIP and run `NMS-Base-Aligner.exe`. Keep the `_internal` folder beside it. Use the File menu to open one base for manual editing or both Before and After for measured correction. The viewer can also add After after opening a single base. Use **Save adjusted base** or the viewer's existing download button to choose a destination for the adjusted export.

For optional meshes, put a compatible `models` folder next to the EXE. See [How to activate models](How_to_activate_models.md).

## Build the prototype

From PowerShell with Windows x64 Python 3.14:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-windows.txt
.\build-windows.ps1 -Python .\.venv\Scripts\python.exe
```

The ZIP is written to `dist/NMS-Base-Aligner-Windows-x64-Portable.zip`. Dependency acquisition is a build step. The app loads the viewer from an embedded local origin and has no localhost server.

This prototype needs a clean-machine launch and export test and process-level network verification before release.
