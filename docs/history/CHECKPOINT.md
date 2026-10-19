# History implementation checkpoint

Branch: codex/feature-history. Base: 9a3d275c (complete canvas including lines).
The complete branch is to be fast-forwarded to the verified feature commits;
there is no reason to duplicate them with cherry-picks.

## Investigation completed

- Project, Node, Link and drawing writes converge on Controller.createHTTPQuery.
  Only topology resource CRUD and template/duplicate creation should be captured;
  console, emulator lifecycle, appliance import and project navigation are excluded.
- GUI requests and websocket notifications race. Records must wait for callback
  completion and logical gesture/dialog closure, with replay recording suppressed.
- GNS3 2.2.61 provides project-file GET/POST. Ordinary project-root files are
  included in portable exports, without extending the official .gns3 schema.
- Portable import changes node, link and drawing UUIDs; history references and
  container SVG metadata must be remapped and validated against the imported state.
- Node deletion can delete compute working files. This feature records topology
  definitions, not emulator disk/console state. Restoration must fail explicitly
  if a required compute/image/interface is unavailable; it must never claim that
  arbitrary emulated data has been backed up.

## Work remaining

1. Implement/verify bounded linear model, delta validation and import remapping.
2. Implement async replay preflight, ordered CRUD, compensation and verification.
3. Integrate confirmed GUI requests, gesture/dialog grouping and project lifecycle.
4. Add durable project-file storage, export/close flush and history UI/shortcuts.
5. Add integration/regression tests, documentation, fast-forward complete branch
   and push both branches to https://github.com/redlintles/gns3-gui-fork.

Keep updating this file at component checkpoints. Never describe an unfinished
component as implemented in the final response.

## Primary server references inspected

- https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/schemas/node.py
- https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/schemas/link.py
- https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/handlers/api/controller/project_handler.py
- https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/controller/export_project.py
- https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/controller/import_project.py
