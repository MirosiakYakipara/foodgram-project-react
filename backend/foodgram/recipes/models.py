from colorfield.fields import ColorField

from django.db import models
from django.core.validators import RegexValidator, MinValueValidator

from users.models import User
from core.enum import Regex, Message, MinLimit


class IngredientQuerySet(models.QuerySet):
    """QuerySet для ингридиентов."""
    def filter_by_name(self, name):
        """Метод для фильтрации по названию ингридиента."""
        return self.filter(name__istartswith=name).order_by('name')


class Ingredient(models.Model):
    """Модель ингридиента."""
    name = models.CharField(
        verbose_name='Название ингридиента',
        max_length=200
    )
    measurement_unit = models.SlugField(
        verbose_name='Единица измерения',
        max_length=200
    )

    objects = IngredientQuerySet.as_manager()

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_measurement_unit_and_name'
            )
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        unique=True,
        validators=(RegexValidator(
            regex=Regex.RU_REGEX,
            message=Message.TAG_NAME_MESSAGE), )
    )
    color = ColorField(
        verbose_name='Цвет тега',
        format='hex'
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


class RecipeQuerySet(models.QuerySet):
    """QuerySet для рецепта."""
    def filter_by_tags(self, tags):
        """Метод для фильтрации по тегам."""
        return self.filter(
            tags__slug__in=tags).distinct().order_by('-pub_date')

    def add_annotations(self, user_id):
        """
        Метод для добавления новых полей в модель рецепта при помощи annotate.
        """
        return self.annotate(
            recipes_count=models.Count('recipe'),
            is_favorited=models.Exists(
                FavoriteRecipes.objects.filter(
                    user_id=user_id, recipe__pk=models.OuterRef('pk')
                )
            ),
            is_in_shopping_cart=models.Exists(
                ShoppingCart.objects.filter(
                    user_id=user_id, recipe__pk=models.OuterRef('pk')
                )
            ),
        )

    def filter_in_favorite(self, is_favorited):
        """Метод для фильтрации по избранным."""
        if is_favorited == '1':
            return self.filter(
                is_favorited=True).order_by('-pub_date')
        elif is_favorited == '0':
            return self.exclude(
                is_favorited=False).order_by('-pub_date')

    def filter_in_shopping_cart(self, is_in_shopping_cart):
        """Метод для фильтрации по списку покупок."""
        if is_in_shopping_cart == '1':
            return self.filter(
                is_in_shopping_cart=True).order_by('-pub_date')
        elif is_in_shopping_cart == '0':
            return self.exclude(
                is_in_shopping_cart=False).order_by('-pub_date')

    def filter_by_author(self, author):
        """Метод для фильтрации по автору."""
        return self.filter(author=author).order_by('-pub_date')


class Recipe(models.Model):
    """Модель рецепта."""
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
        validators=(MinValueValidator(
            limit_value=MinLimit.MIN_COOKING_TIME,
            message=Message.MIN_COOKING_TIME_MESSAGE), )
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True
    )

    objects = RecipeQuerySet.as_manager()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модель ингридиента в рецепте."""
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
        verbose_name='Количество',
        validators=(MinValueValidator(
            limit_value=MinLimit.MIN_AMOUNT,
            message=Message.MIN_AMOUNT_MESSAGE), )
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
    """Модель избранного."""
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
    """Модель списка покупок."""
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
