from rest_framework import routers
from django.urls import include, path

from recipes.views import (
    IngredientsViewSet, TagViewSet, RecipesViewSet
)
from users.views import UserViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register(r'users', UserViewSet, basename='users')  # +
router.register(r'ingredients', IngredientsViewSet)
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipesViewSet)

urlpatterns = [
    path('v1/', include(router.urls))
]
