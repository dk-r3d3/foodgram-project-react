from rest_framework import status
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.paginations import LimitPageNumberPagination
from users.models import Subscribtion, User
from api.serializers import SubcribeListSerializer, SubcribeSerializer


class SubcribeApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        data = {'user': request.user.id, 'author': id}
        serializer = SubcribeSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        follow = get_object_or_404(
            Subscribtion, user=user, author=author
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubcribeListAPIView(ListAPIView):
    pagination_class = LimitPageNumberPagination
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = User.objects.filter(author__user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubcribeListSerializer(
            page, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
