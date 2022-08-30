from django.http import HttpResponse
from rest_framework import viewsets, filters
from rest_framework.permissions import (
    IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
)
from rest_framework.decorators import action

# Импорты внутри проекта
from .models import (
    Ingredients, RecipesIngredients, ShoppingCart, Tag,
    Recipes, Favorites
)
from .serializers import (
    IngredientsSerializer, TagSerializer, RecipesSerializer,
    RecipesReadSerializer
)
from .services.add_to import post_or_del_method
from api.paginations import LimitPageNumberPagination


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    actions = ['create', 'update']
    search_fields = ('is_favorited', 'author', 'shopping_cart', 'tags')

    def get_serializer_class(self):
        if self.action in self.actions:
            return RecipesSerializer
        return RecipesReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=('POST', 'DELETE'),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path=r'(?P<pk>\d+)/favorite'
    )
    def favorite(self, request, pk=None):  # добавление/удаление из избранного
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
        ingredients = RecipesIngredients.objects.filter(
            recipes__shopping_cart__user=request.user).values(
            'ingredients__name', 'ingredients__measurement_unit', 'count',
            'recipes__name', 'recipes__text'
        )
        shopping_cart = '\n'.join([
            f'Рецепт - "{ingredient["recipes__name"]}" \n'
            f'Cпособ приготовления - {ingredient["recipes__text"]} \n'
            f'Ингредиенты: \n'
            f'{ingredient["ingredients__name"]} - {ingredient["count"]} '
            f'{ingredient["ingredients__measurement_unit"]}'
            for ingredient in ingredients
        ])
        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
