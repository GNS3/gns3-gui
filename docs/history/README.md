# Histórico da topologia

A implementação pertence a `codex/feature-history`, baseada em
`codex/canvas-all-improvements` no commit `9a3d275c`. Os mesmos commits são
integrados por fast-forward na branch completa, sem duplicação por cherry-pick.
O destino de publicação é `redlintles/gns3-gui-fork`.

## Uso

A barra de controle apresenta **Undo**, **History**, **Redo**, imediatamente
antes de **Manage snapshots**. `Ctrl+Z` e `Ctrl+Y` atuam sobre a topologia;
campos de texto e notas em edição conservam os atalhos nativos do Qt.

History apresenta o estado inicial ainda recuperável e uma linha por operação.
O marcador identifica o cursor; linhas posteriores permanecem disponíveis para
redo. Selecionar uma linha executa os passos necessários em sequência. Clear
history pede confirmação e transforma a topologia atual na nova referência,
sem excluir recursos. Cada projeto mantém até 100 operações. Uma edição após
undo descarta o futuro, enquanto uma operação sem efeito conserva o redo.

## Componentes

- `gns3/history/model.py`: estado canônico JSON, deltas antes/depois, descrições,
  cursor, limite, validação da cadeia e remapeamento de projetos importados.
- `gns3/history/replay.py`: requisições assíncronas, preflight, ordem de
  dependências, verificação, identificação de links recriados e compensação.
- `gns3/history/session.py`: uma sessão por Project, agrupamento de ações,
  captura de respostas confirmadas, atualização do canvas e ciclo de gravação.
- `gns3/history/storage.py`: codec comprimido, checksum, deduplicação de SVGs e
  trabalho de serialização/validação no QThreadPool.
- `gns3/history/ui.py`: ações, proteção do foco de texto e diálogo de navegação.

Não utilizamos QUndoStack: seu contrato síncrono moveria o cursor antes de
terminarem as operações HTTP e suas possíveis compensações. O modelo próprio
mantém o cursor até a verificação do servidor e a aplicação visual terminarem.

## Captura e operações lógicas

Controller.createHTTPQuery é o ponto comum das requisições de Project, Node,
Link e TemplateManager. Apenas POST/PUT/DELETE de nodes, links e drawings,
criação por template e duplicação de dispositivos entram na captura. Requisições
de console, start/stop, snapshots, appliances e arquivos auxiliares não geram
entradas. Campos de execução, como status e captura de pacotes, ficam fora do
estado canônico; propriedades persistentes editáveis continuam incluídas.

Decoradores nas ações e eventos do GraphicsView/CanvasGroups delimitam uma
operação. O botão pressionado abre o gesto e sua liberação o encerra; o registro
aguarda também as respostas HTTP e requisições secundárias dos callbacks.
Mudanças sucessivas do mesmo objeto conservam o primeiro estado anterior e o
último confirmado. No fim, deltas iguais são removidos. Os caminhos existentes
já enviam posições e dimensões ao terminar o gesto; o histórico não adiciona
requisições por pixel percorrido.

A movimentação de uma seleção, os atributos do container e sua associação aos
filhos ficam na mesma operação. Excluir um dispositivo captura também os links
incidentes presentes no cache confirmado, mesmo quando o servidor os remove
por cascata. Uploads grandes mantêm uma operação pendente durante toda a cadeia;
a imagem transparente usada para preparar o diretório é ignorada.

WebSockets e respostas HTTP compartilham o cache canônico, impedindo entradas
extras para ecos. Durante replay os eventos visuais são suspensos; ao terminar,
os recursos verificados passam pelos mecanismos existentes de notificação.
A revisão interna do SVG de containers é normalizada para comparação e elevada
no envio, pois não representa uma ação do usuário.

## Sincronização e falhas

