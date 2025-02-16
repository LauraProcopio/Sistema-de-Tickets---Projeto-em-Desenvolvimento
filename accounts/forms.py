from django import forms
from .models import CustomUser

class AlterarEmailForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email']  # Incluir apenas o campo de e-mail para alteração

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
