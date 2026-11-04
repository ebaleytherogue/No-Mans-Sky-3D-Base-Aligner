# Axes Explained

Coordinate reference for **No Man's Sky_Base Aligner_PRIVATE**, for use when updating the project's other Markdown documentation.

## Coordinate convention

Object positions use `[X, Y, Z]` order in the base's local coordinate system.

| Axis | Role | Informal description |
| --- | --- | --- |
| X | Horizontal position | Left/right along one horizontal axis |
| Y | Vertical position (height) | Up/down |
| Z | Horizontal position | Forward/backward along the other horizontal axis |

**X and Z form the horizontal XZ plane; Y is vertical.** Left/right and forward/backward are descriptive labels, not verified directions relative to the player or camera. Turning the camera does not redefine the saved axes.

## Positive and negative directions

Positive adjustments increase coordinate values; negative adjustments decrease them. For example, translating `[10, 20, 30]` by `[2, -3, 4]` produces `[12, 17, 34]`.

Physical positive directions cannot be established from axis names alone. Do not assume +X means the player's right, +Z means the player's forward, or that either matches a compass direction. Establish those mappings by inspecting code and coordinate references, then comparing controlled before/after exports with known in-game movements and viewpoints. The inspected files establish the axis roles and numeric operations, but do not establish a complete physical sign mapping. Y is height; verify its physical sign before documenting signed raise/lower instructions.

## Translation

Translation adds an offset to a position:

```text
new_position = old_position + [dx, dy, dz]
```

X and Z offsets move parts horizontally; a Y offset adjusts height. Translation alone does not rotate a part. Applying the same translation to construction parts preserves their relative spacing. Orientation vectors `Up` and `At` are directions, so they are not translated.

## Horizontal rotation and height in two-object transfer

In `nms_base_align.py`, `rotate(v, angle)` performs:

```text
rotated_x = x * cos(angle) - z * sin(angle)
rotated_y = y
rotated_z = x * sin(angle) + z * cos(angle)
```

This rotates within the horizontal XZ plane, about the vertical Y axis. It changes heading without introducing tilt. It is not rotation about Z.

`calculate_transform` determines the angle from the horizontal separation of two reference objects. The well-placed anchor has original position A and corrected position A'. The script calculates:

```text
shift = A' - rotate(A, angle)
new_position = rotate(old_position, angle) + shift
```

This is equivalent to rotating object offsets about the original anchor, then placing that anchor at its corrected position. Since rotation preserves Y, `shift_y = A'_y - A_y`. The anchor's measured height difference supplies the separate Y adjustment for the other transformed parts; horizontal rotation itself leaves their heights unchanged.

`make_result` rotates `Up` and `At` without translating them. It retains the corrected reference objects and corrected Base Computer rather than applying the general transform to them.

Numerically, a positive quarter-turn in this formula maps `[1, 0, 0]` to `[0, 0, 1]`. Calling that clockwise or counterclockwise requires specifying the viewing direction.

## Full 3D repair and browser adjustments

The horizontal-only rotation described above belongs to the legacy two-object transfer workflow. In `nms_base_align_3d.py`, `align` can apply full measured rotation about the original reference position, followed by selected translation components. Full rotation can introduce tilt and change Y as well as X and Z. Disabling Y translation does not prevent rotation from changing Y.

The browser labels rotation axes X (pitch), Y (yaw), and Z (roll). Movement along Y adjusts height; rotation about Y changes horizontal heading. Rotations about X or Z can introduce tilt and change height. Manual adjustments rotate positions about the selected pivot, rotate orientation vectors, then add translation. The Base Computer is excluded from construction adjustments.

Do not assume identical angle signs across workflows: the legacy `rotate` formula and browser `euler` Y-rotation formula use opposite signs for a pure Y rotation. Check the relevant implementation before documenting signed angle examples.

## Guidance for later Markdown updates

- Use **X/Z horizontal, Y vertical**, with positions ordered `[X, Y, Z]`.
- Distinguish translation along an axis from rotation about an axis.
- Describe two-object transfer as horizontal XZ rotation plus XYZ translation, including the separate Y height offset.
- Describe full 3D repair separately: its rotations can change height.
- Keep coordinate signs separate from player-relative, screen, and compass directions until verified; specify the viewpoint for clockwise/counterclockwise claims.
- Cite the workflow and function when adding formulas or signed examples.

## Sources inspected

- `nms_base_align.py`: `rotate`, `calculate_transform`, `make_result`.
- `nms_base_align_3d.py`: `align`.
- `nms_base_editor.html`: axis labels, `euler`, `result`.
- `NMS_Base_Aligner_Run_Guide.md`: local XZ-plane transfer geometry and separate height shift.
- `README.md`: workflow distinctions.

This reference describes the inspected implementation without claiming unverified physical sign directions. Existing Markdown files are reserved for a later documentation update.
