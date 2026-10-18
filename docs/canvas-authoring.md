# Criação e edição dos elementos visuais

## Formas por arraste

Ative retângulo ou elipse, pressione no canvas e arraste até a dimensão desejada.
A prévia azul translúcida não é um desenho da topologia e não é exportada.
Soltar abre o editor de estilo existente, com preenchimento, cor, espessura,
tipo de borda e opção sem borda. Confirmar cria o desenho no servidor; cancelar
remove o rascunho sem enviar DELETE para um ID ainda não criado. Esc cancela o
arraste, e um gesto sem área não cria uma forma.

O retângulo normalizado permite desenhar nos quatro sentidos, em coordenadas
da cena, respeitando o zoom. O editor admite até 1.000.000 de unidades por eixo.
Dimensões fracionárias do arraste são preservadas quando não são alteradas no
editor. Os testes de gesto verificam prévia, geometria, cancelamento e formas
de 25.000 × 15.000 unidades.

## Containers: aparência e compatibilidade

A interface usa Container, Enter container, Rename container e Unpack container.
Os nomes de classes, IDs de ações e o tipo interno `group` permanecem estáveis
para preservar arquivos e integrações existentes; nomes dados pelo usuário não
são reescritos. Ctrl+G e Ctrl+Shift+G permanecem disponíveis.

O diálogo abre em General e tem uma aba Style. Três botões exclusivos, com
ícones e nomes acessíveis, escolhem retângulo, triângulo ou elipse. Há cores com
alfa para borda/fundo, espessura e estilos incluindo sem borda. O padrão é o
retângulo, fundo transparente e borda azul sólida.

O contorno de interação, seleção e detecção de saída/entrada acompanha o formato
escolhido. Ao mudar a forma, filhos cujos limites visuais ficam fora são
transladados para dentro, incluindo rótulos e desenhos. Não são escalados nem
removidos. Elementos que já cabem permanecem no lugar. Se um filho não couber
em nenhum ponto, o frame cresce proporcionalmente o necessário para acomodá-lo,
até o limite de dimensões suportado. Não é um algoritmo de distribuição sem
sobreposições: o objetivo é manter o conteúdo dentro e acessível.

A implementação usa o path convexo de retângulo, triângulo ou elipse. Uma busca
binária encontra um deslocamento suficiente na direção de um ponto interior,
com margem para arredondamentos das coordenadas enviadas ao servidor. A troca
pela aba Style faz a prévia com Apply; Cancel restaura também as posições dos
filhos e as dimensões originais. Carregar metadados existentes não executa uma
nova distribuição, preservando o layout salvo.

O retângulo mínimo de pintura exigido pelo Qt continua existindo internamente;
ele não é mais a área funcional das formas não retangulares. As quatro alças
permanecem nos cantos desse retângulo para permitir redimensionar o frame mesmo
onde não há preenchimento do triângulo/elipse. A regra anterior de não recortar
filhos nessas formas é mantida; o ajuste é geométrico, não uma ocultação.

O dicionário opcional `style` nos metadados SVG guarda forma, cores, espessura e
tipo de borda, com validação ao importar. Arquivos sem esse campo usam o padrão.
A duplicação copia o estilo. Nenhuma nova API de servidor é necessária.
Testes verificam exclusividade/acessibilidade dos ícones, valores padrões,
round-trip dos três formatos, encaixe dos filhos e alças em todos os cantos.
Suíte após essa etapa: 278 aprovados e 1 ignorado.

## Notas com tipografia na criação

Criar uma nota abre o editor com texto inicial selecionado, fonte/tamanho/cor
atuais e controles diretos de família, tamanho, negrito, itálico e sublinhado.
O seletor prioriza as famílias já usadas nos textos do projeto, depois famílias
comuns instaladas, e mantém disponíveis as demais fontes locais. Famílias de
projetos que não estejam instaladas ficam na lista; o Qt faz a substituição
local, sem incorporar arquivos de fonte nem instalar novas fontes.

A caixa de texto mostra a prévia da tipografia. O diálogo de fontes completo
continua disponível e sincroniza os controles. Cor e transparência usam o
seletor já existente. Confirmar uma nota não vazia cria o desenho; cancelar ou
confirmar conteúdo vazio descarta o rascunho. Família, tamanho e sublinhado são
preservados pelo SVG existente. Testes cobrem confirmação/cancelamento, padrões
e round-trip da tipografia.

## Imagens: dimensões iniciais e redimensionamento

Importar abre Image properties antes de criar o desenho. Largura/altura vêm
da imagem, com Keep aspect ratio marcado; é possível desmarcar para dimensões
independentes. Confirmar redimensiona mantendo o centro inicial, e cancelar não
adiciona a imagem nem envia criação ao servidor. Dimensões vão de 1 a 1.000.000.

