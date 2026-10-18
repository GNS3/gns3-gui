# Grupos persistentes no canvas

## Executar e testar

Stack: Python >= 3.9 e PyQt6/Qt6. A versão deste checkout é 2.2.61.
As dependências e um servidor GNS3 2.2.61 já estão disponíveis neste computador.
Inicie a GUI modificada em um terminal da sessão gráfica:

```bash
cd /home/jota/gns3-gui
python3 -m gns3.main --profile canvas-grouping --debug
```

Configure o servidor pelo assistente/preferências. O perfil acima separa as
preferências da experiência; os projetos continuam sendo os do servidor
escolhido. Use um projeto de teste ou uma cópia para experimentar as operações.

Em outra máquina Linux com Python e venv instalados:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install PyQt6 -e .
.venv/bin/python -m gns3.main --profile canvas-grouping --debug
```

O servidor GNS3 e os simuladores são instalados/configurados separadamente.

## Como usar

1. Selecione dispositivos, notas, formas, imagens ou grupos com Ctrl+clique ou
   seleção retangular. Os elementos precisam estar no mesmo nível da hierarquia.
2. Clique no botão **Group elements** na barra superior, ou pressione **Ctrl+G**
   com foco no canvas. Informe um nome, por exemplo **LAN 1**, e ajuste largura
   e altura se desejar. Os valores iniciais contêm os elementos selecionados,
   com 30% de espaço extra no total (15% em cada lado) e uma faixa de 24 unidades para o título.
3. O novo elemento aparece com nome e moldura sólida. Arrastar um membro do
   grupo fechado seleciona e move o contêiner inteiro. As posições dos filhos
   passam a ser relativas à origem do grupo.
4. Selecione esse grupo junto de outros elementos e agrupe novamente para criar
   um contêiner pai. Não há um limite de um único nível.
5. Dê duplo clique no corpo do contêiner, ou use **Enter group** no menu de contexto, para
   selecionar/mover seus filhos. Dê outro duplo clique para entrar em um grupo
   interno. **Esc** ou clicar fora do grupo encerra a edição e remove o indicador.
6. Na edição do grupo, os comandos de alinhamento operam nas coordenadas locais
   dos filhos selecionados. Durante o arraste de um filho direto, duas guias
   vermelhas tracejadas marcam os eixos centrais do pai. O centro do elemento
   encaixa a até 6 pixels de cada eixo; a tolerância acompanha o zoom. As guias
   desaparecem ao soltar o mouse ou perder o foco e não pertencem à topologia.
   A grade também usa as coordenadas locais; o encaixe nas guias tem prioridade.
7. Dê duplo clique no **nome** para abrir as propriedades e renomear o grupo,
   ou use **Rename group** no menu de contexto. A mesma janela permite editar
   as dimensões fixas. Mover os filhos não redimensiona a moldura.
   Selecione o grupo e arraste qualquer um dos quatro cantos para redimensionar;
   os filhos mantêm posição e escala. Ao arrastar os cantos esquerdo/superior,
   a origem e as coordenadas locais são compensadas para preservar as posições
   dos filhos na cena. Dimensões menores recortam o conteúdo que excede a borda.
8. **Duplicate** copia a árvore inteira com novas identidades e recria os links
   internos entre os dispositivos copiados. Links para dispositivos externos
   permanecem somente no original. As cópias ficam deslocadas 20 unidades.
9. **Delete** exclui recursivamente o conteúdo e pede confirmação se houver
   dispositivos. Um membro travado impede a exclusão/movimentação do grupo.
10. **Ctrl+Shift+G** ou **Ungroup** dissolve apenas o contêiner selecionado,
    preservando os filhos e suas posições na cena. Se ele era filho de outro
    grupo, seus filhos passam ao contêiner pai.

Arrastar um dispositivo novo da barra de templates sobre um grupo destaca sua
borda e mostra as guias centrais. Ao soltar, o dispositivo é criado pelo servidor
e inserido naquele grupo; em áreas aninhadas, o grupo visível mais interno é o
destino. O destaque não é ativado por arquivos de projeto e desaparece ao sair
ou concluir o drop. O grupo pode estar fechado, sem entrar em modo de edição.

Os campos Width/Height têm fundo branco e texto preto, independentemente do tema.

Salvar/reabrir e exportar/importar preservam os grupos, os nomes e a hierarquia.
A moldura tem dimensões fixas e recorta seus descendentes, incluindo grupos
aninhados. A região do contêiner vai de `(0, 0)` até `(largura, altura)`.
No **Topology Summary**, os grupos aparecem como pastas na hierarquia dos
respectivos dispositivos e portas. O menu de contexto de um grupo oferece
**Rename group**, **Duplicate** e **Delete**, usando as mesmas operações
recursivas do canvas; Delete no teclado também funciona para o grupo selecionado.
Duplo clique no nome do grupo nessa árvore também abre suas propriedades.
O botão superior mostra ajuda na barra de status ao passar o mouse e usa ícones
diferentes para estado normal e hover. Sem seleção, ele aguarda a próxima
seleção no canvas e abre o diálogo ao soltar o mouse; Esc cancela essa espera.
Com uma seleção existente, abre o diálogo imediatamente, assim como Ctrl+G.
O contêiner suporta translação, não rotação/escala do conjunto. Os desenhos
filhos preservam suas rotações individuais. Rótulos de dispositivos/portas
continuam pertencendo aos respectivos objetos; links são relações entre nós,
não objetos independentes de layout. A imagem de marca do fornecedor também
mantém seu tratamento próprio.

## Representação persistente e compatibilidade

A GUI é cliente: o servidor grava `.gns3`, cria snapshots e produz `.gns3p`.
Esta implementação registra cada grupo como um desenho próprio em
`topology.drawings`. Seu SVG contém um bloco `<metadata id="gns3-canvas-group">`
com a extensão de formato versão 2. A versão 1 anterior é carregada e migrada
uma única vez, congelando sua moldura sem deslocar o conteúdo. Exemplo do conteúdo JSON:

```json
{
  "version": 2,
  "revision": 3,
  "name": "LAN 1",
  "drawing_id": "UUID-atual-do-grupo",
  "identity": "UUID-estavel-do-grupo",
  "origin": {"x": 100.5, "y": 80},
  "size": {"width": 600, "height": 400},
  "children": [
    {"type": "node", "id": "UUID-do-no", "key": "SW1", "x": 0, "y": 0},
    {"type": "drawing", "id": "UUID-da-nota", "key": "UUID-estavel", "x": 40, "y": 90},
    {"type": "group", "id": "UUID-do-subgrupo", "key": "UUID-estavel-do-subgrupo", "x": 200, "y": 0}
  ]
}
```

Cada entrada descreve um filho direto, com posição relativa ao grupo. As outras
propriedades continuam nos registros nativos de nós/desenhos. A raiz implícita
é a própria cena. Os IDs podem representar grupos arbitrariamente aninhados,
mas um elemento só pode ter um pai e ciclos são rejeitados antes da restauração.
A origem preserva precisão fracionária mesmo com coordenadas inteiras na API.

As coordenadas enviadas pela API para nós e desenhos são absolutas, como exige
o servidor atual. As coordenadas locais são preservadas na hierarquia dos
grupos. A conversão também é aplicada às respostas do controlador, evitando
que um reconhecimento HTTP reposicione o filho como se ele estivesse na raiz.

O servidor 2.2.61 preserva metadados SVG, incluindo-os em projetos e exportações.
SVGs maiores podem ficar em arquivos de imagens do próprio projeto/arquivo
portátil, conforme o comportamento nativo do servidor. Não há sidecar local
externo ao projeto nem alteração obrigatória no servidor instalado.

Na importação portátil e em Save As, o servidor regenera IDs. O grupo detecta
essa troca pelo próprio `drawing_id` salvo e recupera seus filhos usando a
identidade persistente dos desenhos/grupos e o nome único dos dispositivos.
Depois, grava referências aos IDs atuais. Essa recuperação por chave só ocorre
quando o próprio grupo foi importado com um novo ID; não é usada para adotar
arbitrariamente novos dispositivos durante a edição normal.

Uma GUI antiga pode abrir os dispositivos e desenhos nas posições absolutas,
mas não oferece a semântica dos contêineres. O servidor armazena os grupos como
desenhos: as operações recursivas são implementadas por esta GUI. Alterações
diretas por clientes que não conhecem a extensão não são operações hierárquicas.
Para contribuição oficial, essa representação e eventual API nativa de grupos
precisam ser discutidas com os mantenedores, seguindo `CONTRIBUTING.md`.

## Arquitetura e alterações

A análise partiu de `c776d4ef`; os commits anteriores de agrupamento temporário
são mantidos no histórico, mas essa implementação foi substituída.

- `setup.py` usa setuptools e define `gns3 = gns3.main:main`.
- `gns3/qt` centraliza os bindings PyQt6. `MainWindow` coordena menus, barras e
  comandos. `resources/ui` contém fontes Qt Designer e `gns3/ui`, código gerado;
  não foi necessário regenerar ou reorganizar a interface.
- `GraphicsView` possui a `QGraphicsScene`, ferramentas de mouse, teclado, zoom,
  seleção e comandos. `gns3/items` separa dispositivos SVG, links, notas,
  imagens e formas. `Topology`, `Node`, `Link` e `Project` coordenam o modelo.
- `Controller`/`HTTPClient` usam QtNetwork e QtWebSockets para a API e eventos.
  `gns3/modules` integra os tipos de dispositivo. `LocalConfig` guarda
  preferências locais. O servidor executa os simuladores e persiste o projeto.
- `GroupItem` é um item gráfico e um `DrawingItem` persistente com nome, UUID,
  moldura fixa, recorte por `ItemClipsChildrenToShape` e filhos reais via `setParentItem`. Eventos de um grupo fechado são
  encaminhados ao contêiner; no modo de edição, os filhos recebem os eventos.
- `CanvasGroups` concentra criação, edição, desagrupamento, validação do grafo,
  restauração, gravação, redimensionamento, guias temporárias e cópia assíncrona. Desenhos aguardam o reconhecimento de criação antes de enviar updates,
  evitando PUTs para IDs ainda não registrados no servidor. A duplicação aguarda todos os novos
  IDs de dispositivos antes de gravar a árvore. Em falha de duplicação de um
  dispositivo, solicita rollback das cópias bem-sucedidas; não há transação
  multinó nativa no servidor.
- `Node.setGraphics`, atualizações de `NodeItem` e serialização/atualização de
  desenhos convertem coordenadas entre cena e pai. Links recalculam os pontos
  de conexão e consideram a camada acumulada dos contêineres. Os mecanismos
  existentes de comunicação e exclusão dos dispositivos são reutilizados.
- A restauração ocorre depois do carregamento de nós, links e desenhos. Eventos
  de desenhos do servidor também agendam a reconstrução. Revisões dos grupos
  descartam reconhecimentos SVG antigos que chegarem após uma edição mais nova.
- Desenhos só ganham metadados de identidade ao participarem de grupos;
  projetos sem agrupamento conservam sua serialização anterior.
- `GroupPropertiesDialog` compartilha nome e dimensões entre criação e edição.
  `TopologySummaryView` mantém as linhas existentes de dispositivos e portas ao
  reparentear a árvore por meio do sinal `hierarchy_changed_signal`, preservando
  seleção, expansão e filtros. As guias são desenhadas em `drawForeground` da
  view, sem criar itens nem campos persistentes. O snap ocorre na mudança de
  posição apenas enquanto o elemento é o filho direto sendo arrastado.

O zoom existente usa `AnchorUnderMouse` e Ctrl+roda em `wheelEvent`, com limites
entre 10% e 1000%. `ShapeItem` implementa redimensionamento pelas bordas;
`ImageItem` usa SVG/`DrawingItem` sem esse redimensionamento. Esses recursos não
foram redesenhados nesta alteração.

## Verificação

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest -q
```

