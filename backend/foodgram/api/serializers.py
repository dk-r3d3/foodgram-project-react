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

    def validate_tag(self, value):
        if len(value) == 0:
            raise serializers.ValidationError('Необходимо выбрать хотя бы один тег')
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

    def create_tags(self, tag, recipes):  # добавить тег 
        recipes.tag.set(tag) 
 
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
        tag = validated_data.pop('tag') 
        ingredients = validated_data.pop('ingredients') 
        recipes = Recipes.objects.create(**validated_data) 
        self.create_tags(tag, recipes) 
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
        instance.tag.clear()
        tag = validated_data.get('tag')
        self.create_tags(tag, instance)
        RecipesIngredients.objects.filter(recipes=instance).all().delete()
        ingredients = validated_data.get('ingredients')
        self.create_ingredients(ingredients, instance)
        instance.save()
        return instance

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
