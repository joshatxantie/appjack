from django import forms
from .models import Game


class JoinGameForm(forms.Form):
    joincode = forms.CharField(label='Join Code', max_length=6, min_length=6)


class NewGameForm(forms.ModelForm):
    min_bet = forms.DecimalField(max_digits=6, decimal_places=2)
    max_bet = forms.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        model = Game
        fields = ['min_bet', 'max_bet']
        widgets = {
            'min_bet': forms.NumberInput(attrs={'step': '1'}),
            'max_bet': forms.NumberInput(attrs={'step': '1'}),
        }