from rest_framework import serializers
from .models import Prato, Combo, Mesa, Comanda, Item


class PratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prato
        fields = ['id', 'nome', 'descricao', 'preco', 'categoria', 'disponivel']

    def validate_preco(self, value):
        if value <= 0:
            raise serializers.ValidationError('O preço do prato deve ser maior que zero.')
        return value


class ComboSerializer(serializers.ModelSerializer):
    class Meta:
        model = Combo
        fields = ['id', 'nome', 'descricao', 'preco', 'pratos', 'disponivel']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request.user, 'perfil'):
            org = request.user.perfil.organizacao
            self.fields['pratos'].queryset = Prato.objects.filter(organizacao=org)

    def validate_preco(self, value):
        if value <= 0:
            raise serializers.ValidationError('O preço do combo deve ser maior que zero.')
        return value


class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ['id', 'numero', 'status']

    def validate_numero(self, value):
        request = self.context.get('request')
        if request and hasattr(request.user, 'perfil'):
            org = request.user.perfil.organizacao
            qs = Mesa.objects.filter(organizacao=org, numero=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('Já existe uma mesa com este número nesta organização.')
        return value


class ItemSerializer(serializers.ModelSerializer):
    prato_nome = serializers.CharField(source='prato.nome', read_only=True)
    combo_nome = serializers.CharField(source='combo.nome', read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'comanda', 'prato', 'prato_nome', 'combo', 'combo_nome', 'quantidade']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request.user, 'perfil'):
            org = request.user.perfil.organizacao
            self.fields['comanda'].queryset = Comanda.objects.filter(organizacao=org)
            self.fields['prato'].queryset = Prato.objects.filter(organizacao=org)
            self.fields['combo'].queryset = Combo.objects.filter(organizacao=org)

    def validate(self, data):
        prato = data.get('prato', getattr(self.instance, 'prato', None))
        combo = data.get('combo', getattr(self.instance, 'combo', None))
        if not prato and not combo:
            raise serializers.ValidationError('Informe um prato ou um combo para o item.')
        if prato and combo:
            raise serializers.ValidationError('Escolha apenas um prato ou um combo por item.')
        return data


class ComandaSerializer(serializers.ModelSerializer):
    mesa_numero = serializers.IntegerField(source='mesa.numero', read_only=True)
    itens = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = Comanda
        fields = ['id', 'mesa', 'mesa_numero', 'status', 'data_abertura', 'data_fechamento', 'itens']
        read_only_fields = ['data_abertura']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request.user, 'perfil'):
            org = request.user.perfil.organizacao
            self.fields['mesa'].queryset = Mesa.objects.filter(organizacao=org)
