from django import forms
from .models import Fee, Expense, Salary
from teacher.models import Teacher


class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['student', 'month', 'total_amount', 'amount_paid', 'remaining', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'month': forms.Select(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter total amount'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter paid amount'}),
            'remaining': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter remaining amount'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'category', 'amount', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter description'
            }),
        }


class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ['teacher', 'month', 'amount', 'status']
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'month': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. January'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'status': forms.Select(
                choices=(('Paid', 'Paid'), ('Pending', 'Pending')),
                attrs={'class': 'form-control'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(SalaryForm, self).__init__(*args, **kwargs)
        self.fields['teacher'].queryset = Teacher.objects.all().order_by('first_name')
        self.fields['teacher'].widget.attrs.update({'class': 'form-control'})
