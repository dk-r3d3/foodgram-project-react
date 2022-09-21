from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from recipes.models import Recipes
from api.serializers import RecipesReadSerializer


def post_or_del_method(method, user, pk, model):
    """Метод для добавления/удаления"""

    recipe = get_object_or_404(Recipes, pk=pk)
    if method == 'POST':
        model.objects.get_or_create(user=user, recipe=recipe)
        serializer = RecipesReadSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    instance = get_object_or_404(model, user=user, recipe=recipe)
    instance.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
