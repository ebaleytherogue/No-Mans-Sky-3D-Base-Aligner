# How to activate models in No Man’s Sky 3D Base Aligner

The browser editor loads optional part meshes when the 3D generator creates an HTML file. After installing a compatible pack, generate a fresh viewer and select **Display → Shapes**. The generated HTML embeds the meshes it loaded and works offline.

## Where to get models

- **Separate Aligner model ZIP.** If the Aligner maintainer supplies a compatible ZIP, use the installation steps below. A public download for the full Aligner model pack was not verified. [Aligner releases](https://github.com/ebaleytherogue/No-Mans-Sky-3D-Base-Aligner/releases)
- **Upstream Base Builder assets.** Download the source from DjMonkey’s repository. To reproduce the catalog’s input, use revision `68c4bc945320a8cfcc4a65bff5273da66f2a24a7` and look under `src/addons/no_mans_sky_base_builder/models/`. Upstream source paths are recorded in the full pack catalog, `base-builder-catalog.json`, and include GLB files. Base Builder’s own releases are another upstream download route. Those downloads require conversion before the Aligner can use their meshes. [Base Builder repository](https://github.com/djmonkeyuk/nms-base-builder) · [Base Builder releases](https://github.com/djmonkeyuk/nms-base-builder/releases)

**Redistribution rights are unverified for the converted catalog and its upstream meshes.** The converted pack includes a Base Builder MIT notice. Preserve that notice and verify that the specific assets and any third-party contributions are covered before publishing a pack or mirror. Availability of a download alone does not establish redistribution rights.

## Install an Aligner-compatible ZIP on Windows

1. In File Explorer, locate the folder containing `NMS-Base-Aligner.exe` and `_internal`. Keep them together.
2. Right-click the model ZIP and choose **Extract All**. If the archive contains a top-level `models` folder, extract it into the executable’s folder. If the archive opens directly to `manifest.json` and mesh folders, extract those into a `models` folder beside the executable. If Explorer creates a ZIP-named wrapper folder, move the resulting `models` folder out of it.
3. Verify that the manifest is directly at `models\manifest.json`. Keep all mesh folders in the locations named by the manifest. If switching packs, back up the old folder first so the manifest and mesh files come from the same pack.

A portable installation with the full catalog can look like this. A smaller pack may have fewer mesh folders.

```text
Portable Aligner/
  NMS-Base-Aligner.exe
  _internal/
  models/
    manifest.json
    meshes/
      F_FLOOR.json
      ...
    base-builder/
      ...
    base-builder-catalog.json
    Base Builder LICENSE.txt
```

## Python source and upstream conversion

Place the same `models` folder beside `nms_base_align_3d.py`. Keep `nms_base_align.py` and `nms_base_editor.html` there too. The generator resolves the model directory from the script location, or from the executable location in a portable build.

If starting from upstream assets, export or convert each desired part to a JSON mesh with `vertices` (an array of numeric XYZ triples in the part’s local coordinates) and `indices` (a flat array of zero-based triangle indices). Triangulate the geometry and bake any asset transforms needed to put it in the Aligner’s local axes and units. Compare a known part in the generated viewer to confirm orientation, scale, and origin. No upstream-to-Aligner converter was found with the Aligner source.

Save the mesh files under `models` and create a schema-1 manifest. Use the game object ID with its leading caret removed, and a relative JSON path under `models`. For example:

```json
{
  "schema": 1,
  "parts": {
    "F_FLOOR": "meshes/F_FLOOR.json"
  }
}
```

The Aligner limits each manifest or mesh file to 512,000 bytes and each mesh to 2,048 vertices and 6,144 indices. It also caps the total embedded geometry at 100,000 vertices and 300,000 indices. Parts are matched against IDs in the first base export.

## Verify activation

Use your own exported base with a part listed in the installed manifest. Replace the example path with the path to that export. Run one of these commands in PowerShell from the folder containing the executable or scripts. Choose a fresh output filename if `Model Check.html` already exists.

```powershell
.\NMS-Base-Aligner.exe "C:\path\to\Your Base.nmsbase" -o "Model Check.html"
```

```powershell
py -3 .\nms_base_align_3d.py "C:\path\to\Your Base.nmsbase" -o "Model Check.html"
```

Open the newly generated HTML and switch **Display** from **Points** to **Shapes**. A matching part should show its mesh. Parts without a usable mesh still appear as points.

If **Shapes** is disabled, the generator loaded no usable meshes for that export. Check for an extra ZIP wrapper or a nested `models\models` folder, a mismatched part ID, or an invalid mesh or manifest. Regenerate after fixing the pack. Opening an older preview can give misleading results because it keeps the meshes embedded when it was generated.
