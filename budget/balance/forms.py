from django.forms import ModelForm
from .models import Transaction


class CreateTransactionForm(ModelForm):
    class Meta:
        model = Transaction
        exclude = ["user", "group"]
