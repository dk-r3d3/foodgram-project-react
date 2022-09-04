from django.shortcuts import get_object_or_404
from djoser import views

from rest_framework import status
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from api.serializers import CustomUserSerializer


from .models import User, Subscribtion
from api.serializers import (SubscribtionSerializer)


class UserViewSet(views.UserViewSet):
    pagination_class = PageNumberPagination
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
        permission_classes=[IsAuthenticated],
        detail=False,
        url_path=r'(?P<pk>\d+)/subscribe',
        methods=['post']
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)
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
        Subscribtion.objects.create(user=user, author=author)
        return Response(
            SubscribtionSerializer(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        subscription = Subscribtion.objects.filter(
            user=request.user, author=user
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscriber__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribtionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
