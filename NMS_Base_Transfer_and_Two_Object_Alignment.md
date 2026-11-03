> **New: full 3D repair and interactive editing.** To adjust an existing base using one existing reference part, see [the 3D alignment guide](NMS_3D_Alignment_Guide.md). The two-object transfer instructions below remain available.

# Transferring and aligning an NMS base with Vector Commander's NMSE

This procedure copies a build from one owned base to another owned base, replacing the destination's construction while preserving the destination's base identity and location. It uses two objects placed at corresponding reference points to measure any remaining rotation and shift. A fixed feature, like a portal pillar, can help, but the procedure also works where no portal is involved.

Math used here: This method and the accompanying nms_base_align.py script use a 2D rigid transformation in the base's local X–Z plane: one rotation and one translation, plus a height shift. They do not use the Gram–Schmidt process mentioned in NMSE's base-movement release notes. Gram–Schmidt builds an orthogonal coordinate frame from direction vectors; our two manually corrected objects give us the rotation and translation directly. We use the pin-and-yarn version of this calculation: one well-placed object anchors the build exactly, while the other sets the angle.

## Prepare the two bases

In the game, make a fresh save backup. Keep it until the finished import has been checked in-game.

Export the source base from NMSE as .nmsbase.

Claim a destination base where the copy should go. Put its Base Computer near a useful matching point, if there is one. Initially build nothing else there. Save, exit the game, and export this computer-only destination base from NMSE. Preserve this export: it is the template for every import file in this procedure.

Do not assume that a visible Base Computer marks the base's coordinate origin. A computer can have been moved after the base was claimed. The base record's Position/Forward and the ^BASE_FLAG object's local Position/Up/At are separate data.

## Make the first import

Create a new .nmsbase from the destination export. Keep all its base-level fields and its ^BASE_FLAG object. Replace its other construction objects with copies of the source's non-^BASE_FLAG objects. Do not import the source record wholesale: that would also carry its address, ownership-related fields, and other identity data.

For an initial placement, shift each copied object's local Position by destination ^BASE_FLAG Position − source ^BASE_FLAG Position. Leave its Up and At unchanged. This aligns the computer positions approximately, but it does not guarantee that the structures or landmarks align. Save this as a separate experimental import file.

With the game closed and its save backed up, import that prepared file into the destination using NMSE. Reload the game and inspect the result. Treat this as a calibration pass, not the final build.

## Measure alignment with two objects

Choose two recognizable copied objects that can be positioned against corresponding reference points at the destination. They should be separated by several game units. For example, one may belong beside a pillar and another on a nearby pad. Avoid two objects almost on top of each other; tiny placement errors would produce a large angle error.

In-game, move only those two objects to their intended locations. Put the anchor as accurately as possible; the angle reference can be approximate if necessary. Do not move the Base Computer or the remaining objects. Save, close the game, and export the destination again from NMSE. The first-import export contains their old positions and this calibration export contains their corrected positions, both in the same destination coordinate system.

Compare the two selected objects in the first import file and the calibration export. Check their ObjectID and, if IDs repeat, identify the intended instance by its position. Compare their separation before and after. A modest difference indicates placement imprecision; a large difference suggests a mistaken match or a change in scale or layout that a rigid transform cannot fix.

## Calculate the correction

Work in the destination base's local X–Z plane. Let the well-placed anchor have old position A and corrected position A′; let the angle reference have old position B and corrected position B′. Each position also has a Y height. After finding the two moved objects, the script displays their exact ^ObjectID names and prompts the user to choose the anchor; it labels the other as the angle reference. For an unattended run, the user must pass --anchor.

Draw an arrow from A to B and another from A′ to B′. In coordinates, the arrows are u = (Bx − Ax, Bz − Az) and v = (B′x − A′x, B′z − A′z). The script finds their signed angle with atan2(ux·vz − uz·vx, ux·vx + uz·vz). In plain language: compare the arrows' directions to learn how far to turn the build.

Rotate the old anchor A by that angle. The shift is A′ − rotate(A). This makes the calculated location of the anchor exactly equal to its manually corrected location. Think of the anchor as a pin and the arrow toward the second object as a piece of yarn determining direction.

The rotation leaves Y unchanged. The height component of the shift is therefore the anchor's measured Y change. The script applies it to the other objects along with the X–Z shift.

For each other copied object, rotate its Position around the base's local origin, then add the calculated shift. Rotate its Up and At vectors by the same angle but without a shift. These vectors describe orientation and can also carry scale or wiring length; do not normalize them.

Check the fit. If the reference objects' original separation differs from their corrected separation, a single rigid transformation cannot put both calculated positions exactly on their manually placed positions. The anchor's calculated fit error is zero by construction. The script reports how far the calculated second reference misses its corrected location and rejects an error above 0.25 game units. It keeps both manually corrected objects' own exact exported positions and orientations. A badly positioned angle reference can still imply a wrong rotation even when its reported fit error is small, so inspect the finished build in-game.

Keep the destination's ^BASE_FLAG unchanged and retain the destination's latest base-level fields. Preserve all unrelated object fields, such as IDs and user data.

In compact notation, shift = A′ − rotate_XZ(A, angle). For any other position p: new_p = rotate_XZ(p, angle) + shift. For its Up or At vector w: new_w = rotate_XZ(w, angle). The X–Z rotation is new_x = x·cos(angle) − z·sin(angle) and new_z = x·sin(angle) + z·cos(angle); Y stays as it was until the position-only height shift is added. One corrected object alone cannot uniquely determine both rotation and translation.

## Finish and verify

Save the resulting destination-based record as a new final-test .nmsbase. Check that it contains exactly one ^BASE_FLAG, the expected number of objects, and the destination's base-level identity and location. Check that the two reference objects exactly match their corrected locations.

Restore the computer-only pre-import game save for a clean test; close the game before editing. Import the final-test file into that destination with NMSE, reload, and inspect the build. Compare the reference objects and several uncorrected objects against the source layout. Also check heights, orientation, and connected parts such as wiring.

If satisfactory, save in-game and retain the original save and exports as backups. If the result is off, use the observed error to refine the calibration; do not stack imports or manual edits on an unknown save state.

## What this establishes

The two-object measurement yields an alignment for this source–destination pair. The rotation is not a universal value for other bases or locations. The method assumes the copied construction is one rigid assembly and the two reference locations correspond to the same intended points. Differences in terrain or building geometry may still require individual adjustments. A moved source Base Computer does not prevent the method: the first pass is approximate, and the two in-game reference placements provide the measured correction.
