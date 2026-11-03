# NMS Base Aligner Run Guide

## Requirements and shared precautions

Use Python 3.9 or newer and Vector Commander's NMSE .nmsbase exports. No extra Python packages are needed. For 3D repair and browser editing, keep nms_base_align.py, nms_base_align_3d.py, and nms_base_editor.html together.

Run commands from the folder containing the scripts and exports, or supply full paths. On Windows, py commonly starts Python; substitute python if that is your command. Commands can also be saved in a .bat file. Use -h for help.

Back up your game save before starting. Retain original exports and the save until the result has been checked in-game. Close the game before importing with NMSE. The tools create new output files without modifying input exports or game saves.

Exports, generated HTML, and downloaded exports contain ownership identifiers and other base data. Keep them private and do not commit them to a public repository. The browser editor works offline; nothing is uploaded.

## Transfer between bases

Copy construction from one owned base to another while preserving the destination's identity and location. This mode corrects rotation in the local X-Z plane and translation, including height. Use 3D repair for an existing base that needs tilt correction.

### Prepare the source and destination

Export the source base from NMSE as .nmsbase.

Claim a destination base where the copy should go. Put its Base Computer near a useful matching point, if there is one. Initially build nothing else there. Save, exit the game, and export this computer-only destination base from NMSE. Preserve this export: it is the template for every import file in this procedure.

Do not assume that a visible Base Computer marks the base's coordinate origin. A computer can have been moved after the base was claimed. The base record's Position/Forward and the ^BASE_FLAG object's local Position/Up/At are separate data.

### Make the first import

**The aligner does not create this preliminary import; prepare it separately.** Create a new .nmsbase from the destination export. Keep all its base-level fields and its ^BASE_FLAG object. Replace its other construction objects with copies of the source's non-^BASE_FLAG objects. Do not import the source record wholesale: that would also carry its address, ownership-related fields, and other identity data.

For an initial placement, shift each copied object's local Position by destination ^BASE_FLAG Position − source ^BASE_FLAG Position. Leave its Up and At unchanged. This aligns the computer positions approximately, but it does not guarantee that the structures or landmarks align. Save this as a separate experimental import file.

With the game closed and its save backed up, import that prepared file into the destination using NMSE. Reload the game and inspect the result. Treat this as a calibration pass. Save, exit, and export the destination as Initial Target Import.nmsbase before moving the two reference objects.

### Measure alignment with two objects

Choose two recognizable copied objects that can be positioned against corresponding reference points at the destination. They should be separated by several game units. For example, one may belong beside a pillar and another on a nearby pad. Avoid two objects almost on top of each other; tiny placement errors would produce a large angle error.

In-game, move only those two objects to their intended locations. Put the anchor as accurately as possible; the angle reference can be approximate if necessary. Do not move the Base Computer or the remaining objects. Save, close the game, and export the destination again from NMSE. The first-import export contains their old positions and this calibration export contains their corrected positions, both in the same destination coordinate system.

Compare the two selected objects in the first import file and the calibration export. Check their ObjectID and, if IDs repeat, identify the intended instance by its position. Compare their separation before and after. A modest difference indicates placement imprecision; a large difference suggests a mistaken match or a change in scale or layout that a rigid transform cannot fix.

The four command inputs correspond to these exports, in order:

| Command filename | Export |
| --- | --- |
| Template.nmsbase | Source construction |
| Fresh Target.nmsbase | Computer-only destination |
| Initial Target Import.nmsbase | Destination exported after the preliminary import, before moving references |
| Corrected Target.nmsbase | Destination exported after moving the two references |

### Run the transfer correction

```text
py nms_base_align.py "Template.nmsbase" "Fresh Target.nmsbase" "Initial Target Import.nmsbase" "Corrected Target.nmsbase" -o "Aligned Target.nmsbase"
```

If exactly two uniquely identifiable objects have moved, the script selects that pair automatically. Otherwise, it displays candidates and asks which two to use. In either case, it displays their exact JSON ObjectID names (including ^) and asks which is the well-placed anchor. Place that object especially carefully. The other moved object is the angle reference. You can specify unique object IDs explicitly:

