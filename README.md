# No Man's Sky Base Aligner

Align and adjust No Man's Sky bases exported through Vector Commander's NMSE. Transfer construction between bases, repair a shifted or tilted base, or adjust placement manually in an offline browser editor.

## Choose a workflow

| Goal | Workflow | Inputs |
| --- | --- | --- |
| Copy construction to another owned base | [Two-object transfer](NMS_Base_Aligner_Run_Guide.md#transfer-between-bases) | Four exports; two repositioned reference objects |
| Repair an existing base's position and orientation | [Full 3D repair](NMS_Base_Aligner_Run_Guide.md#repair-an-existing-base) | Before/After exports; one existing part moved and rotated |
| Adjust a base manually in the browser | [Manual adjustment](NMS_Base_Aligner_Run_Guide.md#manual-browser-adjustment) | One export; optionally load an After export later |
| Repair only an affected area | [Selective Alignment](NMS_Base_Aligner_Run_Guide.md#selective-alignment) | Either browser workflow; select pieces and resolve wire attachments |

## Browser features

Whole-base alignment is the default; the Base Computer stays fixed. Measured X/Y/Z movement components and measured rotation can be enabled separately. Manual movement and rotation, a selectable pivot, Undo/Reset, camera presets, and downloadable exports support placement refinement.

Check **Enable Selective Alignment** to select pieces with a rectangle, circle, or individual clicks. Add/remove selection controls refine membership; camera changes preserve it. Electrical (`^U_POWERLINE`) and miniportal (`^U_PORTALLINE`) wires receive endpoint-aware handling in selective mode. Assign uncertain connection attachments before export. See the guide for the full procedure and limitations.

Coordinates use X/Z horizontally and Y vertically. Camera direction does not redefine those axes. The [coordinate explanation](NMS_Base_Aligner_Run_Guide.md#coordinates-and-axes) is included in the Run Guide.

## Requirements

Python 3.9 or newer and NMSE exports are required. No extra Python packages are needed. Keep `nms_base_align.py`, `nms_base_align_3d.py`, and `nms_base_editor.html` together for the 3D tools. The generated browser editor works offline.

The tools write new output files without modifying input exports or game saves. Generated HTML contains private base data. Regenerate the HTML after updating the editor template: previously generated pages do not acquire new features automatically.

Import the result through NMSE and verify placement and both wiring types in-game using a backed-up save. Automated geometry and browser tests do not establish in-game connectivity.

See the [Run Guide](NMS_Base_Aligner_Run_Guide.md) for preparation, commands, editor controls, alignment limits, and developer checks.
