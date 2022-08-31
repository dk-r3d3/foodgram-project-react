from rest_framework import routers
from django.urls import include, path, re_path

from recipes.views import (
    IngredientsViewSet, TagViewSet, RecipesViewSet
)
from users.views import UserViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipesViewSet, basename='recipes')

urlpatterns = [
    path('', include('djoser.urls')),
    path('v1/', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
