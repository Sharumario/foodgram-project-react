from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from recipes.models import Tag, Ingredient
from users.models import User, Follow


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class DjoserUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

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
