# Zoom com o cursor como centro da lupa

## Uso

Posicione o mouse sobre a região que deseja examinar e use **Ctrl + roda**.
A região aumenta ou diminui ao redor do cursor: o ponto sob ele permanece na
mesma posição da tela. Não há deslocamento para o centro da janela, animação
pendente ou foco preso a um ponto anterior. Você pode mover o cursor a qualquer
momento; o próximo evento usa a posição atual, tanto ao aproximar quanto ao
afastar.

Os passos também ficaram menores: um notch convencional de 120 unidades
aproxima cerca de 9%, em vez dos cerca de 19% anteriores. Deltas menores
produzem passos proporcionalmente menores; afastar desfaz a escala equivalente.
A roda sem Ctrl continua rolando a view, e os limites seguem em 10% e 1000%.
Os comandos de zoom da barra e do menu mantêm seu caminho existente.

## Implementação e revisão da interação

A revisão anterior levava a região escolhida para o centro e guardava esse foco
para os eventos seguintes. Esse comportamento foi removido após o esclarecimento
da interação desejada. Não é necessária uma sequência de scrolls para o foco
ser escolhido: cada evento calcula sua própria referência.

`wheelEvent()` passa a posição do evento para `scaleView(scale_factor, anchor)`.
A função guarda a coordenada da cena sob esse pixel, desativa temporariamente
a ancoragem automática do Qt, aplica a escala e compensa por translação a
variação da coordenada sob o cursor. A configuração de ancoragem é restaurada
ao final. O fator da roda é `2 ** (delta_y / 960)`, preservando deltas fracionados
sem impor o salto de um notch inteiro.

Uma margem de navegação pertencente apenas à view permite a compensação perto
das bordas ou quando a cena escalada é menor que a janela. O retângulo da cena,
as dimensões salvas e as posições dos dispositivos não são modificados.

## Correção dos resets após confirmação do servidor

Foi preservada a correção identificada na revisão do vídeo. Salvar o percentual
de zoom dispara confirmações HTTP e notificações; `Topology._projectUpdatedSlot()`
reaplica as dimensões da cena. Antes, isso apagava a área local de navegação
mesmo quando o tamanho era igual, desfazendo o posicionamento e alterando as
barras de rolagem repetidamente.

`setSceneSize()` continua ignorando dimensões já aplicadas. A margem local é
limpa quando o tamanho realmente muda ou quando o projeto é limpo/trocado.
Cada passo de zoom solicita uma repintura completa do viewport. Pedidos fora
dos limites não mudam a view nem geram uma atualização redundante do projeto.

## Validação

A suíte usa eventos de roda reais no viewport Qt, sem depender de movimento
prévio do mouse. Verifica pontos fora do centro, cenas grandes e pequenas,
escalas iniciais de 20%, 100% e 500% e passos de aproximação/afastamento. A
coordenada sob o cursor deve permanecer no mesmo pixel, com tolerância de dois
pixels devido à quantização das barras do Qt.

Outros testes mudam a posição do cursor a cada evento, alternam as direções,
verificam os novos passos menores e sua reversão, reaplicam dimensões recebidas
do servidor e conferem estabilidade da transformação e geometria do viewport.
Também cobrem limites, rolagem sem Ctrl, percentual salvo e limpeza da margem.

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest -q
```

Resultado: **265 aprovados, 1 ignorado**, com o aviso preexistente de `tarfile`.
A interação foi validada na view Qt offscreen; a avaliação de conforto no desktop
pode ser feita repetindo o percurso do vídeo depois de reiniciar a GUI.
