from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/resistors/', search_resistors),  # GET
    path('api/resistors/<int:resistor_id>/', get_resistor_by_id),  # GET
    path('api/resistors/<int:resistor_id>/update/', update_resistor),  # PUT
    path('api/resistors/<int:resistor_id>/update_image/', update_resistor_image),  # POST
    path('api/resistors/<int:resistor_id>/delete/', delete_resistor),  # DELETE
    path('api/resistors/create/', create_resistor),  # POST
    path('api/resistors/<int:resistor_id>/add_to_calculation/', add_resistor_to_calculation),  # POST

    path('api/resistors/<int:resistor_id>/image/', get_resistor_image),  # GET

    # Набор методов для заявок
    path('api/calculations/', search_calculations),  # GET
    path('api/calculations/<int:calculation_id>/', get_calculation_by_id),  # GET
    path('api/calculations/<int:calculation_id>/update/', update_calculation),  # PUT
    path('api/calculations/<int:calculation_id>/update_status_user/', update_status_user),  # PUT
    path('api/calculations/<int:calculation_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/calculations/<int:calculation_id>/delete/', delete_calculation),  # DELETE

    # Набор методов для м-м
    path('api/calculations/<int:calculation_id>/update_resistor/<int:resistor_id>/', update_resistor_in_calculation),  # PUT
    path('api/calculations/<int:calculation_id>/delete_resistor/<int:resistor_id>/', delete_resistor_from_calculation),  # DELETE

    # Набор методов пользователей
    path('api/users/register/', register), # POST
    path('api/users/login/', login), # POST
    path('api/users/logout/', logout), # POST
    path('api/users/<int:user_id>/update/', update_user) # PUT
]
