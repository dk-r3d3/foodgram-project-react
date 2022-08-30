from rest_framework import serializers

from .fields import Base64ImageField
from recipes.models import (
     Recipes,
     ShoppingCart,
     Favorites
)
from users.models import User, Subscribtion


# подписка на пользователя
class SubscribtionReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscribtionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count",
        read_only=True
    )

    class Meta:
        model = Subscribtion
        fields = (
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj: User):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscribtion.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj: User):
        recipes = obj.recipes.all()
        return SubscribtionReadSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipes.objects.filter(author=obj.author).count()


class FavoriteSerializer(serializers.ModelSerializer):  # избранное
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipes.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Favorites
        fields = (
            'user',
            'recipe'
        )


class ShoppingCartSerializer(serializers.ModelSerializer):  # корзина покупок
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipes.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe'
        )
