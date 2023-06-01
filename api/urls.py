from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('insert_store_status/', insert_store_status),
    path('insert_menu_hours/', insert_menu_hours),
    path('insert_time_zone/', insert_time_zone),
    path('trigger_report/', trigger_report),
    path('get_report/<str:report_id>/', get_report),
]