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

## Corrida assíncrona ao sair de um container persistido

- Reproduzido com container carregado do servidor e símbolo firewall: um evento
  node.updated atrasado reposicionava o item real durante o arraste, enquanto a
  prévia externa ao recorte permanecia no destino. O rastreamento confirmou
  NodeItem.updatedSlot como origem da mudança de posição.
- A posição de dispositivos arrastados, inclusive descendentes de containers
  movidos, pertence ao gesto até a liberação do mouse. Outros atributos recebidos
  continuam sendo aplicados; fora do gesto as posições do servidor são aceitas.
- Restaurações agendadas de associações aguardam o término de arraste/resize,
  evitando reaplicar posições locais e pais de recorte durante o gesto.
- Testes Qt cobrem ecos atrasados, movimento de descendentes, restauração
  enfileirada e pintura com diferentes zooms e coordenadas fora da cena original.
- Ecos do próprio container também aguardam o fim do gesto; o avanço da
  revisão no save rejeita a origem antiga, sem deslocar a árvore de filhos.
  O teste dedicado falhava antes da correção.
- Suíte: 520 passaram, 1 ignorado; aviso de tarfile preexistente.
- Servidor GNS3 2.2.61 + X11 virtual: 30 remoções/undos com símbolo visível,
  reabertura, exportação/importação e os demais cenários completos passaram.

## Causa definitiva do desaparecimento de itens após desanexação

- Confirmado no PyQt/SIP: setParentItem(None) torna o item Python-owned mesmo
  permanecendo na cena. Ao liberar referências temporárias, o gráfico C++ é
  destruído, mas Node e recurso do servidor continuam existindo.
- Helper reparent transfere a propriedade para a cena quando desanexa um item
  que ainda pertence a ela. Rascunhos, removeItem e clear mantêm suas regras.
- Testes anteriores retinham referências fortes e mascaravam a falha. Novos
  testes e o roteiro nativo usam weakref, del e gc.collect entre as ações.
- Versão anterior reproduziu a falha na primeira remoção: item gráfico destruído,
  model_exists=True e server_exists=True. Screenshots antes/depois preservadas.
- Oito hubs, inserções/remoções sucessivas, undo/redo e reabertura foram validados
  com PyAutoGUI e screenshots externas em X11 e em Qt Wayland aninhado.
- Detectado também console_type null -> "none" ao reabrir hubs sem console;
  normalização semântica conserva históricos válidos, inclusive campos ausentes.
- Suíte final: 535 aprovados, 1 ignorado. Roteiro completo de histórico, servidor,
  exportação/importação e recuperação também passou.
- Relatório: CONTAINER_VISIBILITY_INVESTIGATION.md. Roteiro:
  scripts/check_container_visibility.py. Publicação nas três branches atuais
  usa os mesmos hashes, sem reescrever histórico Git.

## Clone visual após Undo/Redo de saída de container — retomada 20/10/2026

- Worktree temporário perdido na interrupção; correção e testes reconstruídos.
- Reproduzido no primeiro Ctrl+Z: 1.883 pixels antigos, um item por UUID.
- Causa: região antiga omitida pela invalidação Qt ao trocar pai com clipping.
- Helpers de geometria invalidam regiões anterior/atual, incluindo filhos.
- Dois testes Qt falham no baseline e passam corrigidos; suíte 537/1 ignorado.
- PyAutoGUI: seis ciclos Undo/Redo em Wayland aninhado e X11 sem rastros.
- Ambiente disponível: Ubuntu 24.04.5, conforme o pedido atualizado.
- Relatório e screenshots: CONTAINER_REPLAY_GHOST_INVESTIGATION.md.
