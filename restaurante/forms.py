from django import forms
from .models import Prato, Combo, Mesa


class PratoForm(forms.ModelForm):
    class Meta:
        model = Prato
        fields = ['nome', 'descricao', 'preco', 'categoria', 'disponivel']
        labels = {
            'nome': 'Nome',
            'descricao': 'Descrição',
            'preco': 'Preço',
            'categoria': 'Categoria',
            'disponivel': 'Disponível',
        }

    def __init__(self, *args, org=None, **kwargs):
        self.org = org
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        preco = cleaned_data.get('preco')
        if preco is not None and preco <= 0:
            raise forms.ValidationError('O preço do prato deve ser maior que zero.')
        return cleaned_data


class ComboForm(forms.ModelForm):
    class Meta:
        model = Combo
        fields = ['nome', 'descricao', 'preco', 'pratos', 'disponivel']

    def __init__(self, *args, org=None, **kwargs):
        self.org = org
        super().__init__(*args, **kwargs)
        if org is not None:
            self.fields['pratos'].queryset = Prato.objects.filter(organizacao=org)


class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['numero', 'status']

    def __init__(self, *args, org=None, **kwargs):
        self.org = org
        super().__init__(*args, **kwargs)

    def clean_numero(self):
        numero = self.cleaned_data['numero']
        if self.org is not None:
            qs = Mesa.objects.filter(organizacao=self.org, numero=numero)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Já existe uma mesa com este número nesta organização.')
        return numero


class PeriodoForm(forms.Form):
    inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Início',
    )
    fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fim',
    )


def filtrar_periodo(request, qs, campo_data='data_abertura'):
    form = PeriodoForm(request.GET)
    if form.is_valid():
        inicio = form.cleaned_data.get('inicio')
        fim = form.cleaned_data.get('fim')
        if inicio:
            qs = qs.filter(**{f'{campo_data}__date__gte': inicio})
        if fim:
            qs = qs.filter(**{f'{campo_data}__date__lte': fim})
    return qs
