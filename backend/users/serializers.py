from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer

from .models import User, Follow


class DjoserUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class DjoserCreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'password')
