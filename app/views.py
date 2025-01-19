import random

from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *


def get_draft_calculation():
    return Calculation.objects.filter(status=Status.objects.get(pk=1)).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(["GET"])
def search_resistors(request):
    resistor_name = request.GET.get("resistor_name", "")

    resistors = Resistor.objects.filter(status=1)

    if resistor_name:
        resistors = resistors.filter(name__icontains=resistor_name)

    serializer = ResistorsSerializer(resistors, many=True)
    
    draft_calculation = get_draft_calculation()

    resp = {
        "resistors": serializer.data,
        "resistors_count": ResistorCalculation.objects.filter(calculation=draft_calculation).count() if draft_calculation else None,
        "draft_calculation": draft_calculation.pk if draft_calculation else None
    }

    return Response(resp)


@api_view(["GET"])
def get_resistor_by_id(request, resistor_id):
    if not Resistor.objects.filter(pk=resistor_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resistor = Resistor.objects.get(pk=resistor_id)
    serializer = ResistorSerializer(resistor)

    return Response(serializer.data)


@api_view(["PUT"])
def update_resistor(request, resistor_id):
    if not Resistor.objects.filter(pk=resistor_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resistor = Resistor.objects.get(pk=resistor_id)

    serializer = ResistorSerializer(resistor, data=request.data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_resistor(request):
    serializer = ResistorSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Resistor.objects.create(**serializer.validated_data)

    resistors = Resistor.objects.filter(status=1)
    serializer = ResistorSerializer(resistors, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_resistor(request, resistor_id):
    if not Resistor.objects.filter(pk=resistor_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resistor = Resistor.objects.get(pk=resistor_id)
    resistor.status = 2
    resistor.save()

    resistors = Resistor.objects.filter(status=1)
    serializer = ResistorSerializer(resistors, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_resistor_to_calculation(request, resistor_id):
    if not Resistor.objects.filter(pk=resistor_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resistor = Resistor.objects.get(pk=resistor_id)

    draft_calculation = get_draft_calculation()

    if draft_calculation is None:
        draft_calculation = Calculation.objects.create()
        draft_calculation.owner = get_user()
        draft_calculation.date_created = timezone.now()
        draft_calculation.status = Status.objects.get(pk=1)
        draft_calculation.save()

    if ResistorCalculation.objects.filter(calculation=draft_calculation, resistor=resistor).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    item = ResistorCalculation.objects.create()
    item.calculation = draft_calculation
    item.resistor = resistor
    item.save()

    serializer = CalculationSerializer(draft_calculation)
    return Response(serializer.data["resistors"])


@api_view(["POST"])
def update_resistor_image(request, resistor_id):
    if not Resistor.objects.filter(pk=resistor_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resistor = Resistor.objects.get(pk=resistor_id)

    image = request.data.get("image")
    if image is not None:
        resistor.image = image
        resistor.save()

    serializer = ResistorSerializer(resistor)

    return Response(serializer.data)


@api_view(["GET"])
def search_calculations(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    calculations = Calculation.objects.exclude(status__in=[Status.objects.get(pk=1), Status.objects.get(pk=5)])

    if status > 0:
        calculations = calculations.filter(status=Status.objects.get(pk=status))

    if date_formation_start and parse_datetime(date_formation_start):
        calculations = calculations.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        calculations = calculations.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = CalculationsSerializer(calculations, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_calculation_by_id(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)
    serializer = CalculationSerializer(calculation, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_calculation(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)
    serializer = CalculationSerializer(calculation, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != Status.objects.get(pk=1):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation.status = Status.objects.get(pk=2)
    calculation.date_formation = timezone.now()
    calculation.save()

    serializer = CalculationSerializer(calculation, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != Status.objects.get(pk=2):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        calculation.current = random.randint(1, 10)

    calculation.date_complete = timezone.now()
    calculation.status = Status.objects.get(pk=request_status)
    calculation.moderator = get_moderator()
    calculation.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_calculation(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != Status.objects.get(pk=1):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation.status = Status.objects.get(pk=5)
    calculation.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_resistor_from_calculation(request, calculation_id, resistor_id):
    if not ResistorCalculation.objects.filter(calculation_id=calculation_id, resistor_id=resistor_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ResistorCalculation.objects.get(calculation_id=calculation_id, resistor_id=resistor_id)
    item.delete()

    items = ResistorCalculation.objects.filter(calculation_id=calculation_id)
    data = [ResistorItemSerializer(item.resistor, context={"value": item.value}).data for item in items]

    return Response(data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_resistor_in_calculation(request, calculation_id, resistor_id):
    if not ResistorCalculation.objects.filter(resistor_id=resistor_id, calculation_id=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ResistorCalculation.objects.get(resistor_id=resistor_id, calculation_id=calculation_id)

    serializer = ResistorCalculationSerializer(item, data=request.data,  partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)


@api_view(["GET"])
def get_resistor_image(request, resistor_id):
    if not Resistor.objects.filter(pk=resistor_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resistor = Resistor.objects.get(pk=resistor_id)

    return HttpResponse(resistor.image, content_type="image/png")
