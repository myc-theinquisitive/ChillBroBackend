# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from kvstore.admin.forms import UploadBulkForm, UploadCSVForm
from kvstore.models import Tag


@permission_required(('kvstore.add_tag', 'kvstore.change_tag',))
def upload(request):
    bulk_entry_form = UploadBulkForm()
    context = {
        'bulk_entry_form': bulk_entry_form,
        'csv_upload_form': UploadCSVForm(),
    }
    return render(request, 'admin/kvstore/upload.html', context)


@permission_required(('kvstore.add_tag', 'kvstore.change_tag',))
def upload_bulk(request):
    """
    Mass set kvtags
    """
    if request.method == 'POST':
        bulk_entry_form = UploadBulkForm(request.POST)
        if bulk_entry_form.is_valid():
            ctype = bulk_entry_form.cleaned_data['object']
            count = 0
            for obj_id, k, v in bulk_entry_form.cleaned_data['input']:
                Tag.objects.get_or_create(
                    content_type=ctype,
                    object_id=obj_id,
                    key=k,
                    defaults={'value': v}
                )
                count += 1
            messages.info(request, "%s tags set" % count)
    else:
        bulk_entry_form = UploadBulkForm()

    context = {
        'bulk_entry_form': bulk_entry_form,
        'csv_upload_form': UploadCSVForm(),
    }
    return render(request, 'admin/kvstore/upload.html', context)


@permission_required(('kvstore.add_tag', 'kvstore.change_tag',))
def upload_csv(request):
    """
    Mass set kvtags via csv upload
    """
    if request.method == 'POST':
        upload_csv_form = UploadCSVForm(request.POST, request.FILES)
        if upload_csv_form.is_valid():
            ctype = upload_csv_form.cleaned_data['object']
            csv_file = upload_csv_form.cleaned_data['file']

            tags = []
            for line in csv_file.readlines():
                obj_id, k, v = line.decode("utf-8").strip().split(",")
                new_tag = Tag(
                    content_type=ctype,
                    object_id=obj_id.strip(),
                    key=k.strip(),
                    value=v.strip(),
                )
                tags.append(new_tag)

            Tag.objects.bulk_create(tags)
            messages.info(request, "%s tags set" % len(tags))
    else:
        upload_csv_form = UploadCSVForm()

    context = {
        'bulk_entry_form': UploadBulkForm(),
        'csv_upload_form': upload_csv_form,
    }
    return render(request, 'admin/kvstore/upload.html', context)
