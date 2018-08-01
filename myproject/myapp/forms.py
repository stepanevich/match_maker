# -*- coding: utf-8 -*-

from django import forms
from .models import Document
from django.forms import ModelForm, Form


class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ('docfile', 'name')

class ImageForm(Form):
    docfile = forms.ImageField()

    