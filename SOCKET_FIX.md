# Automatic connection preservation

Replace the three application files together, then regenerate your editor HTML.
Existing generated HTML pages do not update automatically.

Selective alignment now matches Before wire endpoints to socket locations, accounting
for object rotation and scale. Endpoints at the same socket share one junction.
Attached endpoints follow their original object. Existing free endpoints and
unattached wire junctions remain fixed; they do not block export. Whole-base
alignment continues to transform the entire wire.

The tolerance is 0.001 local game units. Multiple socket candidates still require
review rather than an arbitrary assignment. The embedded catalogue covers 214
part IDs from NMS Base Builder; unknown/unsupported sockets cannot be guaranteed
to resolve. Existing unmatched endpoints are preserved as fixed geometry.

Validation: 13 Python tests, JavaScript regression and socket tests, and local
analysis of the supplied Before file (26 wires, 51 socket endpoints, one free end).
Connectivity has not been verified in-game.

Socket data source: https://github.com/djmonkeyuk/nms-base-builder
MIT copyright and permission notice are embedded in the HTML template so they
remain present in generated offline editors.

