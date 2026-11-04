# No-Mans-Sky-3D-Base-Aligner Run Guide

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

The app identifies the one changed non-wiring part, including an orientation-only change and a repeated part ID. It rejects changed base identity/location, added or deleted non-wiring parts, multiple meaningful non-wiring geometry changes, reference resizing, and changes to the Base Computer. Incidental electrical or miniportal wire movement does not become a calibration reference: original wire geometry and segment counts are used so wiring is not moved twice. Wire segments removed or rebuilt in After do not prevent calibration; original Before segments are retained, and After-only segments are omitted. Unrelated non-geometric object-property changes are retained from After; the browser reports these separately.

If `Preview.html` already exists, choose another output name or add `--overwrite`. Never use the template filename `nms_base_editor.html` as your generated output. Regenerate the page after updating the scripts/template; older generated pages contain their own earlier editor code.

The Windows helpers `generate_browser_Two_Files_REFERENCE.bat` and `generate_browser_Single_File_NO_REFERENCE.bat` contain example commands. Edit their input/output filenames for your exports before running them. The single-file helper uses `That_Base.nmsbase` as its placeholder.

To explicitly select a unique object type, add `--reference "^BUILDBEACON"` (use the exact ObjectID from your export). For repeated IDs, specify zero-based before:after indices, such as `--reference "13:17"`. Indices include the Base Computer in each Objects array. The exports can have different object ordering.

