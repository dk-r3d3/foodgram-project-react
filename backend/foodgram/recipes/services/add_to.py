from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db import IntegrityError
from recipes.models import Favorites
from recipes.serializers import RecipesReadSerializer
from recipes.models import Recipes


def post_or_del_method(method, user, pk, model):
    """Метод для добавления/удаления"""
    recipe = get_object_or_404(Recipes, pk=pk)
    if method == 'POST':
        try:
            model.objects.create(user=user, recipe=recipe)
        except IntegrityError:
            return Response(
                {status.ERRORS_KEY: 'Рецепт уже добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = RecipesReadSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    if method == 'DELETE':
        favorite = Favorites.objects.filter(user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
