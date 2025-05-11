from django import forms
from .models import Book, Account, Review

# Форма редактирования профиля
class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['surname', 'name', 'birthday', 'photo_acc']
        widgets = {
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'birthday': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'photo_acc': forms.FileInput(attrs={'class': 'form-control'})
        }
    def save(self, commit=True):
        account = super().save(commit=False)
        if commit:
            account.save()
        return account

from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text_review', 'rating']
        widgets = {
            'text_review': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Напишите ваш отзыв о книге'
            }),
            'rating': forms.HiddenInput(),  # ← теперь рейтинг будет управляться JS
        }

    def clean_text_review(self):
        text = self.cleaned_data.get('text_review')
        if len(text.strip()) < 10:
            raise forms.ValidationError("Отзыв должен содержать минимум 10 символов.")
        return text

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text_review'].label = "Ваш отзыв"
        self.fields['rating'].label = "Оценка"

