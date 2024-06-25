# monitoring/views.py

from rest_framework import generics, viewsets
from .serializers import UserSerializer, PVSystemSerializer, ElectricalDataSerializer, MeteorologicalDataSerializer
from django.contrib.auth.models import User
from .models import PVSystem, ElectricalData, MeteorologicalData
from rest_framework.permissions import IsAuthenticated

class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PVSystemViewSet(viewsets.ModelViewSet):
    queryset = PVSystem.objects.all()
    serializer_class = PVSystemSerializer
    permission_classes = [IsAuthenticated]

class ElectricalDataViewSet(viewsets.ModelViewSet):
    queryset = ElectricalData.objects.all()
    serializer_class = ElectricalDataSerializer
    permission_classes = [IsAuthenticated]

class MeteorologicalDataViewSet(viewsets.ModelViewSet):
    queryset = MeteorologicalData.objects.all()
    serializer_class = MeteorologicalDataSerializer
    permission_classes = [IsAuthenticated]
