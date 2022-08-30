from api.fields import Base64ImageField

from rest_framework import serializers
from recipes.models import (
    Ingredients, Tag, Recipes,
    RecipesIngredients
)
from users.serializers import CustomUserSerializer


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecIngSerializer(serializers.ModelSerializer):
    """Создание записи в связанной таблице"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all()
    )
    count = serializers.IntegerField()

    class Meta:
        model = RecipesIngredients
        fields = (
            'id',
            'count'
        )


class RecipesSerializer(serializers.ModelSerializer):
    """Создание рецепта"""
    ingredients = RecIngSerializer(
        many=True
    )
    tag = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tag',
            'cooking_time'
        )

    def create_tags(self, tag, recipes):  # добавить тег
        recipes.tag.set(tag)

    def create_ingredients(self, ingredients, recipe):  # добавить ингредиенты
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            count = ingredient['count']
            RecipesIngredients.objects.create(
                recipes=recipe, ingredients=ingredient_id, count=count
            )

    def create(self, validated_data):  # функция для создания рецепта
        tag = validated_data.pop('tag')
        ingredients = validated_data.pop('ingredients')
        recipes = Recipes.objects.create(**validated_data)
        self.create_tags(tag, recipes)
        self.create_ingredients(ingredients, recipes)
        return recipes

    # функция для обновления рецепта
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tag_data = validated_data.pop('tag')
        instance.ingredients.clear()
        self.create_data(instance, ingredients_data)
        instance.tag.set(tag_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipesSerializer(
            instance, context=context).data


class RecIngReadSerializer(serializers.ModelSerializer):  # ++++
    """Чтение записи в связанной таблице"""
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = RecipesIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'count',
        )


class RecipesReadSerializer(serializers.ModelSerializer):
    """Чтение рецепта"""
    ingredients = serializers.SerializerMethodField(
        read_only=True
    )
    tag = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipes
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tag',
            'cooking_time',
            'is_favorited',
            'shopping_cart'
        )

    def get_ingredients(self, obj):
        ingredients = RecipesIngredients.objects.filter(recipes=obj)
        return RecIngReadSerializer(ingredients, many=True).data

    def get_user(self):
        return self.context['request'].user

    def get_is_favorited(self, obj):  # избранное
        user = self.get_user()
        return (
            user.is_authenticated
            and user.favorites.filter(recipe=obj).exists()
        )

    def get_shopping_cart(self, obj):  # корзина покупок
        user = self.get_user()
        return (
            user.is_authenticated
            and user.shopping_cart.filter(recipe=obj).exists()
        )
