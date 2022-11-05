from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


username_validator = UnicodeUsernameValidator()


class User(AbstractUser):
    email = models.EmailField(
        'email',
        db_index=True,
        max_length=254,
        unique=True, null=False
    )
    username = models.CharField(
        'Уникальный юзернейм',
        db_index=True,
        max_length=150,
        unique=True,
        help_text=(
            "Обязательное поле. Не более 150 символов."
            "Только буквы, цифры и @/./+/-/_ ."
        ),
        validators=[username_validator],
    )
    first_name = models.CharField('Имя пользователя', max_length=150, )
    last_name = models.CharField(max_length=150, verbose_name='Фамилия', )
    password = models.CharField(max_length=150, verbose_name='Пароль', )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id', )

    def __str__(self):
        return self.email


class Follow(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='following'
                               )
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Подписчик',
                             related_name='follower'
                             )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        models.UniqueConstraint(
            fields=['author', 'user'], name='follow_unique'
        )

    def __str__(self):
        return f"{self.user} follows {self.author}"
