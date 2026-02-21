from django import forms
from .models import Fee, Expense, Salary
from teacher.models import Teacher


class FeeForm(forms.ModelForm):
    """
    Fee form:
    - Only lets user enter: student, month, total_amount, amount_paid
    - remaining + status are calculated in the model (save())
    - extra validation so paid <= total and no negative values
    """

    class Meta:
        model = Fee
        fields = ["student", "month", "total_amount", "amount_paid"]
        widgets = {
            "student": forms.Select(attrs={"class": "form-control"}),
            "month": forms.Select(attrs={"class": "form-control"}),
            "total_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter total amount",
                    "min": "0",
                }
            ),
            "amount_paid": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter paid amount",
                    "min": "0",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get("total_amount")
        paid = cleaned_data.get("amount_paid")

        # Extra safety on form level
        if total is not None and total < 0:
            self.add_error("total_amount", "Total amount must be zero or positive.")

        if paid is not None and paid < 0:
            self.add_error("amount_paid", "Amount paid must be zero or positive.")

        if total is not None and paid is not None and paid > total:
            self.add_error(
                "amount_paid",
                "Amount paid cannot be greater than total amount.",
            )

        return cleaned_data


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["title", "category", "amount", "description"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter title"}
            ),
            "category": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter category"}
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter amount",
                    "min": "0",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter description",
                }
            ),
        }


class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ["teacher", "month", "amount", "status"]
        widgets = {
            "teacher": forms.Select(attrs={"class": "form-control"}),
            "month": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. January"}
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter amount",
                    "min": "0",
                }
            ),
            "status": forms.Select(
                choices=(("Paid", "Paid"), ("Pending", "Pending")),
                attrs={"class": "form-control"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super(SalaryForm, self).__init__(*args, **kwargs)
        self.fields["teacher"].queryset = Teacher.objects.all().order_by("first_name")
        self.fields["teacher"].widget.attrs.update({"class": "form-control"})
