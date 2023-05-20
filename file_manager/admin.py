from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import UploadedFile
# Register your models here.
admin.site.register(UploadedFile)
