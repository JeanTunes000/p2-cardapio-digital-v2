import csv
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Prato, Combo, Mesa, Comanda, Item
from .forms import PratoForm, PeriodoForm, filtrar_periodo
from .permissions import perfil_obrigatorio, papel_requerido
from .dashboard import calcular_metricas_dashboard


def _sanitizar_csv(valor):
    texto = str(valor) if valor is not None else ''
    if texto.startswith(('=', '+', '-', '@')):
        return "'" + texto
    return texto


@perfil_obrigatorio
def inicio(request):
    return render(request, 'restaurante/inicio.html', {'perfil': request.perfil})


@perfil_obrigatorio
def lista_pratos(request):
    org = request.org
    termo = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()

    pratos = Prato.objects.filter(organizacao=org)

    if termo:
        pratos = pratos.filter(nome__icontains=termo)

    if categoria:
        pratos = pratos.filter(categoria=categoria)

    return render(
        request,
        'restaurante/lista_pratos.html',
        {
            'pratos': pratos,
            'categorias': Prato.CATEGORIA_CHOICES,
        },
    )


@papel_requerido('admin')
def cadastrar_prato(request):
    org = request.org
    if request.method == 'POST':
        form = PratoForm(request.POST, org=org)
        if form.is_valid():
            prato = form.save(commit=False)
            prato.organizacao = org
            prato.save()
            return redirect('lista_pratos')
    else:
        form = PratoForm(org=org)

    return render(
        request,
        'restaurante/form_prato.html',
        {'form': form},
    )


@perfil_obrigatorio
def lista_combos(request):
    org = request.org
    combos = Combo.objects.filter(organizacao=org).prefetch_related('pratos')

    return render(
        request,
        'restaurante/lista_combos.html',
        {'combos': combos},
    )


@perfil_obrigatorio
def lista_mesas(request):
    org = request.org
    mesas = Mesa.objects.filter(organizacao=org).order_by('numero')

    return render(
        request,
        'restaurante/lista_mesas.html',
        {'mesas': mesas},
    )


@perfil_obrigatorio
def abrir_comanda(request, mesa_id):
    org = request.org
    mesa = get_object_or_404(Mesa, id=mesa_id, organizacao=org)

    comanda = Comanda.objects.filter(
        organizacao=org,
        mesa=mesa,
        status='ABERTA',
    ).first()

    if not comanda:
        comanda = Comanda.objects.create(organizacao=org, mesa=mesa)
        mesa.status = 'OCUPADA'
        mesa.save()

    pratos = Prato.objects.filter(organizacao=org, disponivel=True)
    combos = Combo.objects.filter(organizacao=org, disponivel=True)

    itens = comanda.itens.select_related('prato', 'combo').all()

    total = sum((item.subtotal for item in itens), 0)

    return render(
        request,
        'restaurante/comanda.html',
        {
            'mesa': mesa,
            'comanda': comanda,
            'pratos': pratos,
            'combos': combos,
            'itens': itens,
            'total': total,
        },
    )


@perfil_obrigatorio
def adicionar_prato(request, comanda_id, prato_id):
    org = request.org
    comanda = get_object_or_404(Comanda, id=comanda_id, organizacao=org)
    prato = get_object_or_404(Prato, id=prato_id, organizacao=org)

    item = Item.objects.filter(
        organizacao=org,
        comanda=comanda,
        prato=prato,
    ).first()

    if item:
        item.quantidade += 1
        item.save()
    else:
        Item.objects.create(
            organizacao=org,
            comanda=comanda,
            prato=prato,
            quantidade=1,
        )

    return redirect('abrir_comanda', mesa_id=comanda.mesa.id)


@perfil_obrigatorio
def adicionar_combo(request, comanda_id, combo_id):
    org = request.org
    comanda = get_object_or_404(Comanda, id=comanda_id, organizacao=org)
    combo = get_object_or_404(Combo, id=combo_id, organizacao=org)

    item = Item.objects.filter(
        organizacao=org,
        comanda=comanda,
        combo=combo,
    ).first()

    if item:
        item.quantidade += 1
        item.save()
    else:
        Item.objects.create(
            organizacao=org,
            comanda=comanda,
            combo=combo,
            quantidade=1,
        )

    return redirect('abrir_comanda', mesa_id=comanda.mesa.id)


@perfil_obrigatorio
def fechar_comanda(request, comanda_id):
    org = request.org
    comanda = get_object_or_404(Comanda.objects.select_related('mesa'), id=comanda_id, organizacao=org)

    comanda.status = 'FECHADA'
    comanda.data_fechamento = timezone.now()
    comanda.save()

    mesa = comanda.mesa
    mesa.status = 'LIVRE'
    mesa.save()

    return redirect('lista_mesas')


@perfil_obrigatorio
def remover_item(request, item_id):
    org = request.org
    item = get_object_or_404(
        Item.objects.select_related('comanda__mesa'),
        id=item_id,
        organizacao=org,
    )

    mesa_id = item.comanda.mesa.id

    if item.quantidade > 1:
        item.quantidade -= 1
        item.save()
    else:
        item.delete()

    return redirect('abrir_comanda', mesa_id=mesa_id)


@perfil_obrigatorio
def dashboard(request):
    org = request.org
    base = filtrar_periodo(
        request,
        Comanda.objects.filter(organizacao=org),
        campo_data='data_abertura',
    )
    metricas = calcular_metricas_dashboard(org, base)

    contexto = {
        **metricas,
        'form': PeriodoForm(request.GET),
        'mostra_series': request.perfil.eh_admin,
        'pode_exportar': request.perfil.eh_admin,
    }
    return render(request, 'restaurante/dashboard.html', contexto)


@papel_requerido('admin')
def exportar_comandas_csv(request):
    org = request.org
    qs = filtrar_periodo(
        request,
        Comanda.objects.filter(organizacao=org)
        .select_related('mesa')
        .prefetch_related('itens__prato', 'itens__combo')
        .order_by('-data_abertura'),
        campo_data='data_abertura',
    )

    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = 'attachment; filename="relatorio_comandas.csv"'

    writer = csv.writer(resp)
    writer.writerow(['Comanda', 'Mesa', 'Status', 'Data Abertura', 'Qtd Itens', 'Total (R$)'])

    for c in qs:
        itens_lista = list(c.itens.all())
        qtd_itens = sum(i.quantidade for i in itens_lista)
        total = sum((i.subtotal for i in itens_lista), 0)
        writer.writerow([
            _sanitizar_csv(c.id),
            _sanitizar_csv(c.mesa.numero),
            _sanitizar_csv(c.get_status_display()),
            _sanitizar_csv(c.data_abertura.strftime('%d/%m/%Y %H:%M') if c.data_abertura else ''),
            _sanitizar_csv(qtd_itens),
            _sanitizar_csv(f'{total:.2f}'),
        ])

    return resp
