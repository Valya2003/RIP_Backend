from django.contrib.auth.models import User
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Resistor, Calculation, ResistorCalculation


def index(request):
    resistor_name = request.GET.get("resistor_name", "")
    resistors = Resistor.objects.filter(status=1)

    if resistor_name:
        resistors = resistors.filter(name__icontains=resistor_name)

    draft_calculation = get_draft_calculation()

    context = {
        "resistor_name": resistor_name,
        "resistors": resistors
    }

    if draft_calculation:
        context["resistors_count"] = len(draft_calculation.get_resistors())
        context["draft_calculation"] = draft_calculation

    return render(request, "resistors_page.html", context)


def add_resistor_to_draft_calculation(request, resistor_id):
    resistor = Resistor.objects.get(pk=resistor_id)

    draft_calculation = get_draft_calculation()

    if draft_calculation is None:
        draft_calculation = Calculation.objects.create()
        draft_calculation.owner = get_current_user()
        draft_calculation.date_created = timezone.now()
        draft_calculation.save()

    if ResistorCalculation.objects.filter(calculation=draft_calculation, resistor=resistor).exists():
        return redirect("/")

    item = ResistorCalculation(
        calculation=draft_calculation,
        resistor=resistor
    )
    item.save()

    return redirect("/")


def resistor_details(request, resistor_id):
    context = {
        "resistor": Resistor.objects.get(id=resistor_id)
    }

    return render(request, "resistor_page.html", context)


def delete_calculation(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE calculations SET status=5 WHERE id = %s", [calculation_id])

    return redirect("/")


def calculation(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return redirect("/")

    calculation = Calculation.objects.get(id=calculation_id)
    if calculation.status == 5:
        return redirect("/")

    context = {
        "calculation": calculation,
    }

    return render(request, "calculation_page.html", context)


def get_draft_calculation():
    return Calculation.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()


def get_resistor_image(request, resistor_id):
    resistor = Resistor.objects.get(pk=resistor_id)

    return HttpResponse(resistor.image, content_type="image/png")
