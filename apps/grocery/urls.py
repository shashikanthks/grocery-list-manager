from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroceryListViewSet, GroceryItemViewSet

router = DefaultRouter()
router.register(r'lists', GroceryListViewSet, basename='grocerylist')
router.register(r'items', GroceryItemViewSet, basename='groceryitem')

urlpatterns = [
    path('', include(router.urls)),
]