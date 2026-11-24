from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Prato, Combo, Mesa, Comanda, Item
from .serializers import (
    PratoSerializer,
    ComboSerializer,
    MesaSerializer,
    ComandaSerializer,
    ItemSerializer,
)
from .permissions import TemPerfilOrganizacao, IsAdminOrganizacao
from .dashboard import calcular_metricas_dashboard
from .forms import filtrar_periodo


class OrganizacaoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, TemPerfilOrganizacao]

    def get_org(self):
        return self.request.user.perfil.organizacao

    def get_queryset(self):
        return self.queryset.filter(organizacao=self.get_org())

    def perform_create(self, serializer):
        serializer.save(organizacao=self.get_org())


class PratoViewSet(OrganizacaoViewSet):
    queryset = Prato.objects.all()
    serializer_class = PratoSerializer
    permission_classes = [IsAuthenticated, TemPerfilOrganizacao, IsAdminOrganizacao]


class ComboViewSet(OrganizacaoViewSet):
    queryset = Combo.objects.prefetch_related('pratos').all()
    serializer_class = ComboSerializer
    permission_classes = [IsAuthenticated, TemPerfilOrganizacao, IsAdminOrganizacao]


class MesaViewSet(OrganizacaoViewSet):
    queryset = Mesa.objects.order_by('numero')
    serializer_class = MesaSerializer
    permission_classes = [IsAuthenticated, TemPerfilOrganizacao, IsAdminOrganizacao]


class ComandaViewSet(OrganizacaoViewSet):
    queryset = Comanda.objects.select_related('mesa').prefetch_related('itens__prato', 'itens__combo')
    serializer_class = ComandaSerializer


class ItemViewSet(OrganizacaoViewSet):
    queryset = Item.objects.select_related('comanda', 'prato', 'combo')
    serializer_class = ItemSerializer


class DashboardApiView(APIView):
    permission_classes = [IsAuthenticated, TemPerfilOrganizacao]

    def get(self, request):
        org = request.user.perfil.organizacao
        base = filtrar_periodo(
            request,
            Comanda.objects.filter(organizacao=org),
            campo_data='data_abertura',
        )
        dados = calcular_metricas_dashboard(org, base)
        if not request.user.perfil.eh_admin:
            dados.pop('por_mes', None)
        return Response(dados)
