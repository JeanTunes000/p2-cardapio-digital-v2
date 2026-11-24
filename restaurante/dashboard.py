from decimal import Decimal
from django.db.models import Count, Sum, F, Q, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncMonth
from .models import Comanda, Item, Prato


def calcular_metricas_dashboard(org, base_comandas=None):
    if base_comandas is None:
        base_comandas = Comanda.objects.filter(organizacao=org)

    # 1. KPIs (Total de comandas, abertas, fechadas e faturamento)
    kpis = base_comandas.aggregate(
        total_comandas=Count('id'),
        abertas=Count('id', filter=Q(status='ABERTA')),
        fechadas=Count('id', filter=Q(status='FECHADA')),
        mesas_atendidas=Count('mesa', distinct=True),
    )

    itens_base = Item.objects.filter(
        organizacao=org,
        comanda__in=base_comandas,
    )

    faturamento_pratos = itens_base.filter(prato__isnull=False).aggregate(
        total=Sum(
            ExpressionWrapper(
                F('quantidade') * F('prato__preco'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
    )['total'] or Decimal('0.00')

    faturamento_combos = itens_base.filter(combo__isnull=False).aggregate(
        total=Sum(
            ExpressionWrapper(
                F('quantidade') * F('combo__preco'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
    )['total'] or Decimal('0.00')

    kpis['faturamento_total'] = faturamento_pratos + faturamento_combos

    # 2. Ranking: Top 5 pratos mais pedidos
    ranking_pratos = list(
        itens_base.filter(prato__isnull=False)
        .values('prato__nome')
        .annotate(total_qtd=Sum('quantidade'))
        .order_by('-total_qtd', 'prato__nome')[:5]
    )

    # 3. Série temporal: Comandas por mês
    por_mes_qs = (
        base_comandas.annotate(mes=TruncMonth('data_abertura'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    por_mes = [
        {
            'mes': r['mes'].strftime('%m/%Y') if r['mes'] else 'Sem data',
            'total': r['total'],
        }
        for r in por_mes_qs
    ]

    # 4. Distribuição: Comandas por status e Pratos disponíveis por categoria
    distribuicao_status = list(
        base_comandas.values('status')
        .annotate(total=Count('id'))
        .order_by('status')
    )

    distribuicao_categorias = list(
        Prato.objects.filter(organizacao=org)
        .values('categoria')
        .annotate(total=Count('id'))
        .order_by('-total', 'categoria')
    )

    return {
        'kpis': kpis,
        'ranking_pratos': ranking_pratos,
        'por_mes': por_mes,
        'distribuicao_status': distribuicao_status,
        'distribuicao_categorias': distribuicao_categorias,
    }