Imagens selecionadas mostram quatro alças internas nos cantos. Arrastar perto
de uma borda ou canto redimensiona; mover pelo interior mantém a movimentação
normal. O bloqueio impede redimensionar. A proporção segue a escolha feita ao
importar. A transformação original do gesto serve de referência, incluindo
imagens dentro de containers ou com rotação, preservando o canto oposto.

O tamanho é salvo no SVG (width, height e viewBox), não apenas em uma escala
transitória do item. A preferência de proporção é um atributo opcional do SVG;
imagens antigas assumem proporção preservada. O renderer tem referência Python
explícita e é substituído antes de liberar o antigo. O conteúdo raster continua
embutido no SVG, sem depender do caminho do arquivo depois da importação.

Testes verificam cancelamento/aceitação da importação, dimensões após recarga,
proporção e tamanho livre, cantos superior esquerdo e inferior direito dentro
de um container, posição do canto oposto e persistência da escolha de proporção.

## Verificação final

Suíte completa: 289 aprovados e 1 ignorado, com o aviso preexistente de `tarfile`.
Os três diálogos foram renderizados e inspecionados em Qt offscreen. A avaliação
de uso no desktop deve incluir desenhos em diferentes níveis de zoom, importação
de imagens reais e a troca de forma de containers já preenchidos. Fontes não
são incorporadas: a aparência pode variar em sistemas sem a família original.

Na revisão visual, os seletores de cor ganharam texto contrastante e o fundo
sem preenchimento é explicitamente identificado como Transparent. Perder o
foco durante o desenho também cancela a prévia, evitando um fantasma órfão.

## Correções de legibilidade e bordas

Os campos de largura e altura de formas/imagens usam fundo branco, texto preto
e seleção azul, com estilo restrito a esses campos e seus editores internos.
A espessura da borda das formas aceita zero também na definição Qt Designer.
Espessura zero significa NoPen, em vez da linha cosmética de um pixel que o Qt
normalmente desenha com width=0. O container segue a mesma regra; destaques de
arraste continuam sendo indicações temporárias, independentes do estilo salvo.

## Edit container e Apply

O menu de contexto do canvas oferece Edit container somente enquanto houver
um container em edição. A ação também aparece na linha correspondente do
Topology Summary nesse estado, sem sair da edição para abrir as propriedades.
Os comandos anteriores de renomear e o duplo clique continuam disponíveis.

Ao editar um container existente, Apply mostra nome, dimensões e estilo no
canvas sem fechar o diálogo. Essa prévia é local: OK confirma e salva; Cancel
restaura os valores que existiam ao abrir, inclusive depois de Apply. A árvore
lateral acompanha a prévia e a restauração. O botão de Apply fica desabilitado
para um nome vazio e não é exibido na criação, onde ainda não há um container
existente para pré-visualizar. Testes cobrem a presença condicional da ação,
a prévia, a confirmação e a reversão.

## Imagens maiores que o limite do JSON

O erro “Maximum request body size 1048576 exceeded” se refere ao corpo JSON,
não à largura/altura desenhada. A imagem é embutida como base64 no SVG; reduzir
apenas suas dimensões visuais não reduz esses bytes.

Quando o corpo serializado alcança 900.000 bytes, o cliente salva o SVG completo
em um arquivo temporário e o envia pelo endpoint nativo de streaming
`POST /projects/{id}/files/project-files/images/{sha256}.svg`. Somente depois
manda o POST/PUT do desenho com o nome desse recurso, um JSON pequeno. Isso
preserva os pixels, as dimensões e os metadados, sem compressão com perdas nem
alteração no limite global do servidor. O arquivo temporário local é removido
após o upload, inclusive em caso de falha. O fluxo existente de POST antes de
PUT continua valendo.

A API de arquivos não cria diretórios. Em projetos vazios, o cliente inicializa
o armazenamento nativo com um desenho transparente de 1×1, removido após o
upload, antes de concluir o desenho real. Arquivos obsoletos seguem a limpeza
normal de imagens do servidor. Não é uma nova API de containers nem uma mudança
no servidor.

O conteúdo raster também é envolvido por um elemento SVG `g`. Isso evita que
a otimização de imagens simples do servidor extraia apenas o bitmap e regenere
suas dimensões originais, perdendo as dimensões e os metadados do desenho. O SVG
é serializado com namespace padrão para continuar compatível com o leitor v2.

Teste integrado (somente contra um servidor descartável separado):

```bash
python3 scripts/check_large_drawing.py --server http://127.0.0.1:3099
```

