# Grupos no canvas: implementação, limites da API e próximo passo no servidor

## O que está implementado

O grupo é um item do canvas com nome, posição, largura e altura. Dispositivos,
notas, formas, imagens e outros grupos são filhos reais desse item no Qt. Isso
permite mover o contêiner sem alterar as posições locais dos filhos. A moldura
tem tamanho fixo, pode ser redimensionada pelos cantos e recorta o conteúdo que
ultrapassa a borda. As guias centrais, o destaque de destino durante um arraste
e o estado de edição são apenas estado da interface.

`GroupItem`, em `gns3/items/group_item.py`, implementa o item gráfico, o recorte,
a apresentação e a serialização do grupo. `CanvasGroups`, em
`gns3/canvas_groups.py`, coordena pertencimento, edição, cópia, restauração e
alinhamento. O `GraphicsView` encaminha os eventos de mouse e de drag-and-drop.
A árvore do `TopologySummaryView` usa os mesmos objetos e operações do canvas;
não mantém uma segunda hierarquia independente.

A janela `GroupPropertiesDialog` compartilha nome e dimensões entre criação e
edição. As dimensões úteis iniciais têm 30% a mais que o retângulo necessário:
15% de margem em cada lado, com uma faixa adicional de 24 unidades para o título.
Os campos de largura e altura têm fundo branco e texto preto, com estilo
restrito a esses dois controles para não alterar o tema da aplicação.

Quando um template de dispositivo é arrastado sobre um grupo, o destino visível
mais à frente recebe uma borda mais grossa e as duas guias centrais. Um grupo
interno tem preferência sobre seu pai na área em que está visível. Grupos
travados não recebem a inserção. Ao sair da área ou soltar o template, o destaque
e as guias desaparecem. Arrastar um arquivo de projeto não ativa esse estado.

O pedido de criação do dispositivo continua indo ao servidor. A GUI guarda o
grupo escolhido e a posição local do drop, espera a resposta com o `node_id` e
só então adota aquele dispositivo. Isso evita associar por engano outro nó que
chegue por WebSocket. Se o grupo se mover durante a espera, a posição local é
preservada. Se o grupo tiver sido removido ou o projeto tiver mudado, o callback
não tenta reconstruir o contêiner antigo.

## Por que apareceu SVG nesta implementação

O motivo não foi uma limitação de desenho do Qt. A GUI já suporta uma hierarquia
gráfica com `setParentItem`; foi isso que usamos para a interação. O problema
está no contrato de persistência.

No GNS3 2.2.61 analisado, quem grava o projeto, produz os arquivos portáteis e
restaura snapshots é o servidor. Os objetos da API são nós, links e desenhos.
Os schemas aceitam coordenadas e SVG para um desenho, mas não um grupo nativo,
`parent_group_id` ou uma lista de filhos. Acrescentar esses campos somente na
GUI não faria o servidor validá-los, armazená-los e reescrevê-los corretamente.

Por isso cada grupo ocupa um registro de desenho e carrega JSON versionado em
`<metadata id="gns3-canvas-group">` dentro do SVG. Esse JSON contém nome,
identidade, origem, dimensões e referências aos filhos com coordenadas locais.
Os demais registros de nós e desenhos continuam existindo. Não transformamos
os dispositivos em uma imagem, nem duplicamos suas configurações no SVG.

O servidor guarda o desenho e exporta o SVG sem precisar entender essa extensão.
Na GUI modificada, o desenho volta a ser um `GroupItem`. Em uma GUI que não
conhece a extensão, ele tem apenas a representação de um desenho. SVGs maiores
podem ser guardados em arquivos de imagens do próprio projeto pelo servidor;
esse é um comportamento nativo, não um arquivo auxiliar criado fora do projeto.

Esse transporte permitiu testar a interação e manter projetos portáteis usando
o servidor instalado. Ele não equivale a acrescentar grupos ao modelo do
servidor. A arquitetura definitiva deveria remover essa responsabilidade dos
metadados de imagem.

## Onde a separação entre GUI e servidor pesou no desenvolvimento

### Persistência e propriedade do arquivo

Não bastava adicionar um `groups` ao JSON salvo localmente. O servidor pode ser
remoto e regrava o arquivo de projeto. A GUI precisou usar uma API já existente
para que o grupo sobrevivesse ao fechamento e à exportação. Isso levou ao
transporte por desenhos descrito acima.

A primeira experiência mantinha associações apenas na sessão. Isso foi uma
decisão de escopo da primeira implementação, não uma impossibilidade técnica
comprovada no servidor. A necessidade de grupos como elementos persistentes
levou à revisão desse desenho.

### Coordenadas locais e coordenadas da API

