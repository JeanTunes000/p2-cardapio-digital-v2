# Melhorias Pós-P1 (Preparação para P2)

1. **Isolamento Multi-organização (Multi-tenant):** Na P1, todos os registros (`Prato`, `Combo`, `Mesa`, `Comanda`, `Item`) eram globais. Para a P2, introduzir o modelo `Organizacao`, base abstrata `DaOrganizacao` e `Perfil` vinculado ao `User`, filtrando todas as consultas e formulários pela organização do usuário logado.
2. **Controle de Acesso e Papéis:** Proteger as rotas com autenticação e diferenciar permissões entre `admin` e `operador`, incluindo tratamento seguro para superusuários sem `Perfil`.
3. **Centralização de Regras de Negócio e API REST (DRF):** Evitar duplicação de validação entre formulário HTML e API JSON, expondo os recursos principais via Django REST Framework sob `/api/` com filtro automático por organização.
4. **Otimização de Consultas (N+1) e Integridade de Templates:** Aplicar `select_related` ao percorrer itens de comandas (`prato` e `combo`) e corrigir a estrutura HTML duplicada em `comanda.html` ao herdar de `base.html`.
5. **Dashboard Gerencial e Relatórios:** Criar consultas agregadas (`aggregate` e `annotate`), filtro por período validado (`PeriodoForm`), gráfico com Chart.js via `json_script`, exportação CSV e testes automatizados.
