# Two-point visual lines

Implemented on 2026-10-19 for the **Drawn line** toolbar action.
Target repository: https://github.com/redlintles/gns3-gui-fork.

## Workflow

1. Activate Drawn line and click an empty area to mark the first endpoint.
   Blank space inside the actively edited container also accepts this click.
2. Move the pointer to preview a dashed ghost line with a visible first-point
   marker. The preview follows the pointer without holding a mouse button.
3. Click a distinct second point, including over another element, to set the
   second endpoint. A second click delivered by Qt as a double-click also works.
4. The Line properties dialog offers solid, dashed, dotted, dash-dot and
   dash-dot-dot strokes, thickness from 1 to 1,000 and color/opacity. Thickness
   uses an explicitly white background with black text, including its editor.
5. Apply previews the style locally and leaves the dialog open. OK confirms and
   saves; Cancel (or closing the dialog) discards a new drawing or restores the
   original pens of existing lines. Apply never sends a preview to the server.

Escape, right click, deactivating Drawn line, choosing another authoring or
navigation tool, project reset and focus loss cancel an unfinished ghost. A
second click at the exact first point leaves the draft active rather than
creating a zero-length drawing.

After creation, drag the line body to move it or select it and drag either
endpoint handle to resize. Reopen Line properties using the Style action on a
line-only selection or by double-clicking a line. Mixed shape/line selections
continue to use the existing shared style editor.

New lines start at the scene root, as existing shape drafts do. Grouping them
into a container remains an explicit operation. Creating a line over a blank
editing-container background does not exit that container.

## Investigation and implementation

The former view handler created a horizontal 200-unit line on the first click.
LineItem used 20-local-unit strips and horizontal/vertical comparisons to infer
which endpoint was being dragged. That made reversed lines and rotated/local
coordinates difficult to handle and could restore ItemIsMovable on locked lines.

`CanvasLines` now coordinates two-point creation, the transient scene-only
preview, endpoint hit testing, resize gestures and final persistence. Small
GraphicsView hooks run before blank-canvas navigation and the normal item-event
path. The tool is consumed before opening the modal properties dialog, so the
associated focus change cannot discard an accepted drawing.

`LinePropertiesDialog` owns copies of the original pens. Apply changes only the
scene; rejection restores those copies, while OK commits through the controller.
Drafts use the existing create=False/discardDraft lifecycle, so neither the ghost
nor a cancelled line sends POST or DELETE. Confirming a new line sends one POST
with its final endpoints and style.

LineItem now uses normal Qt movement for its body and paints endpoint handles
when selected and unlocked. Endpoint resizing is handled at the view level:

- Hit tolerance is seven viewport pixels, including points outside itemAt's
  geometric hit area. It remains usable across zoom levels and prevents empty
  canvas hand panning from consuming the endpoint click.
- Existing container corner handles keep priority when a line endpoint coincides
  with a selected container corner. Closed containers, locked ancestors, ancestor
  clipping and unrelated elements above the endpoint prevent hidden-handle access.
- Pointer displacement is mapped through the original inverse scene transform.
  Only the dragged endpoint changes; the opposite endpoint, rotation, parenting
  and item movement/lock flags remain intact. Dragging past the opposite endpoint
  is supported rather than clamped to one direction.
- End-of-drag saves exactly once. Extra mouse buttons cannot change the gesture;
  focus loss finishes it, and a removed drawing is not saved. With containers,
  CanvasGroups performs hierarchy-aware saving; standalone lines save directly.
- Starting the line tool clears pending shape previews and container-creation
  selection requests. Navigation mode changes cancel a pending line. Device
  links still use their separate tool and handlers.

SVG stores fractional and negative endpoint coordinates, opacity and a nonzero
viewport for horizontal/vertical lines. It accepts metadata before the line when
loading. Because the drawing API uses integer item positions, serialization
normalizes the origin and retains the fractional remainder in the SVG endpoints.
An acknowledgment therefore preserves the scene endpoints even for a rotated
line created or moved at high zoom.

## Branches and commits

`codex/feature-line` starts at `codex/fix-async-requests` (`45fab9bb`) and merges
only the shared draft lifecycle commit `162c879e`. It does not inherit containers,
geometry authoring, typography, image importing, hand navigation or cursor zoom.
The robust existing main-window test-fixture cleanup is also retained to prevent
deferred startup dialogs from interrupting later gesture tests.

The same feature patches are applied to `codex/canvas-all-improvements`, whose
previous complete implementation remains the base (`125c8771`). The first
cherry-pick required combining GraphicsView hooks with existing event handlers
and retaining both sets of main-window tests; later patches applied cleanly.

| Change | feature-line | canvas-all-improvements |
| --- | --- | --- |
| Two-click drawing, style transaction and endpoint handles | `501033bb` | `5d4c9082` |
| Precision, occlusion and cross-feature resize regressions | `3f43a2ab` | `90a5504f` |

Documentation is committed to both branches after validation. Other feature
branches are unchanged. Review the isolated feature against fix-async-requests,
and the complete-branch addition against `125c8771`.

## Validation

Fresh full-suite command in each checkout:

```sh
QT_QPA_PLATFORM=offscreen python3 -m pytest -q
```

- `codex/feature-line`: **290 passed, 2 skipped**. The additional skip is the
  container integration module, intentionally unavailable on this independent
  branch; the other skip already existed.
- `codex/canvas-all-improvements`: **456 passed, 1 skipped**.
- Both runs retain the existing tarfile deprecation warning. Whitespace checks
  pass. A dark-palette rendering of the real dialog was visually inspected;
  the thickness field has a white background and black text.

Coverage includes creation/cancellation, Apply rollback, no network requests
before OK, both endpoints in four directions, rotation, zoom, body movement,
locked items, fractional API acknowledgments, SVG round trips, interrupted
resizes, real toolbar switching, nested containers, clipped/occluded handles,
coincident container corners and navigation mode switching. The previous
container resize regression suite and the existing zoom, geometry, typography,
image and asynchronous tests also pass on the complete branch.

Qt pointer-tracking tests dispatch real viewport MouseMove events directly when
no button is held, avoiding dependence on the native global cursor left by
another offscreen window. Press/drag/release tests use QTest. This validation
uses offscreen Qt and mocked transport acknowledgments; no interactive desktop
session or fresh disposable-server integration was run for this feature.
