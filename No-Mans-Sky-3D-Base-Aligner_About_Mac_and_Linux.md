# No-Mans-Sky-3D-Base-Aligner on macOS and Linux

**Compatibility is untested on macOS and Linux.** These instructions use the checked-in source. The Windows portable executable and build script are Windows-specific. The desktop source and offline browser workflow are described below. [Qt for Python installation](https://doc.qt.io/qtforpython-6/gettingstarted.html)

## Open a generated editor in a browser

If you already have a generated editor `.html` file, open it directly in a modern browser on Windows, macOS, or Linux. It works offline and requires no Python, Tkinter, or PySide6. To generate a fresh HTML editor, use the standard-library Python commands in the platform sections below.

The optional Aligner desktop app uses PySide6 and Qt WebEngine. Tkinter is used by the separate Base Reports desktop app.

## macOS · Terminal

Use an existing Python 3.10 or later (3.12 recommended) interpreter if available. Check it with `python3 --version`. Otherwise, with Homebrew installed, use:

```bash
brew install python@3.12
```

From Terminal, replace the example path with the path to your checkout. The block uses Homebrew Python. If using an existing installation, replace `"$(brew --prefix python@3.12)/bin/python3.12"` with its `python3` command or executable path.

```bash
cd "/path/to/No-Mans-Sky-3D-Base-Aligner"
"$(brew --prefix python@3.12)/bin/python3.12" -m venv .venv
source .venv/bin/activate
python --version
```

For the desktop editor, install the runtime version used by this project. It includes Qt WebEngine on supported systems. Open a single NMSE `.nmsbase` export for manual editing, or use the paired preview for before and after exports. PyInstaller is only for packaging.

```bash
python -m pip install "PySide6==6.10.2"
python aligner_desktop.py
```

If the desktop dependencies are unavailable, use the browser editor. The generator uses only the standard library. Keep `nms_base_align.py`, `nms_base_align_3d.py`, and `nms_base_editor.html` together. Optional meshes go in `models/` beside the scripts. Use a fresh HTML output name.

```bash
python nms_base_align_3d.py Before.nmsbase -o preview.html
open preview.html
```

For a paired preview, run `python nms_base_align_3d.py Before.nmsbase After.nmsbase -o paired-preview.html` and open the new HTML file. See the [run guide](NMS_Base_Aligner_Run_Guide.md) for the four-export alignment workflow and the [model guide](How_to_activate_models.md) for optional meshes.

## Linux · Bash

Use the command for your distribution if Python or its virtual environment support is missing. Check that `python3 --version` reports Python 3.10 or later (3.12 recommended).

```bash
# Ubuntu or Debian
sudo apt update
sudo apt install python3 python3-venv

# Fedora
sudo dnf install python3

# Arch Linux
sudo pacman -Syu python
```


```bash
cd "/path/to/No-Mans-Sky-3D-Base-Aligner"
python3 -m venv .venv
source .venv/bin/activate
python --version
```

The desktop editor needs a graphical session and a compatible PySide6 wheel for your Python, architecture, and Linux distribution. If Qt reports an XCB cursor library error, install `libxcb-cursor0` on Ubuntu/Debian or `xcb-util-cursor` on Fedora/Arch. If `xdg-open` is unavailable, open the HTML file from your browser.

For the desktop editor, install the runtime version used by this project. It includes Qt WebEngine on supported systems. Open a single NMSE `.nmsbase` export for manual editing, or use the paired preview for before and after exports. PyInstaller is only for packaging.

```bash
python -m pip install "PySide6==6.10.2"
python aligner_desktop.py
```

If the desktop dependencies are unavailable, use the browser editor. The generator uses only the standard library. Keep `nms_base_align.py`, `nms_base_align_3d.py`, and `nms_base_editor.html` together. Optional meshes go in `models/` beside the scripts. Use a fresh HTML output name.

```bash
python nms_base_align_3d.py Before.nmsbase -o preview.html
xdg-open preview.html
```

For a paired preview, run `python nms_base_align_3d.py Before.nmsbase After.nmsbase -o paired-preview.html` and open the new HTML file. See the [run guide](NMS_Base_Aligner_Run_Guide.md) for the four-export alignment workflow and the [model guide](How_to_activate_models.md) for optional meshes.

In a new terminal, return to the checkout and run `source .venv/bin/activate` before launching again.
