#Relatto dev guides
Esse arquivo contem padrões a serem seguidos por todos os desenvolvedores do relatto.

## Branching
Semre ao se desenvolver alguma coisa, deve-se usar as sguintes convenções.

`ref = conjunto de letras que descreve uma determinada funcionalidade`

Exemploes:
`fix/ordem-topicos-pagina-empresa`

* `feat/ref` - Features novas a serem adicionadas no relatto.
* `fix/ref` - Correção de bugs.
* `rfc/ref` - Refactoring de código.
* `wip/ref` - Working In Progress, uma funcionalidade/correção/refact fora do escopo, partindo de uma iniciativa dos desenvolvedores e que pode demandar um tempo, a qual não possui deadline.

## Deploy para a produção.
Para uam determinada funcionaldiade/correçao/melhoria chegar a produção, ela deve seguir o seguinte flow:

* Criação da branch da funcionalidade/correção/melhoria a partir da branch `master`.
* Deploy no `nightly`, e esperar validação do P.O.
* Depois da validação do P.O, fazer merge da funcionalidade/correção/melhoria direto para a `master`.
* Após a validação em produção, apagar a branch da funcionalidade/correção/melhoria usando ` git branch -d branchname`.

## TODO:
* PEP-8-ficar o back-end.
* WIP: Criar uma API no back-end.
* WIP: Ações do relatto sem refresh.
* Criar padrões para o JavaScript.