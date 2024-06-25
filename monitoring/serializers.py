# monitoring/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PVSystem, ElectricalData, MeteorologicalData

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class PVSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PVSystem
        fields = '__all__'

class ElectricalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectricalData
        fields = '__all__'

class MeteorologicalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeteorologicalData
        fields = '__all__'
