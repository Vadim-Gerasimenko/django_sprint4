from django.core.exceptions import ValidationError
from blog.models import Post, Comment
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()


class CorrectUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True


class CorrectUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)

        super().__init__(*args, **kwargs)
        del self.fields['password']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'location', 'category', 'image']
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'text': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст публикации',
            'pub_date': 'Дата и время публикации',
            'location': 'Местоположение',
            'category': 'Категория',
            'image': 'Изображение',
        }
        help_texts = {
            'pub_date': 'Если установить дату и время в будущем — можно делать отложенные публикации.',
            'is_published': 'Снимите галочку, чтобы скрыть публикацию.',
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('category'):
            raise ValidationError({'category': 'Необходимо выбрать категорию'})
        return cleaned_data


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
