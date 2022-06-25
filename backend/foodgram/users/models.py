from django.contrib.auth.models import AbstractUser
from django.db import models

USER = 'user'
ADMIN = 'admin'
ROLES = (
    (USER, 'Пользователь'),
    (ADMIN, 'Администратор')
)


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта',
        help_text='Адрес электронной почты пользователя'
    )
    username = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Псевдоним',
        help_text='Псевдоним пользователя'
    )
    role = models.CharField(
        max_length=200,
        choices=ROLES,
        default=USER,
        verbose_name='Роль',
        help_text='Административная роль пользователя'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя',
        help_text='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия',
        help_text='Фамилия пользователя'
    )
    password = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Пароль',
        help_text='Пароль пользователя'
    )
