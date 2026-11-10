param([string]$Python = "python")
$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
try {
    $name = "NMS-Base-Aligner"
    & $Python -m PyInstaller --noconfirm --onedir --windowed --name $name --specpath build --add-data "$PSScriptRoot/nms_base_editor.html;." aligner_desktop.py
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE."
    }
    $bundle = "dist/$name"
    foreach ($required in @("$name.exe", "_internal/nms_base_editor.html", "_internal/PySide6/QtWebEngineProcess.exe")) {
        if (!(Test-Path -LiteralPath "$bundle/$required" -PathType Leaf)) {
            throw "Bundle is missing $required."
        }
    }
    if (Test-Path -LiteralPath "$bundle/models") {
        throw "The portable bundle must exclude optional models."
    }
    # Qt imports Windows ICU. A collected third-party DLL of the same name shadows it.
    $collectedIcu = "$bundle/_internal/icuuc.dll"
    if (Test-Path -LiteralPath $collectedIcu -PathType Leaf) {
        Remove-Item -LiteralPath $collectedIcu
    }
    Copy-Item -LiteralPath LICENSE, README-Windows.md, How_to_activate_models.md -Destination $bundle
    Compress-Archive -LiteralPath $bundle -DestinationPath "dist/$name-Windows-x64-Portable.zip" -Force
} finally {
    Pop-Location
}
