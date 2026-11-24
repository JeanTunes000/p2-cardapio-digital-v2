# Cardápio Digital — Mini-SaaS (P2)

Evolução do projeto da P1 em Django para um Mini-SaaS multi-organização com perfis de acesso, API REST (DRF), dashboard gerencial, exportação CSV e testes automatizados.

## Como executar

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Roteiro de Isolamento Multi-tenant Verificado
- Usuário da Organização A visualiza apenas pratos, combos, mesas e comandas da Organização A.
- Tentativa de acessar ID de recurso da Organização B via URL ou API retorna `404 Not Found`.
- Criação de registros associa automaticamente `organizacao = request.user.perfil.organizacao`.
- Formulários e selects exibem exclusivamente registros da organização do usuário logado.
- Restrições de unicidade (`numero` da mesa por organização) permitem números iguais em organizações distintas.
