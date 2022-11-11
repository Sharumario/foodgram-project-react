from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


COOKING_TIME_MIN_VALUE = 1
INGREDIENTS_MIN_VALUE = 1
MESSAGE_COOKING_TIME_MIN = 'Минимальное время приготовления 1 минута'
MESSAGE_INGREDIENTS_MIN_VALUE = 'Минимальное количество ингридиентов 1'


class Tag(models.Model):
    name = models.CharField('Название тэга', max_length=150, unique=True)
    color = models.CharField('Цвет в HEX', max_length=7, unique=True)
    slug = models.SlugField('Слаг', max_length=150, unique=True)

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название ингредиента', max_length=150)
    measurement_unit = models.CharField('Единица измерения', max_length=150)

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=200)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты ',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipes',
    )
    image = models.ImageField('Картинка', upload_to='recipies/', )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True,
                                    db_index=True)
    text = models.TextField('Описание рецепта')
    cooking_time = models.PositiveIntegerField(
        default=1,
        verbose_name='Время готовки',
        validators=(MinValueValidator(
            COOKING_TIME_MIN_VALUE,
            message=MESSAGE_COOKING_TIME_MIN
        ),)
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_ingredients_list',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=(MinValueValidator(
                INGREDIENTS_MIN_VALUE,
                message=MESSAGE_INGREDIENTS_MIN_VALUE
        ),),
        verbose_name='Количество',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique ingredients recipe'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='favorite_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} favorite: {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='shopping_cart',
                             verbose_name='Пользоавтель')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='shopping_cart',
                               verbose_name='Покупка')

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='shopping_cart_unique'
            )
        ]

    def __str__(self):
        return f'In {self.user} shopping cart: {self.recipe}'
