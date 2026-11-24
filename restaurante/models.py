from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Organizacao(models.Model):
    nome = models.CharField(max_length=120)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Organização'
        verbose_name_plural = 'Organizações'

    def __str__(self):
        return self.nome


class Perfil(models.Model):
    PAPEIS = [
        ('admin', 'Administrador'),
        ('operador', 'Operador'),
    ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
    )
    organizacao = models.ForeignKey(
        Organizacao,
        on_delete=models.PROTECT,
        related_name='perfis',
    )
    papel = models.CharField(
        max_length=20,
        choices=PAPEIS,
        default='operador',
    )

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    @property
    def eh_admin(self):
        return self.papel == 'admin'

    def __str__(self):
        return f'{self.usuario.username} ({self.organizacao.nome} - {self.get_papel_display()})'


class DaOrganizacao(models.Model):
    organizacao = models.ForeignKey(
        Organizacao,
        on_delete=models.PROTECT,
    )

    class Meta:
        abstract = True


class Prato(DaOrganizacao):
    CATEGORIA_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('PRINCIPAL', 'Prato principal'),
        ('SOBREMESA', 'Sobremesa'),
        ('BEBIDA', 'Bebida'),
    ]

    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default='PRINCIPAL',
    )
    disponivel = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if self.preco is not None and self.preco <= 0:
            raise ValidationError({'preco': 'O preço do prato deve ser maior que zero.'})

    def __str__(self):
        return self.nome


class Combo(DaOrganizacao):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    pratos = models.ManyToManyField(Prato, blank=True, related_name='combos')
    disponivel = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if self.preco is not None and self.preco <= 0:
            raise ValidationError({'preco': 'O preço do combo deve ser maior que zero.'})

    def __str__(self):
        return self.nome


class Mesa(DaOrganizacao):
    STATUS_CHOICES = [
        ('LIVRE', 'Livre'),
        ('OCUPADA', 'Ocupada'),
    ]

    numero = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='LIVRE',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['organizacao', 'numero'],
                name='mesa_numero_unico_por_org',
            )
        ]

    def __str__(self):
        return f'Mesa {self.numero}'


class Comanda(DaOrganizacao):
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('FECHADA', 'Fechada'),
    ]

    mesa = models.ForeignKey(
        Mesa,
        on_delete=models.PROTECT,
        related_name='comandas',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ABERTA',
    )
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_fechamento = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['organizacao', 'data_abertura']),
            models.Index(fields=['organizacao', 'status']),
        ]

    @property
    def total(self):
        soma = Decimal('0.00')
        for item in self.itens.select_related('prato', 'combo'):
            soma += item.subtotal
        return soma

    def __str__(self):
        return f'Comanda #{self.id} - Mesa {self.mesa.numero}'


class Item(DaOrganizacao):
    comanda = models.ForeignKey(
        Comanda,
        on_delete=models.CASCADE,
        related_name='itens',
    )
    prato = models.ForeignKey(
        Prato,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    combo = models.ForeignKey(
        Combo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    quantidade = models.PositiveIntegerField(default=1)

    @property
    def preco_unitario(self):
        if self.prato:
            return self.prato.preco
        if self.combo:
            return self.combo.preco
        return Decimal('0.00')

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        nome = self.prato.nome if self.prato else (self.combo.nome if self.combo else 'Item')
        return f'{self.quantidade}x {nome}'
