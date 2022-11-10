from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.pagination import CustomPagination
from recipes.models import (
    Tag, Ingredient, Recipe, ShoppingCart, Favorite, RecipeIngredient
)
from users.models import User, Follow
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (
    TagSerializer, IngredientSerializer, FavoriteAndCartSerializer,
    ReadRecipeSerializer, WriteRecipeSerializer, FollowSerializer,
    DjoserUserSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    search_fields = ('^name', )


class DjoserUserViewSet(UserViewSet):
    pagination_class = CustomPagination
    serializer_class = DjoserUserSerializer

    def get_queryset(self):
        return User.objects.all()

    @action(['get'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        user = request.user
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'Нельзя подписаться на самого себя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Follow.objects.filter(
                    user=user, author=author
            ).exists():
                return Response(
                    {'Нельзя подписаться повторно!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = Follow.objects.filter( 
            user=request.user, 
            author=author 
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'Попытка удалить несуществующую подписку!'},
            status=status.HTTP_400_BAD_REQUEST
        )


class FollowListView(ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = CustomPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )
        return serializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self.add_in_cart(ShoppingCart, request.user,
                                    recipe, pk, 'корзине покупок')
        return self.delete_in_cart(ShoppingCart, request.user,
                                   recipe, pk, 'корзине покупок')

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self.add_in_cart(Favorite, request.user,
                                    recipe, pk, 'избранном')
        return self.delete_in_cart(Favorite, request.user,
                                   recipe, pk, 'избранном')

    @staticmethod
    def add_in_cart(model, user, recipe, pk, message):
        in_cart_or_favorite = model.objects.filter(
            user=user,
            recipe=recipe
        )
        if not in_cart_or_favorite.exists():
            shopping_cart = model.objects.create(
                user=user,
                recipe=recipe
            )
            serializer = FavoriteAndCartSerializer(shopping_cart.recipe)
            return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED
                )
        return Response(
            {f'Рецепт уже в {message}.'},
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def delete_in_cart(model, user, recipe, pk, message):
        in_cart_or_favorite = model.objects.filter(
            user=user,
            recipe=recipe
        )
        if not in_cart_or_favorite.exists():
            return Response(
                {'errors': f'Такого рецепта нет в {message}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        in_cart_or_favorite.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))
        shopping_list = ('Список покупок \n\n')
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["total_amount"]}'
            for ingredient in ingredients
        ])
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="shopping_list.txt"')
        return response