Os testes usam pytest, objetos reais do Qt e doubles de transporte/modelo.
Cobrem grupos mistos e aninhados, eventos de arraste, edição de filhos,
alinhamento local, reconhecimento de coordenadas pela API, bloqueios, nomes,
desagrupamento, exclusão com cancelamento, cópia assíncrona, rollback, links
internos, reconstrução, importação com IDs regenerados e validação do grafo.

Há também um teste contra um servidor **descartável** GNS3 2.2.61, sem executar
simuladores. Ele usa a API HTTP real para dispositivos Ethernet switch,
desenhos, duplicação, conexões, exportação/importação e exclusão. Os adapters
leves de modelo evitam iniciar o controlador desktop e os emuladores.

```bash
python3 scripts/check_canvas_groups.py \
  --server http://127.0.0.1:3099 \
  --output-dir /tmp/gns3-canvas-check
```

O script cria e remove somente os projetos de teste que ele próprio criou.
Deixa uma exportação `.gns3p` e capturas do canvas, do Topology Summary e das
guias temporárias no diretório de saída.
A suíte e esse teste não substituem a avaliação manual de usabilidade com a
sua topologia real.

Resultado desta revisão: a suíte também cobre os quatro cantos, recorte em
renderização, dimensões fixas após mover os filhos, migração da versão 1,
propriedades, saída por clique externo, snap ao pai direto, integração da árvore
e ajuda/estado do botão por eventos reais de hover. O teste integrado passou
com servidor 2.2.61, verificando dimensões e hierarquia também após duplicação
e exportação/importação. Os projetos descartáveis são removidos ao final.

