from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('resistors/<int:resistor_id>/', resistor),
    path('calculations/<int:calculation_id>/', calculation),
]