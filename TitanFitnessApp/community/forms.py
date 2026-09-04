
from django import forms

class CreatePostForm(forms.Form):
    title = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput()
    )
    content = forms.CharField(
    required=True,
    widget=forms.Textarea()
    )

class CreateCommentForm(forms.Form):
    content = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.Textarea()
    )

