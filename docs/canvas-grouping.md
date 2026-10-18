# Canvas: análise e teste de agrupamento

## Base analisada

Implementação a partir de `c776d4ef`, versão local `2.2.61`, na branch
`codex/canvas-device-grouping`. Nenhuma alteração de versão ou protocolo.
O repositório é a própria GUI do GNS3, não uma reimplementação web.

## Tecnologias e organização

- Python >= 3.9; empacotamento com setuptools (`setup.py`); comando `gns3`
  aponta para `gns3.main:main`.
- PyQt6/Qt6: aplicação desktop com loop de eventos, sinais/slots, diálogos,
  menus e barras. `gns3/qt` centraliza a compatibilidade dos bindings.
- `resources/ui` e `gns3/ui`: fontes do Qt Designer e código gerado.
  `scripts/build_pyqt.py` regenera a interface. A adição desta experiência é
  feita em `MainWindow`, sem editar arquivos gerados ou reorganizar a interface.
- `MainWindow` coordena comandos e estado da interface. `GraphicsView` contém
  uma `QGraphicsScene`: seleção retangular, mouse, teclado, zoom, arraste,
  criação de anotações e links, menus e comandos sobre os selecionados.
- `gns3/items` separa as representações gráficas. `NodeItem` é um item SVG;
  rótulos são filhos, links são itens próprios que calculam suas extremidades
  a partir dos dispositivos. `Node`, `Link`, `Project` e `Topology` representam
  e coordenam os objetos da topologia. `gns3/modules` reúne integrações com
  VPCS, QEMU, Dynamips e outros tipos de dispositivo.
- A GUI conversa com o servidor por HTTP e recebe notificações por WebSocket
  (`Controller`, `HTTPClient`, `Project`, QtNetwork e QtWebSockets).
  A execução dos simuladores depende do servidor; este repositório é o cliente.
- Configurações locais passam por `LocalConfig`. Há dependências auxiliares
  para schemas JSON, sistema operacional/processos, certificados, temas e
  telemetria opcional em `requirements.txt`.
- Testes usam pytest, mocks e objetos reais do Qt. `tests/conftest.py` troca
  os sinais próprios por sinais síncronos; o teste de arraste usa eventos reais
  do Qt, mas a comunicação com o servidor é simulada.

## Caminhos relevantes do canvas

`GraphicsView.mousePressEvent` trata seleção e ferramentas. O Qt move os itens
selecionados durante o arraste. `NodeItem.itemChange` aplica a grade e ajusta os
links; `GraphicsView.mouseReleaseEvent` chama `NodeItem.mouseRelease`, que chama
`updateNode` e `Node.setGraphics` para enviar as coordenadas ao controlador.

O agrupamento reutiliza a seleção múltipla do Qt. Cada grupo é um conjunto de
`NodeItem`; clicar num membro expande a seleção. Não há reparentamento para
`QGraphicsItemGroup`, que mudaria as coordenadas locais dos dispositivos e
exigiria rever links, rótulos e persistência. A limpeza descarta itens removidos
ou destruídos; `reset` elimina os grupos ao fechar/trocar o projeto. Grupos
selecionados podem ser unidos. Um membro travado bloqueia o arraste do grupo.

Há apenas um botão novo na barra de anotações superior. O comando inverso fica
no menu Annotate. Os atalhos pertencem ao canvas, evitando ativação em outros
campos e diálogos. O código permanece em inglês, como a interface existente.

## Observações sobre os outros problemas relatados

O zoom já configura `AnchorUnderMouse` e trata Ctrl+roda em `wheelEvent`, com
limites entre 10% e 1000% em `scaleView`. Isso demonstra a intenção no código,
não garante que o comportamento observado pelo usuário esteja correto em todas
as plataformas; precisa de reprodução específica antes de alterar esse caminho.

`ShapeItem` implementa redimensionamento pelas bordas em coordenadas da cena.
`ImageItem` herda de `QGraphicsSvgItem` e `DrawingItem`, sem o tratamento de
redimensionamento de `ShapeItem`. Imagens raster também passam pelo renderer
SVG próprio (`QImageSvgRenderer`). Esses caminhos não foram modificados.

## Executar neste computador

As dependências de execução já estavam disponíveis no Python do sistema e há
um executável `gns3server`. A GUI confirmou `2.2.61` com `--version`.
No terminal gráfico:

```bash
cd /home/jota/gns3-gui
python3 -m gns3.main --profile canvas-grouping --debug
```

O perfil separado mantém as preferências desta experiência separadas do perfil
padrão. Configure a conexão com seu servidor GNS3 pelo assistente/preferências.
Use um servidor compatível com a GUI 2.2.61 e um projeto de teste ou uma cópia:
as posições alteradas continuam sendo enviadas ao servidor normalmente.
Não inicie outra GUI no mesmo projeto simultaneamente.

Para preparar outro ambiente Linux com Python e suporte a venv instalados:

```bash
cd /home/jota/gns3-gui
python3 -m venv .venv
.venv/bin/python -m pip install PyQt6 -e .
.venv/bin/python -m gns3.main --profile canvas-grouping --debug
```

Isso instala a GUI; servidor, simuladores, imagens e ferramentas externas são
configurados separadamente. Não é necessário recompilar os arquivos `.ui`.

## Teste manual

1. Abra um projeto de teste com dois ou mais dispositivos.
2. Selecione dispositivos usando Ctrl+clique ou um retângulo de seleção.
3. Clique no novo ícone (dois quadrados em uma borda tracejada), com tooltip
   “Group devices (Ctrl+G)”, ou pressione Ctrl+G com foco no canvas.
4. Clique no fundo para limpar a seleção e arraste um membro: os demais serão
   selecionados e movidos junto; os links acompanham os dispositivos.
5. Selecione membros de dois grupos e use Ctrl+G para uni-los.
6. Use Annotate > Ungroup devices ou Ctrl+Shift+G para dissolver o grupo.
7. Confira o bloqueio com um membro travado e a remoção de um dispositivo.

## Limites desta experiência

A associação de grupo dura somente a sessão do projeto. Ao reabrir, as posições
continuam salvas, mas é necessário agrupar novamente. Isso evita introduzir um
campo novo no protocolo/arquivo do servidor antes de definir sua compatibilidade
com o projeto oficial. Não há grupos aninhados, moldura permanente, nomes de
grupos, undo novo ou agrupamento de imagens/formas/rótulos. A grade mantém as
regras atuais por dispositivo; desative Snap to grid para testar deslocamentos
livres com espaçamento preservado. O bloqueio impede arraste pelo mouse; outros
comandos continuam com as regras existentes sobre os itens selecionados.

## Verificação automatizada

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest -q
```

Os testes cobrem arraste por eventos do Qt, atualização dos dois dispositivos,
grupo com membro travado, união/desagrupamento, limpeza de membro destruído e
integração das ações na janela. Não substituem a validação gráfica manual com
um servidor e uma topologia real. Para contribuição futura, seguir também
`CONTRIBUTING.md` e discutir a persistência com os mantenedores.
