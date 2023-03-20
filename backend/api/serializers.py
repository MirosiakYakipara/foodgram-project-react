import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from djoser.serializers import UserSerializer, UserCreateSerializer
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from recipes.models import (Tag, Recipe, FavoriteRecipes,
                            ShoppingCart, Ingredient,
                            IngredientInRecipe)
from users.models import Follow

User = get_user_model()


class CreateUserSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    def validate(self, attrs):
        invalid_usernames = [
            'me',
            'set_password',
            'subscriptions',
        ]
        if self.initial_data.get('username').lower() in invalid_usernames:
            raise serializers.ValidationError(
                {'username': 'Нельзя использовать этот username!'}
            )
        return attrs

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserSerializer(UserSerializer):
    """Сериализатор для работы с пользователями."""
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, new_password):
        validate_password(new_password)
        return new_password

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data.get('current_password')):
            raise serializers.ValidationError(
                {'current_password': 'Неверный пароль!'}
            )
        if (validated_data.get('current_password') ==
           validated_data.get('new_password')):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от старого!'}
            )
        instance.set_password(validated_data.get('new_password'))
        instance.save()
        return validated_data


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с избранным и списком покупок."""
    def validate_is_favorited(self, attrs):
        recipe = self.instance
        user = self.context.get('request').user
        if FavoriteRecipes.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': 'Вы уже добавили этот рецепт в избранное!'})
        return attrs

    def validateis_in_shopping_cart(self, attrs):
        recipe = self.instance
        user = self.context.get('request').user
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': 'Вы уже добавили этот рецепт в список покупок!'})
        return attrs

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор для работы с подписками."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    def validate(self, attrs):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                {'errors': 'Вы уже подписаны на этого пользователя!'})
        if user == author:
            raise serializers.ValidationError(
                {'errors': 'Вы не можете подписаться на самого себя!'})
        return attrs

    def get_recipes(self, author):
        request = self.context.get('request')
        recipes = author.recipes.all()
        if 'recipes_limit' in request.GET:
            recipes_limit = request.GET.get('recipes_limit')
            recipes = recipes[:int(recipes_limit)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )


class Base64ImageField(serializers.ImageField):
    """Поле сериализатора для изображений."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с тегами."""
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингридиентами."""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингридиента и его количества в рецепте."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиента для создания рецепта."""
    id = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'amount'
        )


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        read_only=True,
        source='recipe'
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        extra_kwargs = {'is_favorited': {'required': False},
                        'is_in_shopping_cart': {'required': False}}


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    def validate(self, attrs):
        if not attrs.get('tags'):
            raise serializers.ValidationError(
                {'tags': 'Нужно указать хотя бы один тег!'}
            )
        if not attrs.get('ingredients'):
            raise serializers.ValidationError(
                {'ingredients': 'Должен быть хотя бы один ингредиент!'}
            )
        ingredients_list = [ing.get('id') for ing in attrs.get('ingredients')]
        ingredients_set = set(ingredients_list)
        if len(ingredients_list) != len(ingredients_set):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны повторяться!'}
            )
        attrs.update({
            'author': self.context.get('request').user
        })
        return attrs

    def create_ingredients(self, recipe, ingredients):
        """Метод для добавления ингридиентов в рецепт."""
        create_ingredients = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=get_object_or_404(
                    Ingredient, pk=ingredient.get('id')),
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(create_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(instance, ingredients)
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.set(tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(
            instance,
            context=self.context
        ).data

    class Meta:
        model = Recipe
        exclude = ('pub_date',)
