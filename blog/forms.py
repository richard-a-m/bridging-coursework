from django import forms
from tinymce.widgets import TinyMCE

from .models import Post

class PostForm(forms.ModelForm):
    text = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = Post
        fields = ('title', 'text',)
