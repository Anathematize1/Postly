from django import forms
from django.contrib.auth import get_user_model

from .models import Post, Comment


User = get_user_model()


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author', 'is_published')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
