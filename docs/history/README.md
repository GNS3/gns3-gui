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
Projetos sem esses arquivos começam com histórico vazio. Conteúdo inválido ou
versão desconhecida desabilita somente a navegação do histórico e permite limpar
os registros após revisão da topologia.

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
  operações externas: o histórico precisa ser limpo quando houver divergência.
- Importação com identidades ambíguas, alteração externa de desenhos/propriedades,
  reset de MACs ou migração de computes sem correspondência segura pode bloquear
  a recuperação do histórico. A topologia continua abrindo; não se adivinham
  correspondências nem se aplicam deltas sobre recursos possivelmente diferentes.
- Encerramento abrupto pode deixar apenas o slot anterior. Se seu manifesto não
  corresponder à topologia, o histórico é bloqueado em vez de executar dados obsoletos.

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
