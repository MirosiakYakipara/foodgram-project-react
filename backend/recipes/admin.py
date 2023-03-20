from django.contrib import admin
from django.utils.safestring import mark_safe
from sorl.thumbnail import get_thumbnail

from .models import (Tag, Ingredient, IngredientInRecipe, Recipe,
                     FavoriteRecipes, ShoppingCart)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка тега для админке."""
    list_display = (
        'name',
        'color',
        'slug'
    )
    search_fields = ('name', )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка ингридиента для админке."""
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = (
        'name__istartswith',
    )
    fieldsets = (
        (None, {
            'fields': (
                'name', 'measurement_unit'
            )
        }),
    )


class IngInRecipeAdmin(admin.TabularInline):
    """Чтобы добавлять ингридиенты на странице рецепта."""
    model = IngredientInRecipe
    min_num = 1
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка рецепта для админке."""
    list_display = (
        'name',
        'get_image',
        'author',
        'added_favorites'
    )
    list_filter = (
        'author',
        'tags__name'
    )
    search_fields = (
        'name__istartswith',
    )
    filter_horizontal = ('tags', )
    inlines = (IngInRecipeAdmin, )
    fields = (
        'name',
        'author',
        'text',
        'tags',
        'cooking_time',
        'image',
    )
    readonly_fields = ('added_favorites', )

    def get_image(self, obj):
        im = get_thumbnail(obj.image, '75x75', crop='center', quality=99)
        return mark_safe(f"<img src={im.url}/>")
    get_image.short_description = 'Изображение рецепта'

    def added_favorites(self, obj):
        return obj.favorite_recipe.count()

    added_favorites.short_description = 'Добавили в избранное'


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Настройка ингридиента в рецепте для админке."""
    list_display = (
        'recipe',
        'ingredient',
        'amount'
    )
    search_fields = (
        'recipe__istartswith',
    )


@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):
    """Настройка избранного для админке."""
    list_display = (
        'user',
        'recipe'
    )
    search_fields = (
        'user__istartswith',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройка списка покупок для админке."""
    list_display = (
        'user',
        'recipe'
    )
    search_fields = (
        'user__istartswith',
    )