Antes de escrever, replay consulta os recursos afetados e compara seu estado
com o estado esperado. Também consulta os demais endpoints de links e verifica
conexões que seriam removidas por cascata. Mudanças estruturais e de propriedades
em emuladores ligados/suspensos são recusadas; coordenadas e atributos visuais
permanecem editáveis. Objetos de rede internos permanentemente ligados, como
Ethernet switches, seguem seu comportamento próprio no servidor.

A ordem é: desconectar links, remover desenhos/dispositivos, criar dispositivos,
atualizar seus atributos, restaurar desenhos e reconectar links. PUT contém
somente os campos alterados. Nenhum comando de console ou de energia é usado
para contornar restrições. Ao final, GET verifica o estado de cada recurso.
A GUI atualiza somente os recursos alterados e reconstitui a hierarquia; remover
um container preserva os filhos que continuam existindo no estado de destino.

**Particularidade do servidor 2.2.61:** POST /links aceita o campo link_id no
schema, mas gera outro UUID. A implementação utiliza o UUID retornado e reescreve
as referências de todas as entradas, estado atual e conexões da GUI. O mesmo vale
para links restaurados durante compensação. Se a criação perde sua resposta,
a conexão é procurada pelos endpoints e pelos UUIDs ausentes antes da operação,
para evitar deixá-la órfã.

Uma rejeição ou timeout inicia leitura do estado real: timeout pode significar
que a escrita ocorreu. Os deltas inversos necessários são aplicados em ordem de
dependências e verificados novamente. Uma compensação confirmada mantém o cursor;
uma compensação impossível, divergência externa ou falha de sincronização visual
bloqueia o histórico, informa o problema e tenta reconciliar a GUI com o servidor.
Ações concorrentes ficam bloqueadas durante replay e reconciliação. Clear history,
após revisar a topologia, estabelece uma nova referência confirmada.

Não há transação distribuída no GNS3 Server. A compensação é a melhor recuperação
possível pelas APIs disponíveis; uma desconexão permanente não permite prometer
rollback atômico. O sistema nunca avança silenciosamente o cursor nesse caso.

## Persistência e compatibilidade

Dois arquivos binários ficam na raiz do projeto:

- `gns3-gui-history-A.history`
- `gns3-gui-history-B.history`

Cada revisão é gravada em um dos slots pela API existente de arquivos do projeto.
O conteúdo tem checksum SHA-256, gzip e envelope de versão; SVGs idênticos são
armazenados uma única vez. O documento contém a identidade do projeto, manifesto
do estado no cursor e até 100 deltas. Não contém objetos Qt nem referências a
endereços locais de memória. A cadeia é validada nas duas direções antes do uso.
Há um limite de segurança de 64 MiB para o conteúdo serializado deduplicado e sua
leitura expandida; ultrapassá-lo apresenta erro e exige reduzir/limpar o histórico
antes de fechar ou exportar com garantia de persistência.

A extensão `.history` é intencional. O servidor deduz MIME e Content-Encoding
pela extensão: `.json.gz` provoca parsing JSON ou descompressão HTTP automática
no cliente Qt, enquanto o codec precisa receber o arquivo binário original.

A gravação ocorre após cada ação e mudança de cursor. Fechar projeto/aplicação,
exportar e duplicar aguardam a última revisão; falha de gravação impede esses
passos e oferece uma mensagem para permitir nova tentativa. A topologia continua
sendo persistida normalmente pelo servidor. Os arquivos comuns da raiz viajam
na exportação portátil existente, sem alteração do schema oficial `.gns3` e sem
modificações no GNS3 Server.

Na abertura, ambos os slots são lidos. Usa-se a revisão válida mais recente cujo
manifesto corresponde à topologia real; um slot corrompido pode ser ignorado se
outro ainda corresponde ao estado. Um histórico antigo divergente não é executado.
Projetos sem esses arquivos começam com histórico vazio. Se nenhum slot lido
puder ser usado com segurança, os bytes originais de todos os slots são copiados
para arquivos `gns3-gui-history-recovery-<SHA256>.history` na raiz do projeto.
Somente depois da confirmação dessas cópias, uma nova sequência usa a topologia
atual como referência e volta a registrar ações. Os registros incompatíveis
continuam preservados nos arquivos de recuperação; não ficam disponíveis para
undo sobre um estado diferente. A explicação fica no próprio diálogo History, sem interromper a abertura
com um popup de recuperação.