Suíte final desta revisão: **223 aprovados, 1 ignorado**, com o aviso existente
de depreciação de `tarfile` no teste do instalador de atualizações.

O relato técnico sobre as limitações encontradas no contrato GUI/servidor, a
análise do 404 e a proposta de suporte nativo estão em
[group-server-integration.md](group-server-integration.md). Um texto em inglês
para discussão em PR está em [group-pr-draft.md](group-pr-draft.md).

### Correção posterior da duplicação

As cópias recebem nomes como `Copy of LAN 1` e `Copy 2 of LAN 1`; os grupos
internos mantêm seus nomes. Foi corrigida a perda dos callbacks HTTP que impedia
concluir a associação dos filhos e a recriação dos links internos. A reprodução,
a causa e os testes estão em [group-duplication-fix.md](group-duplication-fix.md).
A validação posterior terminou com **226 aprovados e 1 ignorado**, além do teste
com servidor 2.2.61, agora usando o transporte Qt assíncrono para a duplicação.

### Destaque sólido e saída de dispositivos por arraste

Ao arrastar um dispositivo novo da lista de templates sobre um grupo, o
contorno temporário agora usa uma linha **sólida** de quatro unidades de largura.
Ao sair da área ou soltar o dispositivo, volta ao contorno sólido de espessura normal.
As guias de centro continuam temporárias e tracejadas; elas têm outra função.
A mesma indicação de destino também atende dispositivos já presentes no canvas.

