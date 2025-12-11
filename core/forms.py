from django import forms
from core.models import CreditCard, Goal

class CreditCardForm(forms.ModelForm):
    # name = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Card Holder Name"}))
    # number = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"Card Number"}))
    # month = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"Expiry Month", "minlength":"4", "maxlength":"4" }))
    # year = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"Expiry Year"}))
    # cvv = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"CVV"}))

    class Meta:
        model = CreditCard
        fields = ['card_type']

    # this guy will apply automatic class to all the fields with class
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = "form-control form-select" # and the is the border around the input


# Fund Wallet Form
class AmountForm(forms.ModelForm):
    amount = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"$0.00"}))
    
    class Meta:
        model = CreditCard
        fields = ['amount']
        
    # this guy will apply automatic class to all the fields with class
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = "form-control" # and the is the border around the input


# Goal
class GoalForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Goal Title"}))
    description = forms.CharField(widget=forms.Textarea(attrs={"placeholder":"Goal Description"}))
    target_amount = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"0.00"}))
    deadline = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'placeholder': "e.g: 2025-12-17", "class":"form-control"}))

    class Meta:
        model = Goal
        fields = [
            "title",
            "description",
            "goal_type",
            "target_amount",
            "image",
            "deadline"
        ]
        
        
    # this guy will apply automatic class to all the fields with class
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = "form-control" # and the is the border around the input

