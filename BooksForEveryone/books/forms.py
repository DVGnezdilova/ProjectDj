from django import forms
from .models import Account, Review, User, Book

COUNT_CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5')
)

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


class ModeratorReviewForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Выберите пользователя",
        empty_label="---"
    )
    book = forms.ModelChoiceField(
        queryset=Book.objects.none(),
        label="Выберите книгу",
        empty_label="---"
    )
    text_review = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label="Текст отзыва",
        required=True
    )
    rating = forms.ChoiceField(
        choices=COUNT_CHOICES,
        label="Оценка",
        required=True
    )
    confirm = forms.BooleanField(
        required=True,
        label="Я подтверждаю, что пользователь действительно купил эту книгу"
    )

    def __init__(self, *args, **kwargs):
        users = kwargs.pop('users', None)
        books = kwargs.pop('books', None)
        super().__init__(*args, **kwargs)
        
        if users is not None:
            self.fields['user'].queryset = users
        if books is not None:
            self.fields['book'].queryset = books

    def clean_text_review(self):
        text = self.cleaned_data.get('text_review')
        if len(text.strip()) < 10:
            raise forms.ValidationError("Отзыв должен содержать минимум 10 символов.")
        return text