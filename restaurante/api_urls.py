from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    PratoViewSet,
    ComboViewSet,
    MesaViewSet,
    ComandaViewSet,
    ItemViewSet,
    DashboardApiView,
)

router = DefaultRouter()
router.register('pratos', PratoViewSet, basename='api-pratos')
router.register('combos', ComboViewSet, basename='api-combos')
router.register('mesas', MesaViewSet, basename='api-mesas')
router.register('comandas', ComandaViewSet, basename='api-comandas')
router.register('itens', ItemViewSet, basename='api-itens')

urlpatterns = [
    path('dashboard/', DashboardApiView.as_view(), name='api-dashboard'),
    path('', include(router.urls)),
]
