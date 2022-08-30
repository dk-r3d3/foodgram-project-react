from django_filters import rest_framework
from recipes.models import Recipes, Tag


class RecipeFilters(rest_framework.FilterSet):
    tag = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipes
        fields = (
            'tag'
        )
