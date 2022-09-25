from django.contrib import admin

from .models import (
    Recipes, Ingredients, Tag, Favorites,
    RecipesIngredients
)


class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'quantity_favorites'
    )
    list_filter = ('author', 'name', 'tags',)

    def quantity_favorites(self, obj):
        return obj.favorites.count()


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
        'id',
        'user',
        'recipe'
    )
    list_filter = ('user', 'recipe')


class RecipesIngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'ingredients',
        'recipes',
        'amount'
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
