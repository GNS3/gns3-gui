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

## Component checkpoints

1. DONE: bounded linear model, validation and conservative import remapping.
2. DONE: async replay preflight, dependency-ordered CRUD, compensation and verification.
   Core tests cover applied-write timeouts, allocated UUIDs and failed compensation.
3. DONE: confirmed request capture, gesture/dialog grouping and project lifecycle.
4. DONE: checked two-slot project-file storage, export/close flush and history UI/shortcuts.
5. DONE: regression review, integration tests and architecture/limitations documentation.
6. Delivery: fast-forward the complete branch and push both refs together to
   https://github.com/redlintles/gns3-gui-fork; remote refs confirm publication.

Keep updating this file at component checkpoints. Never describe an unfinished
component as implemented in the final response.

## Primary server references inspected

- https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/schemas/node.py
- https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/schemas/link.py
- https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/handlers/api/controller/project_handler.py
- https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/controller/export_project.py
- https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/controller/import_project.py

## Integration checkpoint

- Full suite: 492 passed, 1 skipped; existing tarfile deprecation warning.
- Real GNS3 Server 2.2.61: CRUD, grouped moves, node/link restoration,
  container movement/resize/membership, reopen, portable export/import/replay,
  and oversized image replay passed using the actual Qt HTTP client and canvas.
- Extended run passed with WebSocket notifications, Project export/close flush,
  container movement/resize and oversized images enabled.
- Link POST ignores link_id on this server. Replay now rebinds the whole history
  to returned IDs, including compensation and lost-acknowledgment discovery.
- Storage uses .history (checked, compressed binary); .json/.gz suffixes trigger
  MIME parsing or transparent HTTP decoding in the existing client.
- Implementation and validation are complete. The delivery step uses the same
  commits on both branches; verify their remote tips before handing off.
- Architecture, recovery limits and reproduction commands: README.md in this folder.

## Correção de regressões após uso

- Corrigidos o setter inexistente do evento Qt6 e os eventos drawing.updated
  sem SVG, preservando o estado confirmado e seus metadados.
- Arraste usa o mouseGrabberItem real quando um link se sobrepõe ao dispositivo.
- Reparenting conserva coordenadas confirmadas até o envio ao servidor, evitando
  que a posição deixe de integrar a operação de remoção do container.
- Regressão automatizada: 497 passaram, 1 ignorado; roteiro real de arraste e
  undo/redo executado contra GNS3 Server 2.2.61 com WebSockets.

## Recuperação de persistência após divergência

- Causa confirmada: uma falha de correspondência dos dois slots mantinha invalid
  e bloqueava também a gravação de todas as operações seguintes.
- SVGs de estado e deltas são normalizados antes da validação, conservando a
  cadeia quando a diferença era apenas representação de namespace XML.
- Slots incompatíveis/corrompidos são preservados byte a byte em cópias
  gns3-gui-history-recovery-<SHA256>.history antes de estabelecer nova referência.
  Falha de leitura ou backup mantém os originais intocados.
- Mensagem informativa explica a recuperação; novos registros voltam a funcionar.
- Validação: 502 passaram, 1 ignorado; servidor GNS3 2.2.61 verificou backup exato,
  retomada dos registros e undo/redo após duas reaberturas consecutivas, além dos
  cenários anteriores de exportação/importação, containers e imagens grandes.
- Código, testes e documentação completos; publicar os mesmos commits em
  codex/feature-history e codex/canvas-all-improvements no fork autorizado.


## Regressão de visibilidade e descrições após undo/redo

- Reproduzida reanexação tardia de um dispositivo arrastado para fora: a GUI
  recebia revisão canônica zero no replay e aceitava ecos de associação antigos.
- SVG verificado mantém revisão física na GUI; ecos anteriores são ignorados
  pelo histórico. A carga inicial continua aceitando a revisão real do servidor.
- Descrições de gestos de arraste/resize agora são explícitas e estáveis, com
  fallback semântico e normalização de números equivalentes nos metadados.
- Recuperação deixa nota em History sem popup na abertura; topologias antigas
  populadas sem histórico foram verificadas com referência vazia e sem aviso.
- Cenário real: seis saídas consecutivas com undo/redo, pintura do símbolo no
  viewport e notificações reais; reabertura/exportação/importação preservadas.
- Suíte final: 509 passaram, 1 ignorado; commits devem ser integrados às três
  branches atuais (canvas-improvements, codex/canvas-all-improvements e
  codex/feature-history) sem reescrever commits preexistentes.
