from django.urls import path
from .views import (
    list_files_view,
    view_file_view,
    download_file_view,
    homepage_view,
    new_experiment_view,
)

urlpatterns = [
    path('', homepage_view, name='homepage'),
    path('files/', list_files_view, name='file_list'),
    path('files/<str:file_name>/', view_file_view, name='view_file'),
    path('files/download/<str:file_name>/', download_file_view, name='download_file'),
    path('new-experiment/', new_experiment_view, name='new_experiment'),
]

