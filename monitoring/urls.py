# monitoring/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import PVSystemViewSet, ElectricalDataViewSet, MeteorologicalDataViewSet, UserCreate, create_simple_user, calculate_pvwatts, calculate_system_scores, UserViewSet, CustomTokenObtainPairView, get_total_calculated_power, get_system_totals
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(r'pvsystems', PVSystemViewSet)
router.register(r'electricaldata', ElectricalDataViewSet)
router.register(r'meteorologicaldata', MeteorologicalDataViewSet)
router.register(r'users', UserViewSet, basename='user')  # Register the UserViewSet with basename

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register-admin/', UserCreate.as_view(), name='admin-create'),
    path('api/register-user/', create_simple_user, name='user-create'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/pvsystems/<int:system_id>/calculate/', calculate_pvwatts, name='calculate_pvwatts'),
    path('api/pvsystems/scores/', calculate_system_scores, name='system_scores'),
    path('api/totals-p_dc/', get_total_calculated_power, name='get_total_calculated_power'),  
    path('api/system-totals/', get_system_totals, name='system_totals'),


]
