from django.urls import path
from . import views
from .views import get_file_attributes


urlpatterns = [
    path('', views.file_manager, name='file_manager'),
    path('download/<int:pk>/', views.download, name='download'),
    path('delete/<int:pk>/', views.delete, name='delete'),
    path('convert/', views.convert, name='convert'),
    path('delete_multiple/', views.delete_multiple, name='delete_multiple'),
    path('converter_to_geojson/', views.converter_to_geojson,
         name='converter_to_geojson'),
    path('api/file_data/<int:file_id>/',
         views.get_file_data, name='get_file_data'),
    path('save_edited_file/', views.save_edited_file, name='save_edited_file'),
    path('file_attributes/<int:file_id>/',
         get_file_attributes, name='get_file_attributes'),
]
