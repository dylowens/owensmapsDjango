from django.db import models


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/', max_length=500)
    upload_date = models.DateTimeField(auto_now_add=True)
    # preview_geojson = gis_models.GeometryField(null=True, blank=True)