```text
py nms_base_align.py "Template.nmsbase" "Fresh Target.nmsbase" "Initial Target Import.nmsbase" "Corrected Target.nmsbase" -o "Aligned Target.nmsbase" --references "^BUILDBEACON,^POWERLINE_HIDER"
```

For repeated IDs, give zero-based object indices in the initial and corrected exports respectively, such as --references "13:14,15:16". Inspect the Objects arrays to identify those indices. -h displays the full command help.

For an unattended run, supply --anchor "^BUILDBEACON" (or --anchor 1 / --anchor 2 as numbered by the program). The anchor choice is required: an unattended run without it stops instead of guessing. Ensure the pair is unambiguous or supply --references as well.

The script stops if base identity or object counts do not match. It reports the angle reference's calculated fit error and rejects errors above 0.25 game units. The output preserves both manually corrected references exactly, transforms the other copied parts, and retains the destination Base Computer and latest destination metadata.

### Import and verify the transfer

Use the generated Aligned Target.nmsbase as the final-test file. Check that it contains exactly one ^BASE_FLAG, the expected number of objects, and the destination's base-level identity and location. Check that the two reference objects exactly match their corrected locations.

Restore the computer-only pre-import game save for a clean test; close the game before editing. Import the final-test file into that destination with NMSE, reload, and inspect the build. Compare the reference objects and several uncorrected objects against the source layout. Also check heights, orientation, and connected parts such as wiring.

If satisfactory, save in-game and retain the original save and exports as backups. If the result is off, use the observed error to refine the calibration; do not stack imports or manual edits on an unknown save state.

## Repair an existing base

Use this workflow to repair a shifted or tilted base using one existing part's position and orientation.

### Prepare two exports

1. Back up your game save and export the affected base through NMSE as `Before.nmsbase`.
2. Return to the game. Choose an existing, visibly directional building part whose intended placement you know. A Save Beacon or a regular floor panel can work; a beacon is not required.
3. Move and rotate that same part into the desired position and orientation. Do not delete, replace, resize, recolor, or otherwise edit it. Leave all other parts, including the Base Computer, unchanged.
4. Save, exit, and export the same base as `After.nmsbase`. Uploading the base is not required.

The part must have usable, perpendicular Up/At vectors and unchanged scale. Wiring and other special parts may not qualify. A part's intended facing direction matters: level ground alone does not establish yaw. The app can validate the numbers but cannot establish that a visually symmetric part is facing the direction you intended.

### Generate the editor

```text
py nms_base_align.py 3d "Before.nmsbase" "After.nmsbase" -o "Preview.html"
```

The app identifies the one changed part, including an orientation-only change and a repeated part ID. It rejects changed ownership/location, added or deleted parts, changes to other objects, and changes to the Base Computer. Matching unchanged objects is deliberately strict: even unrelated per-object data changes require a fresh calibration.

To explicitly select a unique object type, add `--reference "^BUILDBEACON"` (use the exact ObjectID from your export). For repeated IDs, specify zero-based before:after indices, such as `--reference "13:17"`. Indices include the Base Computer in each Objects array. The exports can have different object ordering.