With a calibration pair, only the changed part is eligible: the app will not silently substitute an unchanged part for it. Continue with [browser controls and export](#browser-controls-and-export).

## Manual browser adjustment

For manual adjustment without in-game calibration, supply one export:

```text
py nms_base_align.py 3d "Before.nmsbase" -o "Preview.html"
```

Supplying the same export twice remains supported, but is unnecessary. Open Preview.html and choose a manual rotation pivot from the dropdown or click an eligible original point. Entries include object indices so repeated IDs can be distinguished. Electrical and miniportal wires and the Base Computer are excluded from pivot choices.

### Browser controls and export

The generated page is self-contained and works offline; no file is sent to a server.

**Add After file** loads a corrected export into the open page. The editor detects the calibration reference, retains current manual adjustments, and reports validation errors without discarding the current layout. This file input is local even though the interaction is sometimes called an upload. Loading After does not itself apply the measured correction.

For a valid calibration pair, **Align rest of base to corrected reference** applies the measured correction. The X/Y/Z checkboxes under **Apply measured movement** select translation components, and **Apply measured rotation** enables or disables the full measured rotation. Changing these options changes the next alignment application; click the alignment button again to apply the new options. Applying the same options again does not stack another copy of the correction. Manual adjustments are preserved.

The corrected reference itself retains its exact After geometry when it is in the moving scope, even when some measured components are disabled for the other pieces. A reference outside a selective selection remains in its original geometry. Calibration reference detection and the manual pivot are separate: choosing another pivot does not change which part supplied the measured correction.

Inspect original gray and proposed blue points, the green reference, orange fixed computer, and orientation arrows. In selective mode, selected pieces are yellow and unselected pieces are subdued. The viewer shows positions, not part meshes.

Drag in **Orbit camera** mode to look around; scroll to zoom or right-drag to pan. Top, Front, Side, and Fit control the camera only. Select **Rotate base on selected axis** or **Move base on selected axis**, choose X/Y/Z, then drag. Colored axis handles indicate the selected local axis. Numeric fields allow exact values. Manual rotation uses fixed local X, then Y, then Z axes about the manual pivot, followed by translation. Changing the pivot preserves the proposed layout instead of clearing adjustments.

**Undo** restores earlier edits, including scope, selection, and connection assignments. **Reset to original** removes measured and manual corrections while retaining the current selection and connection assignments. Latest After metadata is retained; Reset is a geometry reset, not a return to Before metadata.

**Download adjusted .nmsbase** creates `Adjusted Base.nmsbase` in the browser's download location. Base metadata and non-geometric object properties come from the latest export. The Base Computer is never transformed. Ordinary construction orientation vectors rotate without changing length. Selective wires can change length/direction to preserve their original socket attachments while existing free endpoints remain fixed.

Back up the save, close the game, and import the downloaded file into the same base with NMSE. Check placement, electrical power, and miniportal links in-game before saving. **Existing-base repair and manual editing do not require restoring a computer-only save.** Do not use the transfer workflow's restoration step for an existing-base repair.

### Selective Alignment

Leave **Enable Selective Alignment** unchecked to move the whole construction using the existing rules, with the Base Computer fixed. Enable it when only an affected area needs correction.

1. Check **Enable Selective Alignment**. The drag action switches to **Select pieces**.
2. Choose **Rectangle** or **Circle** and **Replace**, **Add**, or **Remove**. Draw around original object positions; the circle grows outward from the drag's starting point. A click picks the nearest eligible original point within the click tolerance.
3. Inspect the yellow selection and selected-piece count. Use Add/Remove and individual clicks to refine it, or **Clear selection** to start again. The Base Computer and wire objects are not directly selectable.
4. Check Top, Front, and Side views for overlapping objects. Shapes select through all depths; there is no depth/height filter. Membership stays attached to object indices when the camera or preview changes. Enable **Show original** to see the points used for selection.
5. Apply the measured correction and/or make manual adjustments. Only selected construction pieces move; unselected construction geometry stays fixed. A manual pivot may be outside the selection.
6. Inspect the connection summary and preview, review any ambiguous attachments as described below, then download. Supported socket attachments are automatic; existing free ends do not require a choice.

With selective mode enabled and no pieces selected, alignment application and export are disabled. Unchecking the checkbox restores whole-base scope while retaining the selection for later use. Scope and selection changes recompute the preview from the original geometry and current correction rather than accumulating extra movement.

### Electrical and miniportal connections

Selective mode handles standard electrical wires (`^U_POWERLINE`) and miniportal/short-range teleporter wires (`^U_PORTALLINE`). Selecting a device does not automatically select the rest of its network.

Open **Connection attachments** to inspect automatic attachment results. The editor matches endpoints against a bundled socket catalogue using the Before file's object positions, orientations, and scales. A unique compatible socket within 0.001 local game units identifies the original attachment. Electrical and miniportal sockets are matched separately.

An attached endpoint follows its original object's position and orientation when that object moves; otherwise it stays fixed. Endpoints attached to the same socket share one junction, including endpoints with small numeric differences. Nearby unattached endpoints of the same wire type also share a junction within the matching tolerance. Selecting a device does not select other devices in its network.

Existing free endpoints and unattached wire junctions stay at their original positions during selective alignment. They are preserved as existing geometry and do not block export. For example, a wire attached to a selected solar panel at one end and free at the other follows the panel at its attached end while the free end stays fixed. If the panel stays stationary, that wire remains unchanged. The status reports the number of existing free ends preserved.

| Segment endpoints | Result |
| --- | --- |
| Both attached objects move | Each endpoint follows its original object. |
| Neither endpoint moves | The segment stays unchanged. |
| Only one endpoint moves | That end follows its object; the other stays fixed, changing segment length and direction. |

The catalogue covers 214 part IDs; it is not a complete guarantee for every game part or version. For parts without catalogue entries, a unique exact object-origin match remains supported. Other unmatched endpoints are preserved as fixed geometry, so an unsupported device socket may be treated as unattached. Inspect affected connections carefully when using unsupported parts.

Multiple socket candidates remain ambiguous rather than being assigned arbitrarily. Only ambiguous junctions expose assignment controls. Choose the actual attached object if known; **Keep fixed** or **Move with selection** explicitly overrides endpoint movement, and **Resolve attachment** leaves the ambiguity unresolved. Do not assign a socket to an unrelated nearby object. Routine supported attachments and existing free ends require no manual assignment.

The preview draws crossing wires purple, unresolved wires red, and other resolved wires in a muted color. The status report counts internal, crossing, fixed, and unresolved segments. Unresolved ambiguous attachments or a moved segment collapsed to zero length block selective export. Existing free endpoints do not. The exporter preserves other wire properties while updating geometry.

In whole-base mode, wires follow the established whole-base transform, including free ends, preserving their shape. The fixed-free-end policy applies to selective alignment.

These checks establish geometry, not an in-game connectivity guarantee. Verify both power delivery and miniportal travel after import.

## Coordinates and axes

Positions use `[X, Y, Z]` in the base's local coordinate system:

| Axis | Position role | Browser rotation label |
| --- | --- | --- |
| X | Horizontal | Pitch |
| Y | Vertical / height | Yaw |
| Z | Horizontal | Roll |

**X and Z form the horizontal plane; Y is vertical.** Left/right and forward/backward are only informal descriptions. Saved axes are not redefined by turning the camera and are not established player-relative or compass directions.

Translation adds an offset:

```text
new_position = old_position + [dx, dy, dz]
[10, 20, 30] + [2, -3, 4] = [12, 17, 34]
```

X/Z translation moves horizontally; Y translation changes height. Translation does not rotate `Up` or `At`. Positive offsets increase coordinate values; negative offsets decrease them. Verify physical sign directions with controlled in-game tests rather than assuming +X means player-right or +Z means player-forward. The coordinate roles alone do not establish a complete physical sign mapping.

Rotation **about** an axis differs from movement **along** it. Browser Y rotation changes heading; X/Z rotations can introduce tilt and change height. Full measured rotation can change all three coordinates, so disabling Y translation does not freeze height when rotation is enabled.

The two-object transfer formula in `nms_base_align.py: rotate` rotates horizontally about Y, not Z. It leaves Y unchanged until the anchor's separate height offset is added. Its formula and browser `euler` use opposite signs for a pure Y rotation: a positive quarter-turn maps `[1,0,0]` to `[0,0,1]` in legacy transfer and to `[0,0,-1]` in browser manual rotation. Clockwise/counterclockwise descriptions require a specified viewpoint.

The calculation below explains the transfer's anchor, height offset, and orientation-vector treatment. The axes material from `Axes_Explained.md` is incorporated here and in the workflow explanations; that standalone reference is retained.

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

The viewer displays object positions and orientation arrows, not meshes or terrain. A single rigid correction cannot repair multiple areas requiring different movements. Use selective mode for one affected area at a time, and inspect seams and connections between moved and fixed pieces. Large builds can swing a long way around the reference; inspect the largest-movement summary and check the result in-game. Automated tests cover synthetic geometry and browser behavior; real exports and game behavior still need in-game validation.

One corrected position alone cannot determine rotation and translation uniquely. The 3D repair workflow works with one part because it also uses that part's orientation.

## Developer checks

```text
py -m unittest -v test_alignment_3d
node test_editor_logic.cjs
node test_editor.cjs
```

The browser smoke test uses a local Windows Chrome installation and Node 22+ with no npm dependencies. It creates synthetic fixtures and a temporary browser profile under the system temporary directory. It checks the real generated page, single-file generation, After-file loading, measured translation options, rotation, manual edits, undo/reset, download, rectangle/circle selection, camera-stable membership, and scope toggling. Set the `PYTHON` environment variable to the Python executable if `py` is unavailable.

The Node logic regressions cover selective scope, empty-selection/export guards, unselected geometry, electrical and teleporter endpoints, crossing connections under rotation, and unresolved attachments, alongside existing alignment behavior. Socket regressions also cover offset sockets on rotated/scaled objects, shared socket junctions with small coordinate differences, fixed free ends during translation and rotation, and preservation of unaffected wires. The Python suite covers generation, calibration, identity validation, and geometry. These synthetic tests do not replace in-game validation.