Um filho usa coordenadas relativas ao pai no Qt. A API 2.2 espera coordenadas da
cena. A GUI passou a converter essas posições em `Node.setGraphics`, nos
callbacks de `NodeItem` e na serialização/atualização de `DrawingItem`.

Essa conversão é necessária nos dois sentidos. Sem ela, uma resposta HTTP com
coordenadas absolutas deslocaria novamente um dispositivo que já tem um pai.
Também foi necessário considerar a soma das camadas dos ancestrais para os
links e preservar as coordenadas ao reagrupar, desagrupar e redimensionar pelo
canto superior/esquerdo. O SVG do grupo mantém a posição local, enquanto a API
mantém uma representação absoluta de compatibilidade. Há, portanto, duas
representações que a GUI precisa manter coerentes.

### Ordem de criação dos desenhos e o erro 404 informado

A captura enviada mostra uma resposta Not Found para
`/v2/projects/<project_id>/drawings/<drawing_id>`. Ela não contém o método HTTP,
o corpo da resposta nem o histórico das requisições. Não permite afirmar que o
servidor precisa de uma API de grupos para resolver essa ocorrência.

O caminho de criação/duplicação tinha uma corrida compatível com esse erro:

1. A GUI gerava o UUID de um desenho e enviava `POST /drawings`.
2. A cópia continuava sendo montada e o salvamento disparava `PUT /drawings/UUID`.
3. Se o PUT chegasse antes da conclusão do POST, o servidor ainda não conhecia
   aquele UUID e podia responder 404.

Isso é um defeito de ordenação do cliente, não ausência da rota de desenhos.
A revisão atual registra se o desenho foi confirmado pelo servidor, mantém
edições pendentes enquanto o POST está em voo e envia a atualização somente
após a confirmação. Um reconhecimento antigo de criação não sobrescreve as
edições feitas durante a espera. Se o desenho for excluído nesse intervalo, a
GUI espera a criação terminar e remove a cópia do servidor.

A correção foi feita no ciclo de vida de `DrawingItem`, porque as cópias de
formas e notas têm a mesma dependência, não apenas o grupo. A análise do código
e os testes reproduzem a condição de corrida; a causa exata da ocorrência da
captura continua sendo uma hipótese, pois não temos o log daquela sessão.
Se o erro persistir, o próximo dado útil é o log `--debug` com método, ordem e
resultado dos POSTs/PUTs, além da versão do servidor. Um projeto fechado ou um
desenho removido por outro cliente também pode produzir um 404.

### Duplicação distribuída e operações parciais

O servidor oferece duplicação de um nó. Não oferece, neste contrato, uma
operação de cópia de grupo que devolva toda a nova árvore. A GUI precisa esperar
os novos `node_id`, criar os desenhos, remontar os pais e recriar os links cujas
duas pontas pertenciam ao conjunto original. Conexões para dispositivos externos
não são copiadas para a nova árvore.

Foi acrescentado um callback opcional à duplicação de nó e à criação por template
para associar cada resposta ao pedido correto. Eventos WebSocket podem chegar
antes ou depois da resposta HTTP; a GUI procura o objeto pelo ID para não
criá-lo duas vezes.

O rollback atual de cópia trata falhas de duplicação de dispositivos e solicita
a remoção das cópias já feitas. Não é uma transação de grupo: falhas posteriores
de desenho, link, limpeza ou comunicação com um compute podem deixar trabalho
parcial. Apenas uma operação coordenada no servidor pode definir e acompanhar
esse resultado de forma confiável para todos os clientes.

### Importação e Save As regeneram identidades

Na importação portátil, o servidor regenera IDs de nós, links e desenhos. Ele
reescreve suas referências conhecidas, mas não interpreta as referências
escondidas no SVG do grupo. A hierarquia ficaria apontando para os IDs antigos.

A GUI detecta que o próprio grupo recebeu um novo ID e tenta recuperar seus
filhos por identidades persistidas nos desenhos/grupos e pelo nome dos nós.
Depois grava referências aos IDs atuais. Esse fallback tem limites: metadados
antigos, nomes alterados fora desse fluxo ou referências ambíguas podem impedir
a recuperação. Na implementação nativa, o importador deve remapear as relações
de pai pelo mesmo mapa de IDs usado para o restante do projeto, sem depender
de nomes.

### Exclusão, bloqueios e múltiplos clientes

Apagar o registro de desenho de um grupo na API atual não exclui seus filhos.
É a GUI que calcula o conjunto e chama os endpoints individuais. Isso funciona
pela interface modificada, mas outro cliente pode apagar ou alterar o desenho
sem executar a mesma operação hierárquica.

