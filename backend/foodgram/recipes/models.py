from colorfield.fields import ColorField
from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингридиента',
        max_length=200
    )
    measurement_unit = models.SlugField(
        verbose_name='Единица измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200
    )
    color = ColorField(
        verbose_name='Цвет тега',
        format='hexa'
    )
    slug = models.SlugField(
        verbose_name='Описание тега',
        max_length=200,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        through='IngredientInRecipe'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингридиент',
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингридиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingridient_in_recipe'
            )
        ]

    def __str__(self):
        return (f'{self.recipe.name}: '
                f'{self.ingredient.name} - {self.amount} '
                f'{self.ingredient.measurement_unit}')


class FavoriteRecipes(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт в избранном'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            ),
        ]

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name} в избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipe',
        verbose_name='Рецепт в списке покупок'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            ),
        ]

    def __str__(self):
        return (f'{self.user.username} добавил '
                f'{self.recipe.name} в список покупок')
