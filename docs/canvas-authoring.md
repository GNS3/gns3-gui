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

A forma é decorativa: coordenadas, área de interação, detecção de saída/entrada
e alças dos quatro cantos continuam retangulares. Triângulos e elipses não
recortam filhos, evitando que uma mudança de forma esconda dispositivos. O
retângulo conserva seu recorte anterior. Redimensionar o container não move
nem escala os filhos. Destaques temporários azul/vermelho prevalecem durante
arrastes e não são persistidos.

O dicionário opcional `style` nos metadados SVG guarda forma, cores, espessura e
tipo de borda, com validação ao importar. Arquivos sem esse campo usam o padrão.
A duplicação copia o estilo. Nenhuma nova API de servidor é necessária.
Testes verificam exclusividade/acessibilidade dos ícones, valores padrões,
round-trip dos três formatos, filhos sem deslocamento e alças em todos os cantos.
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
