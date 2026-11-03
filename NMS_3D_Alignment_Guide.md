# Full 3D alignment and browser editor

Use this mode to repair an existing base that has shifted or tilted. The original four-export, two-object transfer mode is still available.

## Prepare two exports

1. Back up your game save and export the affected base through NMSE as `Before.nmsbase`.
2. Return to the game. Choose an existing, visibly directional building part whose intended placement you know. A Save Beacon or a regular floor panel can work; a beacon is not required.
3. Move and rotate that same part into the desired position and orientation. Do not delete, replace, resize, recolor, or otherwise edit it. Leave all other parts, including the Base Computer, unchanged.
4. Save, exit, and export the same base as `After.nmsbase`. Uploading the base is not required.

The part must have usable, perpendicular Up/At vectors and unchanged scale. Wiring and other special parts may not qualify. A part's intended facing direction matters: level ground alone does not establish yaw. The app can validate the numbers but cannot establish that a visually symmetric part is facing the direction you intended.

## Generate the editor

Keep `nms_base_align.py`, `nms_base_align_3d.py`, and `nms_base_editor.html` together. Python 3.9 or newer is required; no extra packages are needed.

```text
py nms_base_align.py 3d "Before.nmsbase" "After.nmsbase" -o "Preview.html"
```

The app identifies the one changed part, including an orientation-only change and a repeated part ID. It rejects changed ownership/location, added or deleted parts, changes to other objects, and changes to the Base Computer. Matching unchanged objects is deliberately strict: even unrelated per-object data changes require a fresh calibration.

To explicitly select a unique object type, add `--reference "^BUILDBEACON"` (use the exact ObjectID from your export). For repeated IDs, specify zero-based before:after indices, such as `--reference "13:17"`. Indices include the Base Computer in each Objects array. The exports can have different object ordering.

For manual adjustment without an in-game calibration, supply the same export twice. Choose a reference from the dropdown or click its gray point. Exact duplicate objects with identical data require explicit index selection. The reference becomes the rotation pivot. With a calibration pair, only the changed part is eligible: the app will not silently substitute an unchanged part for it.

## Adjust and export

Open `Preview.html` in a browser. It is self-contained and works offline; nothing is uploaded. Select **Apply reference correction** to apply the measured full 3D correction. Inspect the original gray and proposed blue points, green reference, orange computer, and reference orientation arrows.

Drag in **Orbit camera** mode to look around; scroll to zoom or right-drag to pan. Top, Front, Side, and Fit buttons control the camera only. Select **Rotate base** or **Move base**, choose X/Y/Z, then drag to adjust the construction. Colored axis handles indicate the selected local axis; numeric fields allow exact values. Manual rotation uses fixed local X, then Y, then Z axes about the reference pivot; movement uses local game coordinates. The reference moves with manual adjustments. Undo restores previous edits; Reset restores the original construction. Selecting a different reference clears the current adjustment.

**Download adjusted .nmsbase** creates `Adjusted Base.nmsbase` in your browser's download location. Base metadata comes from the latest export; the Base Computer is never transformed. Positions and orientation vectors are rotated together without changing vector lengths, preserving scale. Other object fields are retained.

Back up the save, close the game, and use NMSE to import the downloaded file into the same base. Check the result in-game before saving. This repair workflow does not require a computer-only save. Do not use the legacy transfer workflow's restoration step for an existing-base repair.

## Limits and privacy

The viewer displays object positions and orientation arrows, not meshes or terrain. A rigid correction cannot repair uneven terrain changes. Large builds can swing a long way around the reference; inspect the largest-movement summary and check the result in-game. Automated tests cover synthetic geometry and browser behavior; real exports and game behavior still need in-game validation.

Generated preview HTML and downloaded exports include the base's ownership identifiers and other export data. Keep them private. Do not commit them to a public repository.

## Developer checks

```text
py -m unittest -v test_alignment_3d
node test_editor.cjs
```

The browser smoke test uses a local Windows Chrome installation and Node 22+ with no npm dependencies. It creates synthetic fixtures and a temporary browser profile under the system temporary directory. It checks the real generated page, correction, manual edits, undo, reset, and download.
