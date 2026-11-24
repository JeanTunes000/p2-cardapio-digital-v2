# Relatório P1 — Features adicionais

## Feature 1 — Busca e filtro na listagem

Na página de listagem de pratos, foi implementada uma busca pelo nome do prato e um filtro por categoria. A busca utiliza `request.GET.get('q')` e `nome__icontains`, enquanto o filtro utiliza `request.GET.get('categoria')` e o campo `categoria` do modelo. Os dois filtros podem ser usados separadamente ou em conjunto. A escolha foi feita porque o nome identifica diretamente o prato e a categoria facilita a navegação pelo cardápio.

## Feature 2 — Validação customizada

No cadastro de pratos, foi implementada uma validação no `PratoForm` para impedir que o preço seja zero ou negativo. A regra foi escolhida porque um prato não pode ser cadastrado com preço zero ou negativo para a operação do restaurante. Quando a regra é violada, o formulário apresenta a mensagem de erro ao usuário.
