> **New: full 3D repair and interactive editing.** To adjust an existing base using one existing reference part, see [the 3D alignment guide](NMS_3D_Alignment_Guide.md). The two-object transfer instructions below remain available.

# NMS Base Aligner

Use nms_base_align.py with Python 3.9 or newer. It uses only Python's standard library and does not alter any input export or game save.

## Prepare four .nmsbase exports in Vector Commander's NMSE

Template: the base whose construction you want to copy.

Fresh target: your new destination base with only its Base Computer.

Initial target import: export the destination after you have imported the template construction for an initial, approximately positioned test. Do this before moving objects to correct alignment.

Corrected target: move exactly two identifiable, well-separated objects to their intended locations in-game, save, and export the destination again. Do not move the Base Computer or any other parts during this calibration.

The third export should be a destination-based import: retain the destination's base identity and ^BASE_FLAG, and copy the template's other objects. If you need a first approximation, shift all copied positions by target ^BASE_FLAG Position − template ^BASE_FLAG Position. The aligner does not create that preliminary import; it uses the third and fourth exports to measure and correct it.

## Run

Place the script and four exports in one folder. Open a terminal in that folder. On Windows, py commonly starts Python; substitute python if that is the command on your PC.

py nms_base_align.py "Template.nmsbase" "Fresh Target.nmsbase" "Initial Target Import.nmsbase" "Corrected Target.nmsbase" -o "Aligned Target.nmsbase"

If you’d rather, simply add the full command line above to a .bat file and execute it thatway.

If exactly two uniquely identifiable objects have moved, the script selects that pair automatically. Otherwise, it displays candidates and asks which two to use. In either case, it displays their exact JSON ObjectID names (including ^) and asks which is the well-placed anchor. Place that object especially carefully. The other moved object is the angle reference. You can specify unique object IDs explicitly:

py nms_base_align.py "Template.nmsbase" "Fresh Target.nmsbase" "Initial Target Import.nmsbase" "Corrected Target.nmsbase" -o "Aligned Target.nmsbase" --references "^BUILDBEACON,^POWERLINE_HIDER"

For repeated IDs, give zero-based object indices in the initial and corrected exports respectively, such as --references "13:14,15:16". Inspect the Objects arrays to identify those indices. -h displays the full command help.

For an unattended run, supply --anchor "^BUILDBEACON" (or --anchor 1 / --anchor 2 as numbered by the program). The anchor choice is required: an unattended run without it stops instead of guessing.

The calculation uses the pin-and-yarn method. Rotate the arrow from the old anchor to the old angle reference until it points in the direction from the corrected anchor to the corrected angle reference. Then shift the rotated build so the anchor lands exactly on its corrected position, including height. The angle reference determines direction, not the shift. It may miss its manually placed location if the two placements have slightly different spacing. The script reports that miss and stops if it exceeds 0.25 game units. The resulting file keeps the corrected positions and orientations of your two reference objects, transforms the other copied parts, and preserves the target Base Computer and current target base metadata. It also stops if the base identity or object counts do not match.

## Test the result

Back up the save. Restore the target's computer-only save used for the first import, close the game, import the new aligned file with NMSE, and then reload the game. Check both reference points and several other objects, including heights and connected wiring. Save in-game once satisfied. Each distinct destination needs its own two-object calibration; the angle from a previous destination is not a universal setting.
