from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from .models import Organizacao, Perfil, Prato, Mesa, Comanda, Item


class CardapioP2TestCase(TestCase):
    def setUp(self):
        self.org_a = Organizacao.objects.create(nome='Restaurante Alpha')
        self.org_b = Organizacao.objects.create(nome='Restaurante Beta')

        self.admin_a = User.objects.create_user(username='admin_a', password='123')
        Perfil.objects.create(usuario=self.admin_a, organizacao=self.org_a, papel='admin')

        self.operador_a = User.objects.create_user(username='op_a', password='123')
        Perfil.objects.create(usuario=self.operador_a, organizacao=self.org_a, papel='operador')

        self.admin_b = User.objects.create_user(username='admin_b', password='123')
        Perfil.objects.create(usuario=self.admin_b, organizacao=self.org_b, papel='admin')

        self.prato_a = Prato.objects.create(
            organizacao=self.org_a,
            nome='Feijoada Alpha',
            descricao='Completa',
            preco=Decimal('45.00'),
            categoria='PRINCIPAL',
        )
        self.prato_b = Prato.objects.create(
            organizacao=self.org_b,
            nome='Moqueca Beta',
            descricao='Tradicional',
            preco=Decimal('60.00'),
            categoria='PRINCIPAL',
        )

        self.mesa_a = Mesa.objects.create(organizacao=self.org_a, numero=1)
        self.mesa_b = Mesa.objects.create(organizacao=self.org_b, numero=1)

        self.comanda_a = Comanda.objects.create(organizacao=self.org_a, mesa=self.mesa_a, status='FECHADA')
        Item.objects.create(organizacao=self.org_a, comanda=self.comanda_a, prato=self.prato_a, quantidade=2)

        self.comanda_b = Comanda.objects.create(organizacao=self.org_b, mesa=self.mesa_b, status='ABERTA')
        Item.objects.create(organizacao=self.org_b, comanda=self.comanda_b, prato=self.prato_b, quantidade=3)

    def test_isolamento_lista_pratos_e_mesa_outra_org(self):
        self.client.force_login(self.admin_a)
        resp = self.client.get(reverse('lista_pratos'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Feijoada Alpha')
        self.assertNotContains(resp, 'Moqueca Beta')

        resp_404 = self.client.get(reverse('abrir_comanda', args=[self.mesa_b.id]))
        self.assertEqual(resp_404.status_code, 404)

    def test_dashboard_totais_e_filtro_periodo(self):
        self.client.force_login(self.admin_a)
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['kpis']['total_comandas'], 1)
        self.assertEqual(resp.context['kpis']['faturamento_total'], Decimal('90.00'))

        # Período futuro sem dados não gera erro
        amanha = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        resp_vazio = self.client.get(reverse('dashboard'), {'inicio': amanha})
        self.assertEqual(resp_vazio.status_code, 200)
        self.assertEqual(resp_vazio.context['kpis']['total_comandas'], 0)

        # Data inválida na URL não gera erro 500
        resp_invalido = self.client.get(reverse('dashboard'), {'inicio': 'abc'})
        self.assertEqual(resp_invalido.status_code, 200)

    def test_permissao_operador_csv_e_cadastro_prato(self):
        self.client.force_login(self.operador_a)
        resp_csv = self.client.get(reverse('exportar_comandas_csv'))
        self.assertEqual(resp_csv.status_code, 403)

        resp_novo = self.client.get(reverse('cadastrar_prato'))
        self.assertEqual(resp_novo.status_code, 403)

        self.client.force_login(self.admin_a)
        resp_csv_admin = self.client.get(reverse('exportar_comandas_csv'))
        self.assertEqual(resp_csv_admin.status_code, 200)
        self.assertEqual(resp_csv_admin['Content-Type'], 'text/csv; charset=utf-8')

    def test_api_isolamento_e_criacao(self):
        api = APIClient()
        # Sem autenticação -> 403
        self.assertIn(api.get('/api/pratos/').status_code, (401, 403))

        api.force_authenticate(user=self.admin_a)
        resp = api.get('/api/pratos/')
        self.assertEqual(resp.status_code, 200)
        nomes = [p['nome'] for p in resp.data]
        self.assertEqual(nomes, ['Feijoada Alpha'])

        # Cria prato na API e valida organização automática
        post_resp = api.post('/api/pratos/', {
            'nome': 'Suco Natural',
            'descricao': 'Laranja',
            'preco': '12.00',
            'categoria': 'BEBIDA',
            'disponivel': True,
        }, format='json')
        self.assertEqual(post_resp.status_code, 201)
        criado = Prato.objects.get(nome='Suco Natural')
        self.assertEqual(criado.organizacao, self.org_a)

    def test_sem_n_mais_1_ao_listar_itens_comanda(self):
        for i in range(5):
            p = Prato.objects.create(
                organizacao=self.org_a,
                nome=f'Prato Extra {i}',
                descricao='Desc',
                preco=Decimal('10.00'),
            )
            Item.objects.create(organizacao=self.org_a, comanda=self.comanda_a, prato=p, quantidade=1)

        with self.assertNumQueries(1):
            itens = list(self.comanda_a.itens.select_related('prato', 'combo').all())
            for item in itens:
                _ = item.preco_unitario
