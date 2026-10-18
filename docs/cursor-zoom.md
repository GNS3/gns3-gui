# Zoom para focar regiões da topologia

## Uso

Posicione o mouse sobre a região que deseja configurar e use **Ctrl + roda
para cima**. O ponto escolhido vai para o **centro da janela**. Os passos
seguintes da roda, mantendo o mouse no mesmo lugar, aproximam essa região sem
escolher outro ponto a cada passo. Mover o mouse permite escolher um novo foco.

Use **Ctrl + roda para baixo** para ampliar a visão ao redor da região atual.
Depois, posicione o mouse sobre o outro lado da topologia e aproxime novamente.
Não é necessário reposicionar a região pelas barras de rolagem. A roda sem Ctrl
continua rolando a view. A faixa de zoom permanece entre 10% e 1000%.

## Revisão a partir do vídeo

A primeira implementação preservava o ponto sob o cursor na mesma posição da
tela. O vídeo enviado mostrou que a interação desejada era diferente: trazer
a região escolhida para o centro. A correção agora usa `centerOn()` com a
coordenada da cena escolhida no primeiro evento da sequência. O foco é guardado
para os passos seguintes; sem isso, depois da centralização, o mesmo pixel do
mouse já apontaria para outra região e cada passo deslocaria novamente a cena.

Também foi identificado um problema no ciclo de atualização do projeto:

1. O scroll altera a escala e salva o percentual no projeto.
2. A resposta HTTP e as notificações emitem a atualização do projeto.
3. `Topology._projectUpdatedSlot()` chama `GraphicsView.setSceneSize()`.
4. Essa função apagava a área local de navegação, mesmo quando as dimensões
   eram iguais. A view voltava a sofrer os limites de rolagem e o alinhamento
   automático do Qt, mudando novamente sua posição e a geometria das barras.

`setSceneSize()` agora ignora dimensões que já estão aplicadas. A área de
navegação só é limpa quando as dimensões realmente mudam ou ao limpar/trocar
um projeto. As confirmações de zoom deixam de desfazer a navegação e provocar
as alternâncias de geometria que causavam saltos e contribuíam para a borda
piscando. Ao terminar cada passo de zoom, o viewport também recebe um pedido
completo de repintura, para atualizar o canvas após a transformação.

## Implementação

`wheelEvent()` passa o foco escolhido para `scaleView()`. A ancoragem automática
do Qt fica temporariamente desativada durante a escala e a centralização, e
sua configuração anterior é restaurada ao final. O afastamento mantém um foco
central estável, evitando acumular arredondamentos das barras a cada passo.

Uma margem de navegação na view permite centralizar regiões nas bordas ou
em cenas pequenas. Ela não altera o retângulo da cena, as dimensões salvas do
projeto nem as posições dos dispositivos. Pedidos fora dos limites não alteram
a view nem geram atualização redundante do projeto. Os comandos de zoom que
não passam um foco explícito continuam com o caminho existente.

## Validação

Os testes usam eventos reais de roda no viewport Qt, pontos fora do centro,
cenas de 2000×1000 e 100×80, escalas iniciais de 20%, 100% e 500%, aproximação
e afastamento. A região deve permanecer no centro com tolerância de dois pixels
pela quantização das barras do Qt.

A regressão das confirmações do servidor reaplica as mesmas dimensões várias
vezes depois do zoom e verifica que a transformação, a área de navegação e a
geometria do viewport não mudam. Outro teste aproxima a região esquerda,
afasta até a região direita estar visível e então centraliza essa outra região,
sem manipular barras de rolagem. Também permanecem os testes dos limites,
rolagem sem Ctrl, percentual salvo, restauração da ancoragem e troca de tamanho.

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest -q
```

Resultado da revisão: **264 aprovados, 1 ignorado**, com o aviso preexistente
de `tarfile`. A geometria e a navegação foram verificadas na view Qt offscreen;
a confirmação visual do comportamento no ambiente desktop pode ser feita
repetindo o percurso do vídeo depois de reiniciar a GUI.
