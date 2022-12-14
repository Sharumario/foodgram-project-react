from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DjoserUserViewSet, FollowListView, IngredientViewSet,
    RecipeViewSet, TagViewSet
)


app_name = 'api'
router_v1 = DefaultRouter()
router_v1.register('users', DjoserUserViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tag')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
urlpatterns = [
    path(
        'users/subscriptions/', FollowListView.as_view(), name='subscriptions'
        ),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
