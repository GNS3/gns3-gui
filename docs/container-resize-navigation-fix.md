# Container resize and hand navigation

## Report and investigation

Resizing near container corners could pan the canvas instead. The resize hit test
accepts a seven-pixel area around each corner in viewport coordinates, including
points outside the container shape. Hover used that test, but mouse press first
checked `itemAt()` to start hand navigation on empty canvas. In the outer part of
a handle, `itemAt()` returns no item, so panning consumed the event before resize
could start. In editing mode this also left the active container.

## Solution

In `GraphicsView.mousePressEvent`, attempt container resize before the empty-canvas
hand-navigation branch. Retain the existing left-button, drawing-tool, active-pan,
and Shift guards. Use the existing handle hit test, geometry update and release
persistence paths. The change fixes the existing corner handles; it does not add
new handles along the sides. Empty canvas outside the handles continues to pan.

## Validation

Added real Qt viewport gesture regressions for clicks five pixels outside all four
corners, for rectangles, ellipses and triangles at 50%, 100% and 200% zoom. Verify
that the point is outside `itemAt()` but inside the resize hit area, resizing wins
over hand navigation, editing remains active, dimensions change correctly, child
scene positions stay fixed and release saves the container once. A separate case
checks that blank-canvas hand navigation still starts and stops.

Before the fix, the outer-corner cases reproduced the failure to start resizing.
After the fix:

```
QT_QPA_PLATFORM=offscreen pytest -q tests/items/test_container_resize_navigation.py
37 passed

QT_QPA_PLATFORM=offscreen pytest -q tests/items
159 passed
```

Validation used automated Qt events with the offscreen platform; no interactive
desktop check was performed.
