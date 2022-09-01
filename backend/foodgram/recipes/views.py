from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import (
    IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly,
    SAFE_METHODS
)
from rest_framework.decorators import action

from .models import (
    Ingredients, RecipesIngredients, ShoppingCart, Tag,
    Recipes, Favorites
)
from api.serializers import (
    IngredientsSerializer, TagSerializer, RecipesWriteSerializer,
    RecipesReadSerializer
)
from api.services.add_to import post_or_del_method
from api.paginations import LimitPageNumberPagination
from api.filters import Fav_Cart_Filter, FilterIngredients


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterIngredients
    search_fields = ('name',)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filterset_class = Fav_Cart_Filter
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('is_favorited', 'author', 'shopping_cart', 'tags')

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesReadSerializer
        return RecipesWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=('POST', 'DELETE'),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path=r'(?P<pk>\d+)/favorite'
    )
    def favorites(self, request, pk=None):  # добавление/удаление из избранного
        method = request.method
        user = request.user
        return post_or_del_method(method, user, pk, Favorites)

    @action(
        methods=('POST', 'DELETE'),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path=r'(?P<pk>\d+)/shopping_cart'
    )
    #  добавление/удаление из списка покупок
    def shopping_cart(self, request, pk=None):
        method = request.method
        user = request.user
        return post_or_del_method(method, user, pk, ShoppingCart)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    # скачать рецепт с описанием и ингредиентами
    def download_shopping_cart(self, request):
        user = request.user
        ingredient_list_user = (
            RecipesIngredients.objects.
            prefetch_related('ingredients', 'recipes').
            filter(recipes__shopping_cart__user=user).
            values('ingredients__id').
            order_by('ingredients__id')
        )
        shopping_list = (
            ingredient_list_user.annotate(count=Sum('count')).
            values_list(
                'ingredients__name', 'ingredients__measurement_unit', 'count',
            )
        )
        shopping_cart = '\n'.join([
            f'{ingredient[0]} - {ingredient[2]} {ingredient[1]}'
            for ingredient in shopping_list
        ])
        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
