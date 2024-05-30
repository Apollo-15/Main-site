from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms

class CommentForm(forms.Form):
    content = forms.CharField(min_length=6,max_length=200)
