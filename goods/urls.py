from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(prefix="packages", viewset=views.PackageViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("types/", views.TypeListAPIView.as_view(), name="types"),
]