A GUI verifica ciclos e propriedade única antes de restaurar a árvore e observa
notificações de desenhos. Revisões locais ajudam a descartar reconhecimentos
antigos. Ainda assim, o servidor não valida a hierarquia, não arbitra edições
concorrentes e não oferece uma revisão de grupo para todos os clientes.
Clientes antigos também podem editar um desenho sem preservar os metadados.

### O que os testes anteriores não cobriam

Houve acesso a um servidor GNS3 2.2.61 real para testar persistência, nós de tipo
Ethernet switch, links, cópia, exportação e importação. Esses testes não executam
todos os simuladores e não comprovam comportamento equivalente em outro ramo
ou versão da API.

O adaptador HTTP do primeiro teste integrado executava cada pedido de forma
síncrona. Por isso, ele confirmou o formato e o remapeamento de IDs, mas não
exercitou PUTs antes da conclusão dos POSTs. A revisão atual acrescenta testes
com callbacks atrasados e segura os POSTs de desenhos no teste integrado;
qualquer PUT prematuro alcançaria o servidor real e falharia. As confirmações
também são entregues em ordem inversa. Essa distinção deve constar do PR para
não apresentar a validação anterior como cobertura de concorrência completa.

## Proposta para suporte nativo no servidor

As estruturas e rotas abaixo são uma proposta para discussão, não endpoints já
implementados. A referência analisada é o contrato 2.2.61. Antes de codificar no
servidor, vale alinhar com os mantenedores a versão de destino e o ramo adequado.

### Modelo e arquivo

Usaria um recurso de layout `Group`, separado de `Drawing`, sem envolvê-lo na
execução dos emuladores. Cada elemento teria no máximo um `parent_group_id`.
O pai seria a fonte de verdade; a lista de filhos seria obtida pelo servidor,
evitaria manter referências de pertencimento duplicadas em dois lugares.

```json
{
  "topology": {
    "groups": [
      {
        "group_id": "uuid-do-grupo",
        "parent_group_id": null,
        "name": "LAN 1",
        "x": 100,
        "y": 80,
        "z": 0,
        "width": 600,
        "height": 400,
        "locked": false,
        "clip_children": true
      }
    ],
    "nodes": [
      {"node_id": "uuid-do-no", "parent_group_id": "uuid-do-grupo", "x": 40, "y": 70}
    ],
    "drawings": [],
    "links": []
  }
}
```

Esse exemplo omite os demais campos de nó/projeto. `x`, `y` e `z` seriam relativos
ao pai; `null` identifica a raiz. Coordenadas podem ser fracionárias, conforme o
schema acordado. O servidor validaria que pai e filho pertencem ao mesmo
projeto, que o pai existe, que a árvore não tem ciclos e que as dimensões são
válidas. Recorte é uma propriedade de apresentação: não deve apagar ou limitar
as coordenadas dos filhos.

Os links continuariam sendo conexões entre IDs de nós, inclusive entre grupos.
Sua geometria na GUI usaria a transformação acumulada dos pais. Agrupar não
precisa mudar a topologia de rede nem criar outra camada de emulação.

### Contrato de operações

| Operação proposta | Responsabilidade do servidor |
| --- | --- |
| Criar/editar grupo | Persistir nome, quadro, pai e revisão; validar a hierarquia. |
| Agrupar/reparentear em lote | Mudar o pai dos elementos selecionados e converter suas posições para preservar a aparência. |
| Mover/redimensionar | Atualizar um contêiner; redimensionar não escala filhos. Manter a regra escolhida de compensação da origem ao arrastar cantos. |
| Desagrupar | Promover filhos ao pai anterior, preservar posições na cena e remover apenas o contêiner. |
| Excluir recursivamente | Validar bloqueios antes de iniciar e acompanhar a remoção de nós, desenhos e links incidentes. |
| Duplicar recursivamente | Gerar o mapa antigo→novo, copiar recursos, remontar pais e links internos e devolver o resultado da operação. |
| Criar nó em grupo | Receber pai e posição local no mesmo pedido de template/nó, sem um segundo pedido posterior para adotar o dispositivo. |

Um desenho possível seria `POST/GET /projects/{id}/groups`,
`PATCH /projects/{id}/groups/{group_id}` e comandos de `duplicate`, `ungroup` e
`delete` com política explícita. A escolha dos verbos e caminhos deve seguir
as convenções do ramo de destino. Pedidos de criação e reparentamento deveriam
ser idempotentes ou aceitar um identificador de operação para não duplicar
recursos quando houver timeout e repetição.

