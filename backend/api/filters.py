from django_filters import rest_framework
from recipes.models import Recipes, Tag, Ingredients


class Fav_Cart_Filter(rest_framework.FilterSet):
    """Набор фильтров для получения списка рецептов в избранном и в корзине"""
    author = rest_framework.filters.NumberFilter(
        field_name='author__id',
        lookup_expr='exact'
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = rest_framework.filters.BooleanFilter(
        method='favorited'
    )
    is_in_shopping_cart = rest_framework.filters.BooleanFilter(
        method='shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class FilterIngredients(rest_framework.FilterSet):
    """Фильтр для ингредиентов"""
    name = rest_framework.filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredients
        fields = ('name',)
