from osgeo import gdal, ogr
import numpy as np
import geopandas as gpd
import base64
import json
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view
from .serializers import UploadedFileSerializer
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from .converter_to_geojson import convert_gis_file_geojson
from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import UploadedFile
import traceback
from .file_converter import convert_gis_file
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.shortcuts import render
from django.http import HttpResponse
from .models import UploadedFile
from .forms import UploadFileForm
from django.conf import settings
import os
from django.shortcuts import redirect


def file_manager(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Redirect back to the file manager page
            return redirect('file_manager')
    else:
        form = UploadFileForm()

    files = UploadedFile.objects.all()
    return render(request, 'file_manager/file_manager.html', {'form': form, 'files': files})


def download(request, pk):
    uploaded_file = get_object_or_404(UploadedFile, pk=pk)
    file_path = os.path.join(settings.MEDIA_ROOT, str(uploaded_file.file))

    # Debugging: Print the file path to make sure it's correct
    print(f"File path: {file_path}")

    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'),
                                content_type="application/octet-stream")
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
    else:
        # Debugging: Print an error message if the file does not exist
        print(f"Error: File not found at {file_path}")
        return HttpResponse("File not found.", status=404)


def delete(request, pk):
    uploaded_file = get_object_or_404(UploadedFile, pk=pk)
    uploaded_file.file.delete()
    uploaded_file.delete()
    return redirect('file_manager')


def convert(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        output_format = request.POST.get('output_format')
        uploaded_file = get_object_or_404(UploadedFile, pk=file_id)
        input_file_path = os.path.join(
            settings.MEDIA_ROOT, str(uploaded_file.file))

        # Debugging: Print input file path
        print(f"Input file path: {input_file_path}")

        if output_format == 'shp':
            file_extension = 'zip'
        else:
            file_extension = output_format

        output_file_name = f"{os.path.splitext(str(uploaded_file.file))[0]}_converted.{file_extension}"
        output_file_path = os.path.join(settings.MEDIA_ROOT, output_file_name)

        # Debugging: Print output file path
        print(f"Output file path: {output_file_path}")

        try:
            actual_output_file_path = convert_gis_file(
                input_file_path, output_file_path)

            # Calculate the relative path for the actual output file
            actual_output_file_relative_path = os.path.relpath(
                actual_output_file_path, settings.MEDIA_ROOT)

            # Pass the relative path to the UploadedFile object
            converted_file = UploadedFile(
                file=actual_output_file_relative_path)
            converted_file.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            print(f"Error: {e}")
            print(traceback.format_exc())  # Print traceback
            return JsonResponse({"status": "error", "message": str(e), "traceback": traceback.format_exc()})

    return JsonResponse({"status": "error", "message": "Invalid request"})


def delete_multiple(request):
    if request.method == 'POST':
        file_ids = request.POST.getlist('selected_files')
        UploadedFile.objects.filter(id__in=file_ids).delete()
        return redirect('file_manager')
    else:
        return redirect('file_manager')


# for leaflet preview on file manager.html
def converter_to_geojson(request):
    if request.method == 'POST':
        file_url = request.POST.get('file_url')
        input_file = os.path.join(settings.MEDIA_ROOT, file_url[1:])
        output_file = os.path.splitext(input_file)[0] + '_temp.geojson'

        try:
            convert_gis_file_geojson(input_file, output_file)
            with open(output_file, 'r') as f:
                geojson_data = f.read()

            os.remove(output_file)
            return JsonResponse({'geojson_data': geojson_data})

        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Conversion failed'})

    return JsonResponse({'error': 'Invalid request'})


@api_view(['GET'])
def get_file_data(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, pk=file_id)
    serializer = UploadedFileSerializer(uploaded_file)
    return Response(serializer.data)


@api_view(['POST'])
def save_edited_file(request):
    geojson_data = request.data.get('geojson_data')
    original_file_id = request.data.get('file_id')
    original_file = get_object_or_404(UploadedFile, pk=original_file_id)
    original_filename = os.path.splitext(
        os.path.basename(original_file.file.path))[0]

    edited_filename = f"{originalfilename}_edited.geojson"

    edited_file_path = os.path.join(
        settings.MEDIA_ROOT, 'uploads', edited_filename)

    # Convert the GeoJSON data to a file
    with open(edited_file_path, 'w') as f:
        json.dump(geojson_data, f)

    # Save the edited file as a new UploadedFile instance
    with open(edited_file_path, 'rb') as f:
        content = ContentFile(f.read())
        edited_file = UploadedFile(file=content, name=edited_filename)
        edited_file.save()

    return Response({"status": "success", "message": "Edited file saved successfully."})


@api_view(['GET'])
def get_file_attributes(request, file_id):
    try:
        uploaded_file = get_object_or_404(UploadedFile, pk=file_id)

        # Get the driver for the file format
        driver = ogr.GetDriverByName('GeoJSON')

        # Open the file
        dataSource = driver.Open(
            uploaded_file.file.path, 0)  # 0 means read-only

        # Get the first (and only) layer
        layer = dataSource.GetLayer()

        # Get the fields in the layer
        layerDefinition = layer.GetLayerDefn()
        field_names = [layerDefinition.GetFieldDefn(
            i).GetName() for i in range(layerDefinition.GetFieldCount())]

        # Extract the attributes for each feature in the layer
        data = []
        for feature in layer:
            attributes = {field: feature.GetField(
                field) for field in field_names}
            data.append(attributes)

        return JsonResponse({'data': data})

    except Exception as e:
        print(f"Error getting file attributes: {e}")
        return JsonResponse({"error": str(e)})
