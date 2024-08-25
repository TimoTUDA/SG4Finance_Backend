from django.urls import path, include
from rest_framework import routers
from .views import GameViewSet, RoundViewSet, InvestmentViewSet

from app import views

router = routers.DefaultRouter()
router.register(r'game', GameViewSet)
router.register(r'round', RoundViewSet)
router.register(r'investment', InvestmentViewSet)

app_name = 'app'
urlpatterns = router.urls
