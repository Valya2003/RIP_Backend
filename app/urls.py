from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('resistors/<int:resistor_id>/', resistor_details, name="resistor_details"),
    path('resistors/<int:resistor_id>/add_to_calculation/', add_resistor_to_draft_calculation, name="add_resistor_to_draft_calculation"),
    path('calculations/<int:calculation_id>/delete/', delete_calculation, name="delete_calculation"),
    path('calculations/<int:calculation_id>/', calculation),
    path('resistors/<int:resistor_id>/image', get_resistor_image, name="resistor_image"),
]
