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