Falha de leitura ou de preservação mantém os slots originais intocados e informa
o erro, sem substituir um arquivo cujo conteúdo não pôde ser preservado. O codec
normaliza os SVGs de estado e deltas antes de comparar a cadeia, evitando rejeitar
um histórico válido só porque outro registro de namespace XML mudou os prefixos.

Importação e Save As podem trocar todos os UUIDs. O remapeamento usa nomes/tipos
únicos dos dispositivos, endpoints dos links e correspondência exata dos desenhos.
Também reescreve referências SVG dos containers e realoca identidades históricas
de recursos ausentes. Consoles realocados sem edição histórica deliberada são
rebaseados; computes precisam ter correspondência consistente. A correção de
referências persistidas dos containers é confirmada no servidor antes de habilitar
o histórico importado.

## Limites conhecidos

- São recuperadas definições da topologia e conexões, **não discos, configurações
  internas ou arquivos de trabalho removidos pelo compute**. Undo de exclusão não
  substitui snapshots/backups de appliances. Uma imagem, compute, console ou
  interface indisponível pode impedir a restauração e produzir erro explícito.
- Mudanças persistentes de outro cliente, restauração de snapshot ou edição manual
  podem tornar os registros incompatíveis. Nenhuma entrada é inventada para essas
  operações externas: a navegação pode ser bloqueada durante a sessão. Na próxima
  abertura, uma divergência persistente passa pela recuperação com cópias preservadas.
- Importação com identidades ambíguas, alteração externa de desenhos/propriedades,
  reset de MACs ou migração de computes sem correspondência segura pode impedir
  a reutilização dos registros anteriores. Eles são arquivados antes de iniciar
  uma nova sequência. A topologia continua abrindo; não se adivinham
  correspondências nem se aplicam deltas sobre recursos possivelmente diferentes.
- Encerramento abrupto pode deixar apenas o slot anterior. Se seu manifesto não
  corresponder à topologia, os arquivos são preservados e uma nova referência
  é gravada, em vez de executar dados obsoletos ou desativar novos registros.

## Validação reproduzível

```sh
QT_QPA_PLATFORM=offscreen python3 -m pytest -q
QT_QPA_PLATFORM=offscreen python3 scripts/check_history.py --server http://127.0.0.1:3099
```

O segundo comando exige um servidor **descartável** GNS3 2.2 e cria/remove apenas
seus próprios projetos. Usa Project, HTTPClient Qt, WebSocket, modelos reais e
canvas reais, sem iniciar appliances dependentes de imagens externas. Verifica
CRUD, seleção agrupada, exclusão/restauração de dispositivo conectado, resize e
movimento de containers, associação de filhos, fechamento/reabertura, exportação
pela API Project, importação com remapeamento e replay de imagens acima de 1 MiB.

Resultado final da suíte: **492 passaram, 1 ignorado**; permanece o aviso de
depreciação de tarfile já existente no teste de atualização.

Os testes automatizados cobrem também cursor/limite/no-op, descarte de redo,
falhas parciais e timeout após escrita aplicada, UUIDs alocados pelo servidor,
compensação impossível, estado divergente, arquivos corrompidos, isolamento de
projetos, falha/repetição de gravação, GUI indisponível, atalhos e diálogo reaberto.
A suíte existente inclui regressões de linhas, zoom, geometria, hand tool,
containers, tipografia, imagens e requisições assíncronas.

Referências do servidor inspecionadas:
[API de nodes](https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/handlers/api/controller/node_handler.py),
[API de links](https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/handlers/api/controller/link_handler.py),
[arquivos de projeto](https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/handlers/api/controller/project_handler.py),
[exportação](https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/controller/export_project.py),
[importação](https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/controller/import_project.py).

