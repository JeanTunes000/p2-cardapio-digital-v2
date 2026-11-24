# Data migration (RunPython) para criar organização padrão e vincular registros sem organização
from django.db import migrations


def criar_org_padrao(apps, schema_editor):
    Organizacao = apps.get_model('restaurante', 'Organizacao')
    Prato = apps.get_model('restaurante', 'Prato')
    Combo = apps.get_model('restaurante', 'Combo')
    Mesa = apps.get_model('restaurante', 'Mesa')
    Comanda = apps.get_model('restaurante', 'Comanda')
    Item = apps.get_model('restaurante', 'Item')

    org, _ = Organizacao.objects.get_or_create(nome='Organização padrão')
    for model in (Prato, Combo, Mesa, Comanda, Item):
        model.objects.filter(organizacao__isnull=True).update(organizacao=org)


class Migration(migrations.Migration):

    dependencies = [
        ('restaurante', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_org_padrao, migrations.RunPython.noop),
    ]
