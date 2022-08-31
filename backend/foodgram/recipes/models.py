from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

CHOICES_COLOR = (
    ('#E26C2D', '#E26C2D'),
    ('#49B64E', '#49B64E'),
    ('#8775D2', '#8775D2')
)
CHOICES_NAME = (
    ('Завтрак', 'Завтрак'),
    ('Обед', 'Обед'),
    ('Ужин', 'Ужин'),
)
CHOICES_SLUG = (
    ('breakfast', 'breakfast'),
    ('lunch', 'lunch'),
    ('dinner', 'dinner'),
)

User = get_user_model()


class Ingredients(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = "Ингредиент"
        ordering = ('id',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название тега',
        choices=CHOICES_NAME
    )
    color = models.CharField(
        max_length=10,
        verbose_name='Цветовой HEX-код',
        choices=CHOICES_COLOR
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Slug',
        choices=CHOICES_SLUG
    )

    class Meta:
        verbose_name = "Tag"
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        unique=True,
        error_messages={
            'unique': 'Данный рецепт уже существует',
        },
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='images/',
        verbose_name='Картинка'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipesIngredients',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                1, message='Минимальное значение 1 минута'
                )
            ],
        verbose_name='Время приготовления',
        default=1
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = "Рецепт"
        ordering = ['-pub_date', ]

    def __str__(self):
        return self.author

    def _count_ingredients(self):
        return self.ingredients.count()


class RecipesIngredients(models.Model):
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиент'
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт'
    )
    count = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                1, message='Добавьте количество ингредиента'
                )
            ]
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='favorites',
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorites'
            )
        ]

    def __str__(self):
        return self.user


class ShoppingCart(models.Model):
    """Корзина покупок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoppingcart'
            )
        ]

    def __str__(self):
        return self.user
