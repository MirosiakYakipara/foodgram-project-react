from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response


class ListRetriveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет на получение одного или нескольких объектов."""
    ...


class CreateAndDeleteMixin:
    """
    Миксин для добавления и удаления подписки,
    рецепта в избранное, рецепта в список покупок.
    """
    def create_and_delete(self,
                          pk,
                          klass,
                          field):
        qs_obj = get_object_or_404(self.get_queryset(), pk=pk)
        kwargs = {
            'user': self.request.user,
            field: qs_obj
        }
        if self.request.method == 'POST':
            context = self.get_serializer_context()
            serializer = self.get_serializer_class()(
                qs_obj, data=kwargs, context=context
            )
            serializer.is_valid(raise_exception=True)
            klass.objects.create(**kwargs)
            response = Response(
                serializer.data,
                status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            get_object_or_404(klass, **kwargs).delete()
            response = Response(status=status.HTTP_204_NO_CONTENT)
        return response
