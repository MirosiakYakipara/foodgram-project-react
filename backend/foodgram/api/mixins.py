from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework import mixins, viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


class ListRetriveCreateViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    pass


class ListRetriveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CreateAndDeleteMixin:
    def create_and_delete(self,
                          pk,
                          klass,
                          create_failed_msg,
                          delete_failed_msg,
                          field):
        qs_obj = get_object_or_404(self.get_queryset(), pk=pk)
        kwargs = {
            'user': self.request.user,
            field: qs_obj
        }
        if self.request.method == 'POST':
            try:
                klass.objects.create(**kwargs)
            except IntegrityError:
                raise ValidationError({'errors': create_failed_msg})
            context = self.get_serializer_context()
            serializer = self.get_serializer_class()
            response = Response(
                serializer(instance=qs_obj, context=context).data,
                status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            try:
                get_object_or_404(klass, **kwargs).delete()
            except IntegrityError:
                raise ValidationError({'errors': delete_failed_msg})
            response = Response(status=status.HTTP_204_NO_CONTENT)

        else:
            raise ValidationError({'errors': 'Неверный метод запроса!'})
        return response
