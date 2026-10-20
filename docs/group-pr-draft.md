# Suggested title

Add named, nested topology groups to the canvas

# Pull request description draft

This adds named containers for devices, notes, shapes, images and other groups.
Children use their parent's coordinate system. Moving a group moves its contents;
duplicate, delete and ungroup operate on the selected hierarchy. The Topology
Summary displays the same group/device tree and exposes the group actions.

Groups have fixed, editable dimensions and clip overflowing contents. The initial
frame adds 30% to the content dimensions, split across both sides, plus room for
the title. Users can resize a frame from its corners without scaling its children,
rename it by double-clicking its title, and edit its direct children. Temporary
center guides help align a dragged child to its immediate parent. Dragging a new
device template over a group highlights that destination and inserts the returned
node into it after the server confirms creation.

The drop-target border is temporarily thicker and solid. When an existing device
is dragged out of its group, releasing its symbol center outside the parent
detaches it while preserving its scene position and links. In a nested hierarchy,
the device moves to the nearest containing ancestor, or to the canvas if none
contains it. Partial overflow remains clipped until the center leaves the frame.
During exit, the source frame turns red and a view-only foreground preview keeps
the dragged symbol and labels visible beyond ancestor clips without exposing
other overflowing children. Existing devices can also be dropped into a group;
the destination uses the same thick blue border and center guides as template
drops. Ownership changes only on release, including direct group-to-group moves.

The canvas uses Qt parent/child items rather than a selection association. The
implementation keeps the existing menus and tools, adding a toolbar action with
Ctrl+G and Ctrl+Shift+G for ungrouping. Name and dimension fields share one dialog.
With a selection, the group action opens the properties dialog immediately.
Without one, it waits for the next selection and opens the dialog on mouse
release with the selected elements. The request is consumed once; Esc cancels
the wait. Group frames are solid in every state, with thicker blue/red drag
feedback; temporary alignment guides remain dashed.
Guides, hover highlighting and editing state are view-only and are not exported.

## Persistence and server scope

The prototype targets the GNS3 2.2.61 API. That contract persists nodes, links and
drawings, but has no native group resource or parent relationship. Each group is
therefore transported as a drawing with versioned JSON metadata inside its SVG.
The modified GUI reconstructs the Qt hierarchy from that metadata. Normal node
and drawing requests still carry absolute coordinates for compatibility, while
the group metadata stores child-local coordinates.

This makes the feature testable with an unmodified 2.2 server, including portable
projects. It does not make the server hierarchy-aware. Recursive operations are
coordinated by the GUI; older clients do not provide the same semantics. Portable
import regenerates IDs, so this prototype repairs embedded references using
persistent drawing/group identities and a node-name fallback. That is a migration
workaround, not the intended long-term API.

A reported Not Found response on a drawing update also exposed an asynchronous
ordering issue: the client could send PUT before the drawing POST completed.
Drawing updates now wait for creation acknowledgment and preserve edits made
while waiting. Deleting a pending creation schedules cleanup after acknowledgment.
The screenshot alone does not establish the exact cause of that session's error.
The ordering issue is reproducible and can be fixed in the client without a new
server group endpoint.

## Validation

The regression suite covers actual Qt mouse, resize, hover and drag/drop events,
fixed bounds, rendered clipping, nested parenting, center snapping, properties,
summary actions, portable-ID recovery and asynchronous drawing creation.
The disposable-server integration check uses GNS3 2.2.61 with Ethernet switches
and links, tests duplication/export/import/deletion, and deliberately delays
creation POSTs to detect premature updates. It uses lightweight model/transport
adapters and does not exercise every emulator or a full multi-client session.

Run:

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest -q
python3 scripts/check_canvas_groups.py --server http://127.0.0.1:3099
```

The integration command requires a separate disposable server. It creates and
removes only its own test projects.

## Follow-up proposed for the server

Before treating the SVG transport as the final persistence contract, I would like
to agree on a native group model with maintainers. A `groups` collection and one
`parent_group_id` per layout element would let the server validate ownership,
remap all relationships during import, coordinate recursive operations and publish
consistent revisions/events. Group duplication should return the new ID mapping
and track cleanup when a node or compute operation fails. A future GUI adapter
could then retain this interaction model while replacing the SVG transport with
the native API.

The HTTP client also retains in-flight reply wrappers until completion. Requests
without a timeout or progress dialog could otherwise lose Python signal callbacks
to garbage collection, leaving device copies on the canvas before the hierarchy
and internal links were rebuilt. Regression coverage forces collection with real
Qt replies and exercises duplication from the summary menu. The disposable-server
check now uses the actual asynchronous Qt HTTP transport for node duplication.
Copied root groups receive distinct names such as `Copy of LAN 1` and
`Copy 2 of LAN 1`, while nested groups retain their names.

The implementation notes and a concrete server-side proposal are in
`docs/group-server-integration.md`. No server-side group API is implemented by
this GUI change, and that remains the main architectural point for review.