Para retirar um dispositivo existente, entre no grupo e arraste o dispositivo
para fora. A retirada acontece ao soltar o botão do mouse, quando o **centro do
símbolo** está fora do retângulo do pai direto. Deixar apenas parte do símbolo
para fora mantém o dispositivo no grupo e preserva o recorte. Um clique sem
movimento também não altera a hierarquia.

Em um grupo aninhado, o dispositivo passa ao ancestral mais próximo cujo
retângulo ainda contenha seu centro. Se nenhum ancestral o contiver, passa a
pertencer diretamente ao canvas. Isso permite sair de um grupo interno sem
sair automaticamente de um contêiner externo maior. Essa interação se aplica
a dispositivos; o arraste de notas, formas, imagens e grupos mantém o
comportamento anterior.

No código, `CanvasGroups.beginDrag()` registra as posições dos dispositivos
selecionados no mesmo pai. `endDrag()` avalia os que realmente mudaram de posição,
depois de o Qt terminar de processar a soltura em `GraphicsView.mouseReleaseEvent()`.
Durante o gesto, o dispositivo continua filho do grupo; a prévia descrita abaixo
permite vê-lo fora da borda.
O helper `reparent()` preserva a posição no canvas e a camada visual; os links
continuam ligados aos mesmos dispositivos. O salvamento inclui o dispositivo,
o pai anterior, mesmo que tenha ficado vazio, e os ancestrais envolvidos.
Assim os metadados persistidos e o Topology Summary refletem a nova hierarquia.
As guias e o estado de arraste são limpos ao final.

