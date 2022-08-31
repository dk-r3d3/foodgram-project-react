from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from recipes.models import Favorites, Recipes
from api.serializers import RecipesReadSerializer


def post_or_del_method(method, user, pk, model):
    """Метод для добавления/удаления"""
    recipe = get_object_or_404(Recipes, pk=pk)
    if method == 'POST':
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipesReadSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if method == 'DELETE':
        favorite = Favorites.objects.filter(user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
