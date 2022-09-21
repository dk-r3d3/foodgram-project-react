from rest_framework import routers
from django.urls import include, path

from recipes.views import (
    IngredientsViewSet, TagViewSet, RecipesViewSet
)

router = routers.DefaultRouter()

router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipesViewSet, basename='recipes')

urlpatterns = [path('', include(router.urls))]
