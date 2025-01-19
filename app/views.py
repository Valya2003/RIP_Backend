import random
from datetime import datetime, timedelta
import uuid

from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .permissions import *
from .redis import session_storage
from .serializers import *
from .utils import identity_user, get_session


def get_draft_calculation(request):
    user = identity_user(request)

    if user is None:
        return None

    calculation = Calculation.objects.filter(owner=user).filter(status=1).first()

    return calculation


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'resistor_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_resistors(request):
    resistor_name = request.GET.get("resistor_name", "")

    resistors = Resistor.objects.filter(status=1)

    if resistor_name:
        resistors = resistors.filter(name__icontains=resistor_name)

    serializer = ResistorsSerializer(resistors, many=True)

    draft_calculation = get_draft_calculation(request)

    resp = {
        "resistors": serializer.data,
        "resistors_count": ResistorCalculation.objects.filter(calculation=draft_calculation).count() if draft_calculation else None,
        "draft_calculation_id": draft_calculation.pk if draft_calculation else None
    }

    return Response(resp)


@api_view(["GET"])
def get_resistor_by_id(request, resistor_id):
    if not Resistor.objects.filter(pk=resistor_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resistor = Resistor.objects.get(pk=resistor_id)
    serializer = ResistorSerializer(resistor)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=ResistorSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_resistor(request, resistor_id):
    if not Resistor.objects.filter(pk=resistor_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resistor = Resistor.objects.get(pk=resistor_id)

    serializer = ResistorSerializer(resistor, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='POST', request_body=ResistorAddSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def create_resistor(request):
    serializer = ResistorSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    resistor = Resistor.objects.create(**serializer.validated_data)

    image = request.data.get("image")
    if image is not None:
        resistor.image = image
        resistor.save()

    resistors = Resistor.objects.filter(status=1)
    serializer = ResistorSerializer(resistors, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_resistor(request, resistor_id):
    if not Resistor.objects.filter(pk=resistor_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resistor = Resistor.objects.get(pk=resistor_id)
    resistor.status = 2
    resistor.save()

    resistor = Resistor.objects.filter(status=1)
    serializer = ResistorSerializer(resistor, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_resistor_to_calculation(request, resistor_id):
    if not Resistor.objects.filter(pk=resistor_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resistor = Resistor.objects.get(pk=resistor_id)

    draft_calculation = get_draft_calculation(request)

    if draft_calculation is None:
        draft_calculation = Calculation.objects.create()
        draft_calculation.date_created = timezone.now()
        draft_calculation.owner = identity_user(request)
        draft_calculation.status = CalculationStatus.objects.get(pk=1)
        draft_calculation.save()

    if ResistorCalculation.objects.filter(calculation=draft_calculation, resistor=resistor).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = ResistorCalculation.objects.create()
    item.calculation = draft_calculation
    item.resistor = resistor
    item.save()

    serializer = CalculationSerializer(draft_calculation)
    return Response(serializer.data["resistors"])


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE),
    ]
)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def update_resistor_image(request, resistor_id):
    if not Resistor.objects.filter(pk=resistor_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resistor = Resistor.objects.get(pk=resistor_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    resistor.image = image
    resistor.save()

    serializer = ResistorSerializer(resistor)

    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'date_formation_start',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'date_formation_end',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_calculations(request):
    status_name = request.GET.get("status", "Не указан")
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    calculations = Calculation.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        calculations = calculations.filter(owner=user)

    if status_name != "Не указан":
        calculations = calculations.filter(status=CalculationStatus.objects.get(name=status_name))

    if date_formation_start and parse_datetime(date_formation_start):
        calculations = calculations.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        calculations = calculations.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = CalculationsSerializer(calculations, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_calculation_by_id(request, calculation_id):
    user = identity_user(request)

    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)

    if not user.is_superuser and calculation.owner != user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = CalculationSerializer(calculation)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=CalculationSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_calculation(request, calculation_id):
    user = identity_user(request)

    if not Calculation.objects.filter(pk=calculation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)
    serializer = CalculationSerializer(calculation, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, calculation_id):
    user = identity_user(request)

    if not Calculation.objects.filter(pk=calculation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != CalculationStatus.objects.get(pk=1):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation.status = CalculationStatus.objects.get(pk=2)
    calculation.date_formation = timezone.now()
    calculation.save()

    serializer = CalculationSerializer(calculation)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=UpdateHistoryStatusAdminSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = request.data["status"]

    if request_status not in ["Завершен", "Отклонен"]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != CalculationStatus.objects.get(pk=2):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == "Завершен":
        calculation.current = random.randint(1, 10)

    calculation.status = CalculationStatus.objects.get(name=request_status)
    calculation.date_complete = timezone.now()
    calculation.moderator = identity_user(request)
    calculation.save()

    serializer = CalculationSerializer(calculation)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_calculation(request, calculation_id):
    user = identity_user(request)

    if not Calculation.objects.filter(pk=calculation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != CalculationStatus.objects.get(pk=1):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation.status = CalculationStatus.objects.get(pk=5)
    calculation.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_resistor_from_calculation(request, calculation_id, resistor_id):
    user = identity_user(request)

    if not Calculation.objects.filter(pk=calculation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not ResistorCalculation.objects.filter(calculation_id=calculation_id, resistor_id=resistor_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ResistorCalculation.objects.get(calculation_id=calculation_id, resistor_id=resistor_id)
    item.delete()

    calculation = Calculation.objects.get(pk=calculation_id)

    serializer = CalculationSerializer(calculation)
    resistors = serializer.data["resistors"]

    return Response(resistors)


@swagger_auto_schema(method='PUT', request_body=ResistorCalculationSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_resistor_in_calculation(request, calculation_id, resistor_id):
    user = identity_user(request)

    if not Calculation.objects.filter(pk=calculation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not ResistorCalculation.objects.filter(resistor_id=resistor_id, calculation_id=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ResistorCalculation.objects.get(resistor_id=resistor_id, calculation_id=calculation_id)

    serializer = ResistorCalculationSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    user = identity_user(request)

    if serializer.is_valid():
        user = authenticate(**serializer.data)
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        session_id = str(uuid.uuid4())
        session_storage.set(session_id, user.id)

        serializer = UserSerializer(user)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        response.set_cookie("session_id", session_id, samesite="lax")

        return response

    if user is not None:
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@swagger_auto_schema(method='PUT', request_body=UserProfileSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    password = request.data.get("password", None)
    if password is not None and not user.check_password(password):
        user.set_password(password)
        user.save()

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_resistor_image(request, resistor_id):
    if not Resistor.objects.filter(pk=resistor_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    resistor = Resistor.objects.get(pk=resistor_id)

    return HttpResponse(resistor.image, content_type="image/png")
