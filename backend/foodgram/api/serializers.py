from rest_framework import serializers, validators

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
    email = serializers.EmailField(
        validators=[validators.UniqueValidator(
            queryset=User.objects.all()
        )]
    )
    username = serializers.CharField(
        validators=[validators.UniqueValidator(
            queryset=User.objects.all()
        )]
    )

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'username',
            'first_name',
            'last_name',
        )


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


class RecipesWriteSerializer(serializers.ModelSerializer):
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

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'Нужно выбрать хотя бы один ингредиент'}
            )
        for ing in ingredients:
            count = ing['count']
            if int(count) == 0:
                raise serializers.ValidationError(
                    {'Нужно выбрать количество ингредиента'}
                )
        tag = self.initial_data.get('tag')
        if not tag:
            raise serializers.ValidationError(
                {'Нужно выбрать хотя бы один тег'}
            )
        cooking_time = self.initial_data.get('cooking_time ')
        if cooking_time == 0:
            raise serializers.ValidationError(
                {'Время приготовления должно быть больше 0'}
            )
        return data

    #  функция для обновления рецепта
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
        return RecipesWriteSerializer(
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


class SubscribtionReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


# подписка на пользователя
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
