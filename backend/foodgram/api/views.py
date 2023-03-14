from django.db.models import F, Sum
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from djoser.views import UserViewSet

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from .mixins import (CreateAndDeleteMixin, ListRetriveViewSet)
from .paginators import LimitPageNumberPagination
from .permissions import (IsAdminOrOwner, IsAdminOrReadOnly,
                          IsAuthenticatedOrAdminOrReadOnly)
from .serializers import (TagSerializer, SubscribeSerializer,
                          RecipeSerializer, IngredientSerializer,
                          CreateRecipeSerializer, ReadRecipeSerializer,)
from users.models import Follow
from recipes.models import (Tag, Recipe, Ingredient, IngredientInRecipe,
                            FavoriteRecipes, ShoppingCart)

User = get_user_model()


class CustomUserViewSet(UserViewSet, CreateAndDeleteMixin):
    pagination_class = LimitPageNumberPagination

    def get_permissions(self):
        if self.action in ('subscriptions', 'subscribe'):
            return (IsAuthenticated(), )
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('subscriptions', 'subscribe'):
            return SubscribeSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=['get'],
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        context = self.get_serializer_context()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer_class()(
            page, many=True,
            context=context
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)
        if user == author:
            raise ValidationError({'errors': 'Нельзя подписаться на себя!'})
        return self.create_and_delete(
            pk=id,
            klass=Follow,
            create_failed_msg='Не удалось подписаться на автора!',
            delete_failed_msg='Не удалось отписаться от автора!',
            field='author'
        )


class TagViewSet(ListRetriveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly, )


class IngredientViewSet(ListRetriveViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def get_queryset(self):
        qs = Ingredient.objects
        name = self.request.query_params.get('name', None)
        if name:
            qs = qs.filter(name__istartswith=name)
        return qs.all()


class RecipeViewSet(viewsets.ModelViewSet, CreateAndDeleteMixin):
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        qs = Recipe.objects
        tags = self.request.query_params.getlist('tags', None)
        user = self.request.user
        author = self.request.query_params.get('author', None)
        is_favorited = self.request.query_params.get('is_favorited', None)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart',
            None
        )

        if tags:
            qs = qs.filter(tags__slug__in=tags).distinct()
        if author:
            qs = qs.filter(author=author)
        if user.is_anonymous:
            return qs

        if is_favorited:
            if is_favorited == '1':
                qs = qs.filter(favorite_recipe__user=user)
            elif is_favorited == '0':
                qs = qs.exclude(favorite_recipe__user=user)
        if is_in_shopping_cart:
            if is_in_shopping_cart == '1':
                qs = qs.filter(shopping_cart_recipe__user=user)
            elif is_in_shopping_cart == '0':
                qs = qs.exclude(shopping_cart_recipe__user=user)
        return qs.all()

    def get_permissions(self):
        if self.action in ('partial_update', 'destroy'):
            return (IsAdminOrOwner(), )
        return (IsAuthenticatedOrAdminOrReadOnly(), )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        elif self.action in ('favorite', 'shopping_cart'):
            return RecipeSerializer
        return CreateRecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete']
    )
    def favorite(self, request, pk=None):
        return self.create_and_delete(
            pk=pk,
            klass=FavoriteRecipes,
            create_failed_msg='Не удалось добавить рецепт в избранное!',
            delete_failed_msg='Не удалось удалить рецепт из избранного!',
            field='recipe'
        )

    @action(
        detail=True,
        methods=['post', 'delete']
    )
    def shopping_cart(self, request, pk=None):
        return self.create_and_delete(
            pk=pk,
            klass=ShoppingCart,
            create_failed_msg='Не удалось добавить рецепт в список покупок!',
            delete_failed_msg='Не удалось удалить рецепт из списка покупок!',
            field='recipe'
        )

    @action(
            detail=False,
            methods=['get']
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart_recipe__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit'),
            total=Sum('amount')
        ).order_by('-total')

        text = '\n'.join([
            f"{ing['name']} {ing['units']} - {ing['total']}"
            for ing in ingredients
        ])
        filename = 'foodgram-shopping-cart.txt'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