With a calibration pair, only the changed part is eligible: the app will not silently substitute an unchanged part for it. Continue with [browser controls and export](#browser-controls-and-export).

## Manual browser adjustment

For manual adjustment without in-game calibration, supply the same export twice:

```text
py nms_base_align.py 3d "Before.nmsbase" "Before.nmsbase" -o "Preview.html"
```

Open Preview.html. Choose a reference from the dropdown or click its gray point. Exact duplicate objects with identical data require explicit index selection using --reference, as described above. The reference becomes the rotation pivot. Use the browser controls below for both manual editing and calibrated repair.

### Browser controls and export

Open `Preview.html` in a browser. It is self-contained and works offline; nothing is uploaded. For a calibrated before/after pair, select **Apply reference correction** to apply the measured full 3D correction. Inspect the original gray and proposed blue points, green reference, orange computer, and reference orientation arrows.

Drag in **Orbit camera** mode to look around; scroll to zoom or right-drag to pan. Top, Front, Side, and Fit buttons control the camera only. Select **Rotate base** or **Move base**, choose X/Y/Z, then drag to adjust the construction. Colored axis handles indicate the selected local axis; numeric fields allow exact values. Manual rotation uses fixed local X, then Y, then Z axes about the reference pivot; movement uses local game coordinates. The reference moves with manual adjustments. Undo restores previous edits; Reset restores the original construction. Selecting a different reference clears the current adjustment.

**Download adjusted .nmsbase** creates `Adjusted Base.nmsbase` in your browser's download location. Base metadata comes from the latest export; the Base Computer is never transformed. Positions and orientation vectors are rotated together without changing vector lengths, preserving scale. Other object fields are retained.

Back up the save, close the game, and use NMSE to import the downloaded file into the same base. Check the result in-game before saving. **Existing-base repair and manual editing do not require restoring a computer-only save.** Do not use the legacy transfer workflow's restoration step for an existing-base repair.

## How alignment works and its limits

### Two-object pin-and-yarn calculation

The transfer calculation uses a 2D rigid transform, not the Gram-Schmidt process mentioned in NMSE's base-movement release notes. Gram-Schmidt builds an orthogonal frame from direction vectors; two corrected positions give this method its rotation and translation directly.

Work in the destination base's local X–Z plane. Let the well-placed anchor have old position A and corrected position A′; let the angle reference have old position B and corrected position B′. Each position also has a Y height.

Draw an arrow from A to B and another from A′ to B′. In coordinates, the arrows are u = (Bx − Ax, Bz − Az) and v = (B′x − A′x, B′z − A′z). The script finds their signed angle with atan2(ux·vz − uz·vx, ux·vx + uz·vz). In plain language: compare the arrows' directions to learn how far to turn the build.

Rotate the old anchor A by that angle. The shift is A′ − rotate(A). This makes the calculated location of the anchor exactly equal to its manually corrected location. Think of the anchor as a pin and the arrow toward the second object as a piece of yarn determining direction.

The rotation leaves Y unchanged. The height component of the shift is therefore the anchor's measured Y change. The script applies it to the other objects along with the X–Z shift.

For each other copied object, rotate its Position around the base's local origin, then add the calculated shift. Rotate its Up and At vectors by the same angle but without a shift. These vectors describe orientation and can also carry scale or wiring length; do not normalize them.

Check the fit. If the reference objects' original separation differs from their corrected separation, a single rigid transformation cannot put both calculated positions exactly on their manually placed positions. The anchor's calculated fit error is zero by construction. The script reports how far the calculated second reference misses its corrected location and rejects an error above 0.25 game units. It keeps both manually corrected objects' own exact exported positions and orientations. A badly positioned angle reference can still imply a wrong rotation even when its reported fit error is small, so inspect the finished build in-game.

Keep the destination's ^BASE_FLAG unchanged and retain the destination's latest base-level fields. Preserve all unrelated object fields, such as IDs and user data.

In compact notation, shift = A′ − rotate_XZ(A, angle). For any other position p: new_p = rotate_XZ(p, angle) + shift. For its Up or At vector w: new_w = rotate_XZ(w, angle). The X–Z rotation is new_x = x·cos(angle) − z·sin(angle) and new_z = x·sin(angle) + z·cos(angle); Y stays as it was until the position-only height shift is added. One corrected object alone cannot uniquely determine both rotation and translation.

### Transfer limits

The two-object measurement yields an alignment for this source–destination pair. The rotation is not a universal value for other bases or locations. The method assumes the copied construction is one rigid assembly and the two reference locations correspond to the same intended points. Differences in terrain or building geometry may still require individual adjustments. A moved source Base Computer does not prevent the method: the first pass is approximate, and the two in-game reference placements provide the measured correction.

### Browser and 3D limits

The viewer displays object positions and orientation arrows, not meshes or terrain. A rigid correction cannot repair uneven terrain changes. Large builds can swing a long way around the reference; inspect the largest-movement summary and check the result in-game. Automated tests cover synthetic geometry and browser behavior; real exports and game behavior still need in-game validation.

One corrected position alone cannot determine rotation and translation uniquely. The 3D repair workflow works with one part because it also uses that part's orientation.

## Developer checks

```text
py -m unittest -v test_alignment_3d
node test_editor.cjs
```

The browser smoke test uses a local Windows Chrome installation and Node 22+ with no npm dependencies. It creates synthetic fixtures and a temporary browser profile under the system temporary directory. It checks the real generated page, correction, manual edits, undo, reset, and download.
