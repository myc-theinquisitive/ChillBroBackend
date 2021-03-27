# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django import forms
from django.contrib.contenttypes.models import ContentType


class UploadBulkForm(forms.Form):

    class CTypeChoiceField(forms.ModelChoiceField):

        def label_from_instance(self, obj):
            return "%s - %s" % (obj.app_label, obj.model)

    object = CTypeChoiceField(
        queryset=ContentType.objects.order_by("app_label", "model").all()
    )
    input = forms.CharField(widget=forms.Textarea(attrs={'rows': 10}))

    def clean_input(self):
        """  Return a list of tuples instead of text """
        data = self.cleaned_data['input']

        # Split by newline
        values = re.split('\r\n', data)
        values = filter(lambda x: len(x.strip()) > 0, values)

        # Now split each row by a comma
        def return_row(row):
            vals = row.split(",")
            vals = map(lambda x: x.strip(), vals)
            return vals

        values = map(return_row, values)

        return values


class UploadCSVForm(forms.Form):

    class CTypeChoiceField(forms.ModelChoiceField):

        def label_from_instance(self, obj):
            return "%s - %s" % (obj.app_label, obj.model)

    object = CTypeChoiceField(
        queryset=ContentType.objects.order_by("app_label", "model").all()
    )
    file = forms.FileField()
