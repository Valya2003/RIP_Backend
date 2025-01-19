from django.contrib import admin

from .models import *

admin.site.register(Resistor)
admin.site.register(Calculation)
admin.site.register(ResistorCalculation)
admin.site.register(Status)