Para a concorrência, usaria uma revisão por grupo ou por documento e pedidos
condicionados à revisão esperada. O servidor rejeitaria uma alteração baseada
em estado antigo e publicaria eventos com revisão e referências suficientes
para todos os clientes atualizarem o mesmo modelo. A transição entre pais deve
ser observável como uma operação consistente, não como uma sequência ambígua
de eventos desconectados.

Duplicar uma árvore com discos de VM e computes remotos pode levar tempo. Nesse
caso, prefiro um job com ID, estado e resultado, inclusive limpeza de falhas.
Uma transação do JSON de layout não desfaz automaticamente cópias de arquivos,
processos e recursos de emulação. O servidor precisa registrar as etapas e
executar a limpeza compensatória, informando se a operação terminou ou ficou
parcial. Não prometeria atomicidade total sem definir esse comportamento.

### Onde trabalhar no repositório do servidor

Pontos de entrada conferidos no GNS3 2.2.61:

- `gns3server/controller/project.py`: coleções de nós/desenhos, carregamento,
  gravação, duplicação e exclusão. Aqui entraria a coleção de grupos e o
  coordenador das operações de hierarquia.
- `gns3server/controller/drawing.py`, `node.py`, `link.py`: separar o novo
  recurso de layout e revisar conversões/serialização, mantendo a execução de
  dispositivos independente do pertencimento visual.
- `gns3server/schemas/topology.py`, `drawing.py`, `node.py` e schemas de template:
  revisar formato, campos de pai e validação. Acrescentar um schema de grupo.
- `gns3server/handlers/api/controller/`: criar handlers de grupos e ajustar a
  criação por template para aceitar pertencimento no mesmo pedido.
- `gns3server/controller/import_project.py`, `export_project.py` e `topology.py`:
  atualizar a revisão do formato, remapear todos os pais ao importar/duplicar,
  incluir grupos em snapshots e manter importação de projetos antigos.
- Testes de controller, handlers, schemas e import/export: cobrir árvores
  profundas, ciclos, pai inexistente, falha de clone em compute, rollback,
  bloqueios, exclusão com links externos e dois clientes concorrentes.

O repositório é [GNS3/gns3-server](https://github.com/GNS3/gns3-server).
As referências verificadas da versão usada são o
[schema de desenho](https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/schemas/drawing.py),
o [modelo de projeto](https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/controller/project.py)
e o [importador](https://github.com/GNS3/gns3-server/blob/v2.2.61/gns3server/controller/import_project.py).

### Migração da GUI e compatibilidade

Depois de acordar o modelo, o servidor deveria anunciar uma capacidade/versionamento
que permita à GUI escolher explicitamente o contrato nativo. Eu manteria a
representação Qt e os controles desta experiência, mas substituiria o transporte
SVG por objetos de grupo e pedidos próprios de hierarquia.

Projetos sem grupos ganhariam pais `null`. Para o protótipo SVG, um importador
conhecido validaria os metadados, criaria grupos nativos, converteria/remapearia
as relações e só removeria os desenhos de transporte depois do sucesso. Uma
exportação legada poderia achatar o layout ou usar uma extensão documentada;
essa política precisa ficar explícita para não perder silenciosamente os grupos.

Separaria o trabalho em PRs revisáveis: primeiro schema/modelo/migração e testes
de arquivo, depois operações e eventos do servidor, por fim a GUI usando a nova
API. O PR desta experiência pode apresentar a interação pronta e os testes,
mas deve expor a limitação do transporte e pedir acordo sobre o contrato nativo.
Não é necessário afirmar que o erro 404 só pode ser corrigido no backend.

## Resultado da validação desta revisão

A suíte terminou com **223 testes aprovados e 1 ignorado**. O aviso existente é
uma depreciação de `tarfile` no teste de atualização da aplicação. O teste de
integração passou no servidor 2.2.61: criou um template Ethernet switch
descartável, inseriu um novo dispositivo em um grupo pelo fluxo de drop,
terminou com seis dispositivos e duas conexões após a duplicação, confirmou desenhos com
POSTs atrasados, exportou/importou quatro grupos aninhados e excluiu uma das
árvores. Projetos e template de teste foram removidos. Isso não valida todos
os emuladores nem substitui o log da sessão em que a captura foi produzida.

### Duplicação: perda de callbacks no cliente

Uma revisão posterior reproduziu outro problema: o servidor criava os novos
dispositivos, mas algumas respostas HTTP perdiam seus callbacks Python antes de
terminar. A GUI esperava esses callbacks para associar os filhos e recriar os
links. O cliente HTTP agora mantém referências às respostas até `finished`.
Isso foi corrigido sem mudança no contrato do servidor; a investigação e a
validação com HTTP Qt real estão em
[group-duplication-fix.md](group-duplication-fix.md).
