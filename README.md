# No Man's Sky Base Aligner

Align and adjust No Man's Sky bases exported through Vector Commander's NMSE. Transfer construction between bases, repair a shifted or tilted base, or adjust placement manually in an offline browser viewer.

## Choose a workflow

| Goal | Workflow | Inputs |
| --- | --- | --- |
| Copy construction to another owned base | [Two-object transfer](NMS_Base_Aligner_Run_Guide.md#transfer-between-bases) | Four exports; two repositioned reference objects |
| Repair an existing base's position and orientation | [Full 3D repair](NMS_Base_Aligner_Run_Guide.md#repair-an-existing-base) | Before/after exports; one part moved and rotated |
| Adjust a base manually in the browser | [Manual adjustment](NMS_Base_Aligner_Run_Guide.md#manual-browser-adjustment) | The same export supplied twice |

## Requirements

Python 3.9 or newer and NMSE exports are required. No extra Python packages are needed. Keep `nms_base_align.py`, `nms_base_align_3d.py`, and `nms_base_editor.html` together for the 3D tools. The generated browser editor works offline.

The tools write new output files without modifying input exports or game saves. Import the result through NMSE and verify it in-game.

See the [Run Guide](NMS_Base_Aligner_Run_Guide.md) for preparation, commands, editor controls, alignment limits, and developer checks.
