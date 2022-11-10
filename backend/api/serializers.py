from djoser.serializers import UserCreateSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from drf_extra_fields import Base64ImageField

from recipes.models import (
    Tag, Ingredient, ShoppingCart, Favorite, Recipe, RecipeIngredient
)
from users.models import User, Follow


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class DjoserUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'id',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class DjoserCreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password')


class ReadRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True,)
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ReadRecipeSerializer(serializers.ModelSerializer):
    author = DjoserUserSerializer(read_only=True)
    ingredients = ReadRecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipes_ingredients_list',
    )
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe__id=obj.id).exists()


class WriteRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class WriteRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = WriteRecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )
    fields_required = [
        'ingredients', 'tags',
        'image',
        'name', 'text', 'cooking_time'
    ]

    @staticmethod
    def check_empty_and_repeat(data, text):
        if not data:
            raise serializers.ValidationError(
                f'Поле {text} обязательное для заполнения'
            )
        check_list = []
        for obj in data:
            if obj in check_list:
                raise serializers.ValidationError(
                   f'Нельзя дублировать {text}!'
                )
            check_list.append(obj)

    def validate(self, data):
        data = dict(data)
        tags = data['tags']
        ingredients = data['ingredients']
        self.check_empty_and_repeat(ingredients, 'ингредиенты')
        self.check_empty_and_repeat(tags, 'теги')
        return data

    @staticmethod
    def create_ingredients(ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=get_object_or_404(
                    Ingredient,
                    id=ingredient['id']
                ),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe,
                                ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(recipe=instance,
                                ingredients=ingredients)
        return instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(
            instance,
            context={'request': self.context.get('request'), }).data


class FavoriteAndCartSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(DjoserUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, author):
        return author.recipes.count()

    def get_recipes(self, author):
        recipes = author.recipes.all()
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit'
        )
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return FavoriteAndCartSerializer(recipes, many=True).data
