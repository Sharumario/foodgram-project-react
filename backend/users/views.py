from djoser.views import UserViewSet
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (
    AllowAny, IsAuthenticated
)
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer
from api.pagination import CustomPagination


class DjoserUserViewSet(UserViewSet):
    pagination_class = CustomPagination

    def get_queryset(self):
        return User.objects.all()
    
    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)