## Correções após validação de uso (arraste pela borda)

O teste de integração agora utiliza eventos reais de mouse para retirar um
aparelho conectado do container, inclusive com um link sobreposto ao símbolo.
A operação deve guardar os dois deltas: posição do dispositivo e SVG de
associação do container. Undo e redo verificam também as coordenadas no servidor.

Foram corrigidos três pontos:

- `itemAt()` pode encontrar um link que ignora eventos de mouse, enquanto o Qt
  entrega o gesto ao dispositivo abaixo. O acompanhamento do arraste agora usa
  `mouseGrabberItem()`, mantendo a detecção de saída pela borda.
- Reparenting chamava NodeItem.setPos e atualizava o cache como se as coordenadas
  já estivessem confirmadas. Preservamos as coordenadas confirmadas durante a
  troca de pai visual, permitindo que save envie a posição e registre ambos os
  deltas na mesma ação.
- O GNS3 Server omite SVG em drawing.updated quando seu conteúdo não mudou.
  Eventos parciais agora são combinados com o estado confirmado; isso conserva
  os metadados de associação e evita `Missing history drawing SVG`.

Também foi removida a chamada a setPos em QGraphicsSceneMouseEvent: o binding
Qt6 não oferece esse setter. Os handlers de arraste da classe base utilizam as
posições de cena originais. Um teste captura explicitamente exceções dos eventos
Qt, pois um traceback em um slot pode não reprovar automaticamente o pytest.

Validação após as correções: **497 testes passaram, 1 ignorado**, e o roteiro
com GNS3 Server 2.2.61, HTTP Qt e WebSockets passou com arraste, undo/redo,
persistência, exportação/importação e imagens grandes.


## Recuperação de persistência e continuidade dos registros

A versão anterior mantinha `invalid` quando os dois manifestos não correspondiam
à topologia. Isso também desabilitava `begin`/`record`/`persist`, de modo que cada
nova abertura encontrava os mesmos arquivos obsoletos. O novo caminho de carga
faz a recuperação descrita acima, sem alterar a topologia nem apagar as operações
antigas. O número de revisão da nova referência supera o de todos os candidatos
válidos, evitando que um slot anterior prevaleça na abertura seguinte.

A comparação agora normaliza representações SVG equivalentes também nos deltas,
antes de validar a cadeia, e conserva todas as operações quando o histórico é
compatível. Falhas de backup ou leitura nunca autorizam a substituição dos slots.
As cópias de recuperação são arquivos normais do projeto e acompanham sua exportação.

Testes adicionais verificam os bytes exatos das duas cópias, falha de backup,
slot ilegível, retomada do registro, troca de prefixos XML e duas reaberturas
consecutivas com undo e redo. O roteiro de servidor real também cria uma
incompatibilidade com uma edição externa, recupera o histórico, grava uma nova
ação e verifica seu undo/redo após fechar e reabrir duas vezes.

Resultado da suíte após esta correção de persistência: **502 passaram, 1 ignorado**.
O aviso de depreciação de tarfile pertence ao teste de atualização já existente.


## Revisões de containers, visibilidade e identificação dos gestos

A sequência de saída pela borda com undo/redo podia reutilizar na GUI uma revisão
canônica zero em lugar da revisão real retornada pelo servidor. Um eco atrasado
com associação antiga era então aceito: o dispositivo podia voltar a ser filho
do container mantendo coordenadas externas à sua área recortada, desaparecendo
do canvas sem ser excluído da topologia.

O replay agora retém o SVG físico verificado quando ele representa o mesmo estado
canônico. A GUI recebe sua revisão real, a próxima edição incrementa corretamente
e o gravador ignora ecos anteriores à última revisão confirmada. Listas iniciais
de projeto continuam autoritativas, inclusive quando uma revisão foi reduzida
por restauração de snapshot. O manifesto persistido continua excluindo revisões
internas de transporte.