Validado em GNS3 server 2.2.61 com pixels aleatórios sem perdas e SVG maior que
1 MiB: upload por arquivo, POST/PUT compactos, pixels intactos, dimensões após
recarga e exportação do recurso. Ao final só há o desenho real no projeto; o
projeto descartável é excluído. A suíte completa terminou com 297 aprovados e
1 ignorado, mantendo o aviso anterior de `tarfile`.

A cobertura do diálogo também aciona o botão Apply real e verifica os valores
enviados à prévia, sem aceitar ou fechar o diálogo.

## Fluidez do redimensionamento de imagens

O gesto agora usa uma transformação temporária do item, reutilizando o mesmo
renderer e os pixels já decodificados. Reconstruir e decodificar o SVG/base64 a
cada evento do mouse causava travamentos, especialmente em imagens grandes.
Ao soltar, a transformação temporária é incorporada às dimensões SVG uma única
vez, o transform original é restaurado e a view salva o resultado. Não há uma
segunda gravação redundante disparada pelo próprio item.

Nos cantos com proporção bloqueada, o movimento é projetado na diagonal da
proporção original, evitando a troca abrupta entre eixo dominante horizontal e
vertical. O cálculo usa a transformação original do gesto para preservar o
canto oposto, inclusive com rotação e dentro de containers. A preferência de
proporção e o tamanho livre continuam disponíveis.

A regressão percorre vários eventos nos quatro cantos de uma imagem rotacionada:
verifica que o renderer é o mesmo durante o arraste, que não há nova decodificação
nesse período e que ela ocorre uma vez na soltura. A suíte completa desta revisão
terminou com **304 aprovados e 1 ignorado**, com o aviso preexistente de `tarfile`.

## Navegação e seleção com o mouse

A ferramenta **Hand** é o modo inicial. Arrastar uma região vazia com o botão
esquerdo desloca a view; o cursor passa de mão aberta para mão fechada durante o
arraste. Arrastar sobre um elemento continua movendo o próprio elemento.
Os botões Hand e Selection na barra superior indicam o modo atual e oferecem
descrições no tooltip e na barra de status. Clicar no vazio com o esquerdo ativa
Hand; iniciar um gesto com o direito ativa Selection.

A seleção com o direito usa sempre um retângulo, inclusive sobre dispositivos.
Um clique direito sem arraste abre o menu tradicional do item sob o cursor;
a seleção de área continua exigindo arraste. Ctrl preserva a seleção anterior ao
adicionar outro retângulo. Ao soltar com elementos selecionados, o menu de ações
abre e oferece **Create container**, reutilizando o diálogo e a validação de
parentesco existentes. A seleção de filhos de um container fechado é promovida
ao container, preservando sua hierarquia.

A criação pelo botão Container elements mantém a exceção de selecionar com o
esquerdo antes de abrir o diálogo. Desenho de formas, links e redimensionamento
continuam usando seus gestos próprios. Shift+esquerdo e botão do meio também
continuam disponíveis para navegar.

Tecnicamente, o retângulo é um QRubberBand no viewport. Seu polígono é convertido
para coordenadas da cena para consultar as formas dos itens, respeitando zoom e
scroll. O menu é aberto apenas ao soltar; o evento nativo de menu do mouse é
consumido para evitar uma segunda abertura ou seleção pontual involuntária.
A navegação altera somente as barras da view; não modifica posições exportadas.

O campo **Border width** da aba Style do container tem fundo branco e texto
preto, com estilo restrito ao campo e ao editor interno. Isso mantém o valor
legível em temas escuros sem alterar o restante do diálogo. A verificação
automatizada de contraste dos campos numéricos também cobre esse controle.

Validação desta etapa: suíte completa com 308 testes aprovados e um ignorado.

## Menus e containers aninhados

O clique direito sem arraste volta a abrir as ações do dispositivo ou container
sob o cursor. Se o item já pertencia à seleção, ela é preservada. Durante a
edição de um container, o menu oferece **Edit** como primeira ação para abrir
seus atributos; clicar numa área vazia durante essa edição também permite
acessar o menu do container ativo. Arrastar o direito mantém a seleção por
retângulo e o menu da seleção ao soltar. O evento nativo de menu continua sendo
consumido para evitar uma abertura duplicada.

O duplo clique consulta as formas dos containers visíveis sob o cursor e
prioriza o descendente em relação ao seu ancestral. Esse gesto é tratado na
view e consumido antes do encaminhamento aos itens, evitando que o container
externo intercepte a entrada no interno. As camadas persistidas não são
alteradas. A movimentação simples mantém a regra de mover o container fechado
como uma unidade; entrar no interno abre também seus ancestrais.

Os testes cobrem menu em área vazia durante edição, primeira ação Edit,
clique direito sobre dispositivo, seleção por arraste e duplo clique em
container aninhado com ancestral aberto ou fechado, inclusive quando o interno
tem um valor de camada menor.
