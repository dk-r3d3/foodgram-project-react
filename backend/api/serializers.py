from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserSerializer, UserCreateSerializer

from recipes.models import (
    Tag, Ingredients, Recipes, ShoppingCart, Favorites,
    RecipesIngredients
)
from users.models import User, Subscribtion


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
        )
        read_only_fields = ('is_subscribed', )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscribtion.objects.filter(
            user=request.user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'username',
            'first_name',
            'last_name',
        )


class SubscribtionReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


# подписка на пользователя
class SubscribtionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count",
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name',
            'recipes', 'is_subscribed', 'recipes_count',
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


class RecIngReadSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        source='ingredients.id'
    )
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


class RecipesShowSerializer(serializers.ModelSerializer):
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
            'tags',
            'cooking_time'
        )


class RecipesWriteSerializer(serializers.ModelSerializer):
    """Создание рецепта"""
    ingredients = RecIngSerializer(
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
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
            'tags',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = RecipesIngredients.objects.filter(recipes=obj)
        return RecIngReadSerializer(ingredients, many=True).data

    def validate_tags(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'Необходимо выбрать хотя бы один тег'
            )
        return value

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'Необходимо выбрать хотя бы один ингредиент'
            )
        for ingredient in value:
            if ingredient['count'] == 0:
                raise serializers.ValidationError(
                    'Необходимо выбрать количество ингредиента'
                )
        return value

    def validate_cookingtime(self, value):
        for i in value:
            if not i['cooking_time']:
                raise serializers.ValidationError(
                    'Необходимо указать время приготовления рецепта'
                )
            elif i['cooking_time'] <= 1:
                raise serializers.ValidationError(
                    'Время приготовления должно быть боольше 1 мин.'
                )

    def create_tags(self, tags, recipes):  # добавить тег
        recipes.tags.set(tags)

    def create_ingredients(self, ingredients, recipes):  # добавить ингредиенты
        ing = [
            RecipesIngredients(
                ingredients=ingredient['id'],
                count=ingredient['count'],
                recipes=recipes
            )
            for ingredient in ingredients
        ]
        RecipesIngredients.objects.bulk_create(ing)

    def create(self, validated_data):  # функция для создания рецепта
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipes = Recipes.objects.create(**validated_data)
        self.create_tags(tags, recipes)
        self.create_ingredients(ingredients, recipes)
        return recipes

    #  функция для обновления рецепта
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags = validated_data.get('tags')
        self.create_tags(tags, instance)
        RecipesIngredients.objects.filter(recipes=instance).all().delete()
        ingredients = validated_data.get('ingredients')
        self.create_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipesReadSerializer(
            instance, context=context).data


class RecipesReadSerializer(serializers.ModelSerializer):
    """Чтение рецепта"""

    ingredients = serializers.SerializerMethodField(
        read_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    # print(author)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipes
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_user(self):
        return self.context['request'].user

    def get_ingredients(self, obj):
        ingredients = RecipesIngredients.objects.filter(recipes=obj)
        return RecIngReadSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorites.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()


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
