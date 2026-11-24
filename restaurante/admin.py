from django.contrib import admin
from .models import Organizacao, Perfil, Prato, Combo, Mesa, Comanda, Item


@admin.register(Organizacao)
class OrganizacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'criada_em')
    search_fields = ('nome',)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'organizacao', 'papel')
    list_filter = ('organizacao', 'papel')
    search_fields = ('usuario__username',)


class DaOrganizacaoAdmin(admin.ModelAdmin):
    list_filter = ('organizacao',)


@admin.register(Prato)
class PratoAdmin(DaOrganizacaoAdmin):
    list_display = ('nome', 'categoria', 'preco', 'disponivel', 'organizacao')
    list_filter = ('organizacao', 'categoria', 'disponivel')


@admin.register(Combo)
class ComboAdmin(DaOrganizacaoAdmin):
    list_display = ('nome', 'preco', 'disponivel', 'organizacao')


@admin.register(Mesa)
class MesaAdmin(DaOrganizacaoAdmin):
    list_display = ('numero', 'status', 'organizacao')
    list_filter = ('organizacao', 'status')


@admin.register(Comanda)
class ComandaAdmin(DaOrganizacaoAdmin):
    list_display = ('id', 'mesa', 'status', 'data_abertura', 'organizacao')
    list_filter = ('organizacao', 'status')


@admin.register(Item)
class ItemAdmin(DaOrganizacaoAdmin):
    list_display = ('id', 'comanda', 'prato', 'combo', 'quantidade', 'organizacao')


admin.site.site_header = "Painel Administrativo — Cardápio Digital"
admin.site.site_title = "Cardápio Digital"
admin.site.index_title = "Painel Administrativo"
