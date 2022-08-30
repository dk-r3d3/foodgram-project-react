from django.shortcuts import get_object_or_404
from djoser import views

from rest_framework import status
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.decorators import action
from rest_framework.response import Response

# импорты внутри проекта
from .models import User, Subscribtion
from api.serializers import (SubscribtionSerializer)
from api.paginations import LimitPageNumberPagination


class UserViewSet(views.UserViewSet):  # вьюсет для работы с пользователем
    pagination_class = LimitPageNumberPagination

    @action(
        permission_classes=[IsAuthenticated],
        detail=True,
        methods=['POST']
    )
    def subscribe(self, request, id=None):  # метод для создания подписки
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response(
                {'error': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Subscribtion.objects.filter(
                user=user, author=author
        ).exists():
            return Response(
                {'error': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscribe = Subscribtion.objects.create(user=user, author=author)
        serializer = SubscribtionSerializer(
            subscribe, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):  # метод для отписки от автора
        user = get_object_or_404(User, id=id)
        subscription = Subscribtion.objects.filter(
            user=request.user, author=user
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        methods=['GET']
    )
    def subscribtions(self, request):   # метод для получения данных о подписке
        user = request.user
        queryset = User.objects.filter(subscriber__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribtionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
