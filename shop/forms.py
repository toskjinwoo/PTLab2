from django import forms

from .models import Purchase


class PurchaseForm(forms.ModelForm):
    person = forms.CharField(max_length=200, label='Имя покупателя')

    class Meta:
        model = Purchase
        fields = ['product', 'address']
