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


class SubcribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribtion
        fields = ('user', 'author')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubcribeListSerializer(
            instance.author, context=context).data


class SubcribeRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class SubcribeListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
            )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscribtion.objects.filter(
            user=request.user, author=obj
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        context = {'request': request}
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return SubcribeRecipesSerializer(
            recipes, many=True, context=context).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecIngReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredients.id')
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
            'amount'
        )


class RecIngSerializer(serializers.ModelSerializer):
    """Создание записи в связанной таблице"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipesIngredients
        fields = (
            'id',
            'amount'
        )


class RecipesReadSerializer(serializers.ModelSerializer):
    """Чтение рецепта"""
    ingredients = serializers.SerializerMethodField(
        read_only=True
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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


class RecipesWriteSerializer(serializers.ModelSerializer):
    """Создание рецепта"""
    ingredients = RecIngSerializer(many=True)
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
            amount = ingredient['amount']
            if int(amount) <= 0:
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
                amount=ingredient['amount'],
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
