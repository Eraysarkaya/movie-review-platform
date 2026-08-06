from django import forms
from movie.models import Review, RATE_CHOICES

#İnceleme yazısı ve puanlama için Form
class RateForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'class' : 'materialize-textarea'}), required=False)
    rate = forms.ChoiceField(choices=RATE_CHOICES, widget=forms.Select(), required=True)

    class Meta:
        model = Review
        fields = ('text', 'rate') # Formda yer alacak alanlar

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rate'].required = True # Puanlama zorunlu
