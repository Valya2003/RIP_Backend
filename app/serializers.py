from rest_framework import serializers

from .models import *


class ResistorsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, resistor):
        if resistor.image:
            return resistor.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Resistor
        fields = ("id", "name", "status", "resistance", "image")


class ResistorSerializer(ResistorsSerializer):
    class Meta(ResistorsSerializer.Meta):
        model = Resistor
        fields = ResistorsSerializer.Meta.fields + ("description", )


class CalculationsSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Calculation
        fields = "__all__"


class CalculationSerializer(CalculationsSerializer):
    resistors = serializers.SerializerMethodField()
            
    def get_resistors(self, calculation):
        items = ResistorCalculation.objects.filter(calculation=calculation)
        return [ResistorItemSerializer(item.resistor, context={"count": item.count}).data for item in items]


class ResistorItemSerializer(ResistorSerializer):
    count = serializers.SerializerMethodField()

    def get_count(self, resistor):
        return self.context.get("count")

    class Meta(ResistorSerializer.Meta):
        fields = "__all__"


class ResistorCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResistorCalculation
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
