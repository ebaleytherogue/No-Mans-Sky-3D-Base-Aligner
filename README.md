# No-Mans-Sky-3D-Base-Aligner

See walkthrough video at https://youtu.be/1q_TYTSEzFk 

Align and adjust No Man's Sky bases exported through Vector Commander's NMSE. Transfer construction between bases, repair a shifted or tilted base, or adjust placement manually in an offline browser editor.

## Choose a workflow

| Goal | Workflow | Inputs |
| --- | --- | --- |
| Copy construction to another owned base | [Two-object transfer](NMS_Base_Aligner_Run_Guide.md#transfer-between-bases) | Four exports; two repositioned reference objects |
| Repair an existing base's position and orientation | [Full 3D repair](NMS_Base_Aligner_Run_Guide.md#repair-an-existing-base) | Before/After exports; one existing part moved and rotated |
| Adjust a base manually in the browser | [Manual adjustment](NMS_Base_Aligner_Run_Guide.md#manual-browser-adjustment) | One export; optionally load an After export later |
| Repair only an affected area | [Selective Alignment](NMS_Base_Aligner_Run_Guide.md#selective-alignment) | Either browser workflow; select pieces; supported connections follow automatically |

## Browser features

Whole-base alignment is the default; the Base Computer stays fixed. In single-file mode, enter movement and rotation values, then click **Apply Measured Movement** to commit the preview. A selection limits the move to those pieces. With no pieces selected, the move applies to the whole base. In two-file mode, the measured X/Y/Z translation and rotation options control the correction calculated from the two exports. The editor includes a selectable pivot, Undo, Redo, Reset, camera presets, and downloadable exports.

Check **Enable Selective Alignment** to select pieces with a rectangle, circle, or individual clicks. Add/remove selection controls refine membership; camera changes preserve it. Electrical wires (`^U_POWERLINE`), short-range teleporter cables (`^U_PORTALLINE`), and supply pipes (`^U_PIPELINE`) are excluded from selection. Matched endpoints follow their sockets when attached objects move. Free ends and unattached junctions stay fixed during selective movement. If a single-file move affects an unresolved connection, **Cancel** leaves the move unapplied and **Move anyway** applies it while preserving the unresolved record.

Coordinates use X/Z horizontally and Y vertically. Camera direction does not redefine those axes. The [coordinate explanation](NMS_Base_Aligner_Run_Guide.md#coordinates-and-axes) is included in the Run Guide.

## Requirements

Python 3.9 or newer and NMSE exports are required. No extra Python packages are needed. Keep `nms_base_align.py`, `nms_base_align_3d.py`, and `nms_base_editor.html` together for the 3D tools. The generated browser editor works offline.

The tools write new output files without modifying input exports or game saves. Generated HTML contains private base data. Regenerate the HTML after updating the editor template: previously generated pages do not acquire new features automatically.

Import the result through NMSE and verify placement, electrical power, short-range teleporter links, and supply flow in-game using a backed-up save. Automated geometry and browser tests do not establish in-game connectivity.

See the [Run Guide](NMS_Base_Aligner_Run_Guide.md) for preparation, commands, editor controls, alignment limits, and developer checks.