As descrições de arraste e resize usam o gesto concluído, com nome do dispositivo
e dos containers de origem/destino. Movimentos internos, saídas, entradas,
movimentos de frames e redimensionamentos não dependem da quantidade ou ordem
dos callbacks. A classificação de fallback também considera origem e tamanho
separadamente, sem a descrição ambígua "Move or change container". Diferenças
numéricas equivalentes (100 e 100.0) nos metadados não geram operações falsas.

Uma topologia populada criada antes do histórico, sem slots, abre com referência
inicial vazia e sem popup. Se existirem slots incompatíveis de testes anteriores,
a recuperação ainda preserva seus bytes; somente uma nota no diálogo History
explica a nova sequência. Erros reais de comunicação ou preservação continuam
sendo apresentados.

O roteiro real foi ampliado para seis arrastes sucessivos com espera por eventos
WebSocket, verificação dos pixels do símbolo no viewport, descrições idênticas,
undo/redo, reabertura e uma topologia antiga populada sem slots de histórico.

Validação desta revisão: **509 testes passaram, 1 ignorado**, além do roteiro
com GNS3 Server 2.2.61, notificações WebSocket e verificação visual por pixels.

### Delayed notifications during container exit gestures

Native Qt dragging changes the item's scene position before the release writes
that position to the server. A delayed `node.updated` notification can still
contain the previous coordinates. Applying those coordinates during the gesture
moves the real item independently of the unclipped drag preview. The GUI now
preserves the dragged scene position until release saves it; this includes
descendants carried by a moving container. Other node attributes still update
normally, and server position notifications outside a gesture retain their
existing behavior.

Acknowledgments for a dragged container also wait until release, when the
normal revision check rejects its outdated origin. Queued hierarchy restoration
also waits until dragging/resizing has ended. This prevents saved local
coordinates and clipping parents from being reapplied in
the middle of the user's gesture. The normal release path saves position and
membership together; the history format and persistence files are unchanged.

Regression coverage includes actual viewport pixels at several zoom levels and
outside the original scene bounds, delayed node notifications, and queued
membership restoration. The server check repeats removal/undo on a loaded
pre-history container with a firewall symbol and verifies visibility after the
HTTP/WebSocket responses, alongside the reopen and portable-import checks.

Validation: **520 tests passed, 1 skipped**, plus the real-server X11 checks.

### Desaparecimento após remover dispositivos de containers: causa identificada

A causa era a transferência de propriedade do item gráfico para Python ao chamar
`setParentItem(None)`, embora ele continuasse na cena. A liberação de referências
apagava o gráfico C++, preservando dispositivo e histórico. O helper agora mantém
a cena como dona. Os testes usam referências fracas e coleta explícita para não
mascarar o problema, além de PyAutoGUI e capturas externas sem forçar repintura.

O [relatório completo](CONTAINER_VISIBILITY_INVESTIGATION.md) registra reprodução
antes/depois, screenshots, hipóteses descartadas, invariantes de limpeza,
normalização de console_type em hubs sem console e comandos para repetir os testes.
Validação final: **535 testes aprovados, 1 ignorado**, com servidor real, X11,
Wayland aninhado, undo/redo e persistência após reabrir.

### Clone visual durante replay de associação a containers

A imagem duplicada após Ctrl+Z/Ctrl+Y era um rastro de pintura: a mudança de
posição e de pai com clipping deixava a região anterior sem repintura. Os helpers
de geometria invalidam agora as regiões anterior/atual, incluindo filhos, sem
alterar o formato do histórico nem os recursos do servidor. Veja o
[relatório com reprodução, screenshots e testes](CONTAINER_REPLAY_GHOST_INVESTIGATION.md).
Validação: **537 aprovados, 1 ignorado**; PyAutoGUI em Wayland aninhado e X11
verificou seis ciclos Undo/Redo com zero pixels de símbolo nas posições antigas.