Não foi necessário alterar o formato de arquivo nem a API do servidor. Os
testes usam eventos reais de mouse nas quatro bordas, verificam a árvore lateral
e a restauração dos metadados, a posição, os links e a saída de grupos aninhados.
Também verificam cliques sem movimento, recorte parcial e a renderização do
contorno contínuo durante o destaque, seguida da volta à espessura normal.
Resultado desta revisão: **235 testes aprovados e 1 ignorado**, com o aviso já
existente de depreciação de `tarfile` no teste do instalador de atualizações.

### Prévia de saída e transferência entre grupos

Quando o centro de um dispositivo arrastado sai do pai direto, o contorno desse
grupo fica vermelho, sólido e engrossado. O símbolo e seus rótulos passam a
ser visíveis fora da borda durante o arraste. Voltar para dentro limpa essa
indicação; soltar fora conclui a saída. O critério continua sendo o centro do
símbolo, então um elemento apenas parcialmente para fora continua recortado
enquanto o centro permanecer dentro.

Um dispositivo que já esteja na topologia pode ser inserido em um grupo por
arraste. O grupo sob o centro do símbolo recebe o mesmo contorno azul sólido
e engrossado usado para dispositivos novos, junto das guias de centro. Soltar
confirma a inserção. Isso também permite transferir um dispositivo diretamente
de um grupo para outro: a origem fica vermelha e o destino azul. O destino é o
grupo visível mais interno naquela posição, respeitando os bloqueios do grupo
e dos seus ancestrais. Posição no canvas e links são preservados.

`updateDrag()` calcula a prévia depois que o Qt atualiza as posições. Não há
reparenting temporário: o pai e os metadados só mudam em `endDrag()`. Para mostrar
o dispositivo fora do recorte sem revelar os demais filhos, `drawDragPreviews()`
pinta o símbolo e seus rótulos no foreground, apenas nos pixels excluídos pelo
recorte dos ancestrais. O recorte normal dos grupos continua ativo. Essa prévia,
as cores e as guias são estados da visualização e não entram na topologia
exportada. Soltar, perder o foco ou sair da edição limpa o estado temporário.

A suíte desta revisão terminou com **239 aprovados e 1 ignorado**, mantendo o
aviso anterior de `tarfile`. Os testes novos cobrem saída com símbolo/rótulos
visíveis fora da borda, outros filhos ainda recortados, contorno vermelho,
retorno ao grupo original, entrada a partir do canvas e transferência entre
grupos, incluindo a árvore lateral e a restauração dos metadados.

### Criação pela barra superior após selecionar

O botão **Group elements** e Ctrl+G usam `CanvasGroups.requestGroup()`. Quando
já há uma seleção válida, o diálogo abre imediatamente. Sem seleção, o pedido
fica pendente: selecione os elementos com o retângulo de seleção e solte o
botão esquerdo. O diálogo abre uma única vez, com os elementos selecionados
naquele momento, incluindo dispositivos, desenhos, textos e grupos. Para montar
uma seleção por vários Ctrl+cliques, faça isso antes de acionar o botão.

A soltura é processada primeiro pelo Qt, depois a seleção é normalizada para o
nível atual da hierarquia e só então `finishSelection()` chama a criação já
existente. O pedido é consumido antes do modal, portanto cancelar o diálogo não
deixa a próxima seleção abrindo outro modal. Uma seleção vazia mantém a espera;
Esc e a limpeza do projeto cancelam o pedido. Cliques direitos, pan e ferramentas
de desenho ou criação de links não concluem esse pedido. O botão permanece
momentâneo, sem ficar pressionado ou azul depois do clique.

Todas as molduras dos grupos agora são sólidas: estado normal, seleção, edição,
entrada azul e saída vermelha. As indicações de arraste continuam mais espessas.
O contorno externo do ícone do botão também é sólido. As guias temporárias de
alinhamento continuam tracejadas para se distinguirem dos contornos.

Validação: **247 testes aprovados e 1 ignorado**, com o aviso já existente de
`tarfile`. O teste do botão usa um `QToolBar` real, eventos de mouse e uma seleção
retangular contendo dois dispositivos e uma nota, deixando um terceiro
dispositivo de fora. Confere que o diálogo só abre na soltura e cobre tanto a
confirmação quanto o cancelamento. Outros testes cobrem seleção prévia, Esc,
seleção vazia e continuidade dos contornos em seleção, edição e hover.
