from django.db.models import IntegerField, Value
from django_filters import rest_framework
from recipes.models import Recipes, Tag, Ingredients


class FilterIngredients(rest_framework.FilterSet):
    """Фильтр для ингредиентов"""
    name = rest_framework.CharFilter(method='search_by_name')

    class Meta:
        model = Ingredients
        fields = ('name',)

    def search_by_name(self, queryset, name, value):
        if not value:
            return queryset
        start_with_queryset = (
            queryset.filter(name__istartswith=value).annotate(
                order=Value(0, IntegerField())
            )
        )
        contain_queryset = (
            queryset.filter(name__icontains=value).exclude(
                pk__in=(ingredients.pk for ingredients in start_with_queryset)
            ).annotate(
                order=Value(1, IntegerField())
            )
        )
        return start_with_queryset.union(contain_queryset).order_by('order')


class Fav_Cart_Filter(rest_framework.FilterSet):
    """Набор фильтров для получения списка рецептов в избранном и корзине"""
    author = rest_framework.filters.NumberFilter(
        field_name='author__id',
        lookup_expr='exact'
    )
    tag = rest_framework.ModelMultipleChoiceFilter(
        field_name='tag__slug',
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
            'tag',
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
