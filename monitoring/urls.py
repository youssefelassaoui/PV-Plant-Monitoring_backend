# monitoring/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import PVSystemViewSet, ElectricalDataViewSet, MeteorologicalDataViewSet, UserCreate
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
router = DefaultRouter()
router.register(r'pvsystems', PVSystemViewSet)
router.register(r'electricaldata', ElectricalDataViewSet)
router.register(r'meteorologicaldata', MeteorologicalDataViewSet)

urlpatterns = [
    path('api/register/', UserCreate.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/', include(router.urls)),  # Include router URLs here

]
