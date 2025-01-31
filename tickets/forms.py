from django import forms
from .models import Mensagem, Ticket

class MensagemForm(forms.ModelForm):
    class Meta:
        model = Mensagem
        fields = ['texto']  # Campo que você deseja permitir o preenchimento

    # Caso queira adicionar validações extras
    def clean_texto(self):
        texto = self.cleaned_data.get('texto')
        if len(texto) < 5:
            raise forms.ValidationError("A mensagem deve ter pelo menos 5 caracteres.")
        return texto

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['titulo', 'descricao', 'data_entrega', 'empresa', 'responsavel', 'status', 'prioridade', 'observacoes']

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if len(titulo) < 5:
            raise forms.ValidationError("O título deve ter pelo menos 5 caracteres.")
        return titulo
