# Duplicação de grupos: filhos, links e nomes

## O problema e a reprodução

Ao duplicar um grupo, o servidor criava os dispositivos, mas a GUI podia deixar
as cópias fora do novo grupo e sem as conexões internas. Isso acontecia tanto
pelo canvas quanto pelo Topology Summary, que chama a mesma operação.

A reconstrução da árvore já existia em `CanvasGroups.duplicate()`. Ela espera
os IDs de todos os dispositivos copiados, associa cada item ao pai copiado e
recria os links internos usando o mapa de IDs e os números de adapter/porta.
Se uma resposta não chega ao callback, essa etapa final fica esperando.

Os logs locais mostraram pedidos de duplicação e eventos `node.created`, mas
nem todas as respostas apareciam no processamento HTTP da GUI. Reproduzi isso
em um projeto descartável com três Ethernet switches no servidor 2.2.61, usando
o `Node.duplicate()` e o transporte HTTP Qt reais. O servidor respondia aos três
pedidos com 201, mas o cliente processava apenas uma parte deles. Ao manter
referências explícitas aos objetos de resposta, todos os callbacks chegaram e
a cópia passou a conter os dispositivos e a conexão interna.

## Causa e correção

O caminho da duplicação envia pedidos com `timeout=None` e `showProgress=False`.
Nessa combinação, não há timer nem diálogo de progresso segurando o wrapper
Python do `QNetworkReply`. Os callbacks conectados aos sinais formavam ciclos
que o coletor do Python podia recolher antes do sinal `finished`. O objeto
nativo do Qt continuar pertencendo ao gerenciador de rede não bastava para
preservar os callbacks Python.

O `HTTPClient` agora mantém um conjunto de respostas em andamento. A referência
é retirada no início do processamento de `finished`; durante o restante desse
processamento, o próprio argumento da função mantém o objeto vivo. Isso também
libera a referência quando uma requisição termina com erro de rede. Não foi
necessário serializar a duplicação nem modificar o servidor.

Com os callbacks entregues, o código existente consegue concluir a associação
dos filhos ao novo grupo e recriar os links entre as cópias. A árvore original
permanece intacta. Links para dispositivos que ficaram fora da seleção não são
copiados: o novo grupo recebe suas conexões internas, sem se conectar
automaticamente aos dispositivos originais.

## Nome da cópia

O grupo selecionado recebe o prefixo `Copy of `: `LAN 1` vira `Copy of LAN 1`.
Se esse nome já existir, a próxima cópia recebe `Copy 2 of LAN 1`, e assim por
diante. O nome original permanece igual. Os grupos aninhados mantêm seus nomes,
porque continuam identificados pela hierarquia dentro do novo grupo raiz.
O novo nome também é salvo nos metadados do grupo e aparece no Topology Summary.

## Testes e o que faltava na cobertura anterior

O teste HTTP novo usa wrappers e sinais Qt reais, dispara três pedidos sem
timeout/progresso, força `gc.collect()` antes das respostas e conclui os pedidos
fora de ordem. Ele verifica que todos os callbacks chegam e que o conjunto de
respostas em andamento termina vazio. Os testes de grupo também exercitam a
ação real do menu Topology Summary, além da entrada pelo canvas: verificam pais,
posições locais, nome, ligação interna e manutenção da árvore após `restore()`.

O script `scripts/check_canvas_groups.py` deixou de responder à duplicação por
um adapter HTTP síncrono. Ele usa o hook real de `Node.duplicate()` e o cliente
HTTP Qt, força a coleta de lixo e aguarda os callbacks pelo event loop. Os modelos
de dispositivo ainda são adapters leves; o teste não inicia emuladores nem uma
sessão desktop completa. A troca do transporte é importante: o adapter anterior
entregava todos os callbacks imediatamente e escondia essa falha de ciclo de vida.

Validação desta correção:

- Suíte completa: **226 aprovados, 1 ignorado**. Permanece o aviso já existente
  de depreciação de `tarfile` no teste de atualização.
- Servidor isolado 2.2.61: seis dispositivos após a cópia; três pertencem à
  árvore copiada; duas conexões no projeto, sendo uma interna à cópia.
- Exportação/importação: quatro grupos aninhados, dimensões preservadas,
  referências remapeadas e filhos associados aos respectivos grupos.
- Exclusão recursiva e limpeza dos projetos/templates descartáveis concluídas.

Para repetir, execute a suíte e, com um servidor de testes separado, o script:

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest -q
python3 scripts/check_canvas_groups.py --server http://127.0.0.1:3099
```

Essa correção resolve a entrega das respostas no cliente. A proposta de um
modelo nativo de grupos no servidor continua em
[group-server-integration.md](group-server-integration.md).
