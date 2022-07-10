from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.constraints import UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название тега'
    )
    color = models.CharField(
        max_length=20,
        verbose_name='Цвет',
        help_text='Цвет тега',
        unique=True
    )
    slug = models.SlugField(
        max_length=200,
        unique=True
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Название единицы измерения',
        help_text='Единица измерения ингредиента'
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название рецепта'
    )
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
        )
    image = models.ImageField(
        upload_to='media',
        null=True,
        blank=True
        )

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        blank=True
    )
    cooking_time = models.IntegerField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipeAmount',
        verbose_name='Ингредиенты'
    )

    def __str__(self):
        return self.name


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'author'], name='unique_follow')
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты'
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='starred',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='starred_by',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourite'
                )
        ]


class IngredientRecipeAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_amount',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField()
