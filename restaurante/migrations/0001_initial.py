# Generated manually for P2 multi-tenant schema
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Organizacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=120)),
                ('criada_em', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Organização',
                'verbose_name_plural': 'Organizações',
            },
        ),
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('papel', models.CharField(choices=[('admin', 'Administrador'), ('operador', 'Operador')], default='operador', max_length=20)),
                ('organizacao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='perfis', to='restaurante.organizacao')),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='perfil', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Perfil',
                'verbose_name_plural': 'Perfis',
            },
        ),
        migrations.CreateModel(
            name='Prato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('descricao', models.TextField()),
                ('preco', models.DecimalField(decimal_places=2, max_digits=8)),
                ('categoria', models.CharField(choices=[('ENTRADA', 'Entrada'), ('PRINCIPAL', 'Prato principal'), ('SOBREMESA', 'Sobremesa'), ('BEBIDA', 'Bebida')], default='PRINCIPAL', max_length=20)),
                ('disponivel', models.BooleanField(default=True)),
                ('organizacao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='restaurante.organizacao')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Combo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('descricao', models.TextField(blank=True)),
                ('preco', models.DecimalField(decimal_places=2, max_digits=8)),
                ('disponivel', models.BooleanField(default=True)),
                ('organizacao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='restaurante.organizacao')),
                ('pratos', models.ManyToManyField(blank=True, related_name='combos', to='restaurante.prato')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mesa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('LIVRE', 'Livre'), ('OCUPADA', 'Ocupada')], default='LIVRE', max_length=20)),
                ('organizacao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='restaurante.organizacao')),
            ],
        ),
        migrations.CreateModel(
            name='Comanda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('ABERTA', 'Aberta'), ('FECHADA', 'Fechada')], default='ABERTA', max_length=20)),
                ('data_abertura', models.DateTimeField(auto_now_add=True)),
                ('data_fechamento', models.DateTimeField(blank=True, null=True)),
                ('mesa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='comandas', to='restaurante.mesa')),
                ('organizacao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='restaurante.organizacao')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField(default=1)),
                ('comanda', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='restaurante.comanda')),
                ('combo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='restaurante.combo')),
                ('organizacao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='restaurante.organizacao')),
                ('prato', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='restaurante.prato')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddConstraint(
            model_name='mesa',
            constraint=models.UniqueConstraint(fields=('organizacao', 'numero'), name='mesa_numero_unico_por_org'),
        ),
        migrations.AddIndex(
            model_name='comanda',
            index=models.Index(fields=['organizacao', 'data_abertura'], name='restaurante_organiz_54c0aa_idx'),
        ),
        migrations.AddIndex(
            model_name='comanda',
            index=models.Index(fields=['organizacao', 'status'], name='restaurante_organiz_0bb1de_idx'),
        ),
    ]
