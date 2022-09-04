from django.contrib import admin

from .models import (
    Recipes, Ingredients, Tag, Favorites,
    RecipesIngredients
)


class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author'
    )
    list_filter = ('author', 'name', 'tags',)


class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug'
    )


class FavouritesAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )


class RecipesIngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'ingredients',
        'recipes',
        'count'
    )


ADMINS_LIST = (
    (Recipes, RecipesAdmin),
    (Ingredients, IngredientsAdmin),
    (Tag, TagAdmin),
    (Favorites, FavouritesAdmin),
    (RecipesIngredients, RecipesIngredientsAdmin)
)

for model, admins in ADMINS_LIST:
    admin.site.register(model, admins)
