from django import forms
from post.models import Post

from django.forms import ClearableFileInput


class NewPostForm(forms.ModelForm):
    # ClearableFileInput file input에 사용하는 폼인거 같음
    content = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=True)
    caption = forms.CharField(widget=forms.Textarea(attrs={'class': 'input is-medium'}), required=True)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'input is-medium'}), required=True)

    class Meta:
        model = Post
        fields = ('content', 'caption', 'tags')