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
   com foco no canvas. Informe um nome, por exemplo **LAN 1**.
3. O novo elemento aparece com nome e moldura tracejada. Arrastar um membro do
   grupo fechado seleciona e move o contêiner inteiro. As posições dos filhos
   passam a ser relativas à origem do grupo.
4. Selecione esse grupo junto de outros elementos e agrupe novamente para criar
   um contêiner pai. Não há um limite de um único nível.
5. Dê duplo clique no contêiner, ou use **Enter group** no menu de contexto, para
   selecionar/mover seus filhos. Dê outro duplo clique para entrar em um grupo
   interno. **Esc** encerra a edição e volta ao nível principal.
6. Na edição do grupo, os comandos de alinhamento operam nas coordenadas locais
   dos filhos selecionados. A grade também usa essas coordenadas locais.
7. Use **Rename group** no menu de contexto para mudar o nome.
8. **Duplicate** copia a árvore inteira com novas identidades e recria os links
   internos entre os dispositivos copiados. Links para dispositivos externos
   permanecem somente no original. As cópias ficam deslocadas 20 unidades.
9. **Delete** exclui recursivamente o conteúdo e pede confirmação se houver
   dispositivos. Um membro travado impede a exclusão/movimentação do grupo.
10. **Ctrl+Shift+G** ou **Ungroup** dissolve apenas o contêiner selecionado,
    preservando os filhos e suas posições na cena. Se ele era filho de outro
    grupo, seus filhos passam ao contêiner pai.

Salvar/reabrir e exportar/importar preservam os grupos, os nomes e a hierarquia.
A moldura cresce para envolver o conteúdo; não é uma máscara de recorte.
O contêiner suporta translação, não rotação/escala do conjunto. Os desenhos
filhos preservam suas rotações individuais. Rótulos de dispositivos/portas
continuam pertencendo aos respectivos objetos; links são relações entre nós,
não objetos independentes de layout. A imagem de marca do fornecedor também
mantém seu tratamento próprio.

## Representação persistente e compatibilidade

A GUI é cliente: o servidor grava `.gns3`, cria snapshots e produz `.gns3p`.
Esta implementação registra cada grupo como um desenho próprio em
`topology.drawings`. Seu SVG contém um bloco `<metadata id="gns3-canvas-group">`
com a extensão de formato versão 1. Exemplo do conteúdo JSON:

```json
{
  "version": 1,
  "revision": 3,
  "name": "LAN 1",
  "drawing_id": "UUID-atual-do-grupo",
  "identity": "UUID-estavel-do-grupo",
  "origin": {"x": 100.5, "y": 80},
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
  moldura e filhos reais via `setParentItem`. Eventos de um grupo fechado são
  encaminhados ao contêiner; no modo de edição, os filhos recebem os eventos.
- `CanvasGroups` concentra criação, edição, desagrupamento, validação do grafo,
  restauração, gravação e cópia assíncrona. A duplicação aguarda todos os novos
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
Deixa uma exportação `.gns3p` e uma captura do canvas no diretório de saída.
A suíte e esse teste não substituem a avaliação manual de usabilidade com a
sua topologia real.

Resultado desta revisão: **204 testes aprovados, 1 ignorado**. O aviso existente
é uma depreciação de `tarfile` no teste do instalador de atualizações. O teste
integrado passou com servidor 2.2.61, duplicação de dispositivos e links,
exportação/importação de quatro grupos aninhados, recuperação dos IDs e
exclusão recursiva. Os projetos descartáveis foram removidos ao final.
