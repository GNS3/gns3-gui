# Zoom direcionado pela posição do mouse

## Uso

Posicione o mouse sobre a parte da topologia que deseja examinar e use
**Ctrl + roda do mouse**. O ponto sob o cursor permanece na mesma posição da
tela enquanto a escala aumenta ou diminui. É possível aproximar uma região,
configurar os elementos e afastar novamente sem reposicioná-la pelas barras
de rolagem. Se mudar o cursor de lugar, o próximo passo de zoom usa esse novo
ponto como referência.

A roda sem Ctrl continua rolando a view. A velocidade do zoom, a faixa de
10% a 1000%, os comandos existentes da barra/menu e o percentual salvo no
projeto são preservados.

## Implementação

`GraphicsView` já configurava o Qt com `AnchorUnderMouse`, mas o caminho de
`wheelEvent()` chamava `scaleView()` somente com um fator de escala. Não havia
compensação explícita usando a posição daquele evento. Além disso, quando a
cena escalada cabe inteira na janela, o alinhamento automático e os limites
das barras do Qt restringem a translação necessária para manter o cursor fixo.

O evento agora passa sua posição local à função `scaleView(scale_factor,
anchor=...)`. A função guarda a coordenada da cena sob aquele pixel, desativa
temporariamente a ancoragem automática, aplica a escala e calcula a diferença
entre a coordenada anterior e a nova. Uma translação da view compensa essa
diferença. Ao final, a configuração anterior de ancoragem é restaurada.
Os comandos que não passam `anchor` continuam usando o caminho anterior.

Para permitir a compensação perto das bordas ou com uma cena pequena, a view
ganha uma área de navegação que inclui o viewport pretendido com uma margem.
Essa extensão pertence apenas ao `QGraphicsView`: o `sceneRect` da cena, as
dimensões salvas do projeto e as posições dos elementos não são alterados.
As barras podem oferecer espaço vazio ao redor da topologia para permitir
essa navegação. `setSceneSize()` limpa a extensão local ao carregar ou alterar
as dimensões de uma cena.

Pedidos fora dos limites de escala são rejeitados antes de mudar a view e não
geram uma atualização redundante do projeto. Eventos sem deslocamento vertical
também não geram zoom. Eventos Ctrl+roda são consumidos para não produzir
rolagem adicional junto da aproximação.

## Validação

Os testes enviam `QWheelEvent` ao viewport real, sem um evento prévio de
movimento do mouse. Isso verifica que a posição do próprio evento decide o
zoom. São usados dois pontos afastados do centro, cenas de 2000×1000 e 100×80,
escalas iniciais de 20%, 100% e 500%, e uma sequência de aproximação e afastamento
perto dos limites de rolagem. A tolerância é de dois pixels, por causa da
quantização das barras de rolagem do Qt.

Também são verificados os limites de escala, a rolagem sem Ctrl, o percentual
enviado ao projeto, a restauração da configuração de ancoragem e a limpeza da
área de navegação ao redefinir o tamanho da cena.

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest -q
```

Resultado: **262 testes aprovados, 1 ignorado**. Permanece o aviso já existente
de depreciação de `tarfile` no teste de instalação de atualizações. Os testes
exercitam a view Qt; não dependem de mudanças nem de uma nova API no servidor.
