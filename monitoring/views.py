# monitoring/views.py

from rest_framework import generics, viewsets, status
from .serializers import UserSerializer, PVSystemSerializer, ElectricalDataSerializer, MeteorologicalDataSerializer
from django.contrib.auth.models import User
from django.db.models import Sum, F
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import PVSystem, ElectricalData, MeteorologicalData
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
import pandas as pd
import pvlib
import numpy as np  # Import numpy


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(username=response.data['username'])
        user.is_staff = True  # Marking the user as admin
        user.save()
        return response

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        # Exclude admin accounts from the queryset
        return User.objects.filter(is_staff=False)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class CustomTokenObtainPairView(TokenObtainPairView):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_type'] = 'admin' if user.is_staff else 'user'
        return token

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = User.objects.get(username=request.data['username'])
        response.data['user_type'] = 'admin' if user.is_staff else 'user'
        return response

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_simple_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.is_staff = False
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calculate_pvwatts(request, system_id):
    try:
        system = PVSystem.objects.get(id=system_id)
    except PVSystem.DoesNotExist:
        raise NotFound('System not found')

    # Filter electrical data for the system
    electrical_data = ElectricalData.objects.filter(system=system)

    if not electrical_data.exists():
        return Response({'error': 'No electrical data found for this system'})

    # Get the time range from the electrical data
    start_time = electrical_data.order_by('time').first().time
    end_time = electrical_data.order_by('-time').first().time

    # Filter meteorological data within the time range
    meteorological_data = MeteorologicalData.objects.filter(time__range=(start_time, end_time))

    if not meteorological_data.exists():
        return Response({'error': 'No meteorological data found for the given time range'})

    # Convert to DataFrame for easy manipulation
    electrical_df = pd.DataFrame.from_records(electrical_data.values())
    meteorological_df = pd.DataFrame.from_records(meteorological_data.values())

    # Ensure both dataframes have time as the index
    electrical_df.set_index('time', inplace=True)
    meteorological_df.set_index('time', inplace=True)

    # Resample to ensure consistent intervals and fill missing values
    electrical_df = electrical_df.resample('5min').mean().interpolate()
    meteorological_df = meteorological_df.resample('5min').mean().interpolate()

    # Merge the dataframes
    merged_df = pd.merge_asof(electrical_df, meteorological_df, left_index=True, right_index=True)

    # Calculate power using PVWatts model
    p_stc = system.capacity * 1000  # Convert kW to W
    temp_coeff = -0.005  # Assuming a typical temperature coefficient

    results = []
    for index, row in merged_df.iterrows():
        gti = row['gti']
        air_temp = row['air_temp']
        wind_speed = row['wind_speed']

        if gti <= 0:
            results.append({
                'time': index,
                'calculated_power': 0,
                'current_t1': row.get('t1', None),
                'current_t2': row.get('t2', None),
                'voltage': row.get('u_dc', None),
                'gti': gti,
                'air_temp': air_temp
            })
            continue

        # Calculate cell temperature
        temp_cell = pvlib.temperature.pvsyst_cell(
            poa_global=gti,
            temp_air=air_temp,
            wind_speed=wind_speed
        )

        # Calculate DC power using PVWatts model
        p_dc = pvlib.pvsystem.pvwatts_dc(gti, temp_cell, p_stc, gamma_pdc=temp_coeff)

        # Ensure the calculated power is within valid range
        if not np.isfinite(p_dc) or np.isnan(p_dc):
            p_dc = 0  # Set to zero if the value is not finite or NaN

        results.append({
            'time': index,
            'calculated_power': p_dc,
            'current_t1': row.get('t1', None),
            'current_t2': row.get('t2', None),
            'voltage': row.get('u_dc', None),
            'gti': gti,
            'air_temp': air_temp
        })

    # Sanitize the results to ensure all values are JSON compliant
    for result in results:
        for key, value in result.items():
            if isinstance(value, float) and (np.isnan(value) or not np.isfinite(value)):
                result[key] = 0  # Set invalid float values to zero

    return Response(results)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calculate_system_scores(request):
    systems = PVSystem.objects.all()
    scores = []

    for system in systems:
        # Filter electrical data for the system
        electrical_data = ElectricalData.objects.filter(system=system)

        if not electrical_data.exists():
            continue

        # Get the time range from the electrical data
        start_time = electrical_data.order_by('time').first().time
        end_time = electrical_data.order_by('-time').first().time

        # Filter meteorological data within the time range
        meteorological_data = MeteorologicalData.objects.filter(time__range=(start_time, end_time))

        if not meteorological_data.exists():
            continue

        # Convert to DataFrame for easy manipulation
        electrical_df = pd.DataFrame.from_records(electrical_data.values())
        meteorological_df = pd.DataFrame.from_records(meteorological_data.values())

        # Ensure both dataframes have time as the index
        electrical_df.set_index('time', inplace=True)
        meteorological_df.set_index('time', inplace=True)

        # Resample to ensure consistent intervals and fill missing values
        electrical_df = electrical_df.resample('5min').mean().interpolate()
        meteorological_df = meteorological_df.resample('5min').mean().interpolate()

        # Merge the dataframes
        merged_df = pd.merge_asof(electrical_df, meteorological_df, left_index=True, right_index=True)

        # Calculate power using PVWatts model
        p_stc = system.capacity * 1000  # Convert kW to W
        temp_coeff = -0.005  # Assuming a typical temperature coefficient

        total_power_produced = 0
        for index, row in merged_df.iterrows():
            gti = row['gti']
            air_temp = row['air_temp']
            wind_speed = row['wind_speed']

            if gti <= 0:
                continue

            # Calculate cell temperature
            temp_cell = pvlib.temperature.pvsyst_cell(
                poa_global=gti,
                temp_air=air_temp,
                wind_speed=wind_speed
            )

            # Calculate DC power using PVWatts model
            p_dc = pvlib.pvsystem.pvwatts_dc(gti, temp_cell, p_stc, gamma_pdc=temp_coeff)

            # Ensure the calculated power is within valid range
            if np.isfinite(p_dc) and not np.isnan(p_dc):
                total_power_produced += p_dc
                print(f"Total power produced: {total_power_produced}")


        # Normalize power by system capacity and number of panels
        normalized_power = total_power_produced / (system.capacity * 1000 * system.number_of_panels)

        # Apply scaling factor
        score = min(max(normalized_power * 20, 0), 20)  # Adjusting the factor to 20 for better distribution

        scores.append({
            'system_id': system.id,
            'name': system.name,
            'score': score,
            'capacity': system.capacity,
            'num_panels': system.number_of_panels
        })

    return Response(scores)
