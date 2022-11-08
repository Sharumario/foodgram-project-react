from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DjoserUserViewSet, TagViewSet, IngredientViewSet,
    RecipeViewSet, FollowListView,
)


app_name = 'api'
router_v1 = DefaultRouter()
router_v1.register('users', DjoserUserViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tag')
router_v1.register('ingredient', IngredientViewSet, basename='ingredient')
router_v1.register('recipe', RecipeViewSet, basename='recipe')
urlpatterns = [
    path('users/subscriptions/', FollowListView.as_view()),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
