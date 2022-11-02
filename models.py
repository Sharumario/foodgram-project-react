from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField('email', unique=True, null=False)
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        ordering = ('-id', )

    def __str__(self):
        return self.email

class Follow(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  verbose_name='Подписка',
                                  related_name='following')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Подписчик',
                             related_name='follower')

    class Meta:
        verbose_name = 'Подписки'
        models.UniqueConstraint(
            fields=['following', 'user'], name='follow_unique'
        )

    def __str__(self):
        return f"{self.user} follows {self.following}"

