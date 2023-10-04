from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import (
    Cart,
    Favorite,
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
    Subscription,
    User,
)


# class SignUpSerializer(serializers.Serializer):
#     username = serializers.CharField(
#         required=True,
#         max_length=150,
#         validators=(UnicodeUsernameValidator(), MinLengthValidator(3)),
#     )
#     email = serializers.EmailField(required=True, max_length=254)
#     first_name = serializers.CharField(required=True, max_length=254)
#     last_name = serializers.CharField(required=True, max_length=254)
#     password = serializers.CharField(required=True)


#     def validate(self, data):
#         try:
#             User.objects.get_or_create(
#                 username=data.get('username'), email=data.get('email')
#             )
#         except IntegrityError:
#             raise serializers.ValidationError(
#                 'Пользователь с таким username или email уже существует.'
#             )
#         return data
class SignUpSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
        )


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class UserSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj)
        # if recipes_limit:
        #     recipes = recipes[: int(recipes_limit)]
        # return recipes
        # recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        return RecipeSmallSerializer(recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
        # return obj.recipes.all().count()


class SubscriptionSerializer(serializers.Serializer):
    author = serializers.IntegerField()
    user = serializers.IntegerField()

    class Meta:
        model = Subscription
        fields = '__all__'
        validators = (
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author', 'user'),
                message='Подписка на самого себя не возможна',
            ),
        )

    def validate(self, data):
        author = User.objects.get(id=data.get('author'))
        user = User.objects.get(id=data.get('user'))
        if user == author:
            raise serializers.ValidationError(
                'Подписка на самого себя не возможна'
            )
        return data

    def create(self, validated_data):
        author = User.objects.get(id=validated_data.get('author'))
        user = User.objects.get(id=validated_data.get('user'))
        return Subscription.objects.create(user=user, author=author)

    def to_representation(self, instance):
        request = self.context.get('request')
        return UserSubscriptionSerializer(
            instance.author, context={'request': request}
        ).data


# class TokenSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True)
#     confirmation_code = serializers.CharField(required=True)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class IngredientGetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientGetSerializer(
        many=True, read_only=True, source='recipeingredient'
    )
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Cart.objects.filter(user=request.user, recipe=obj).exists()


class PostRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientPostSerializer(
        # required=True,
        many=True,
        source='recipeingredient',
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        required=True,
        many=True,
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        if not data.get('image'):
            raise serializers.ValidationError('Изображение обязательно')
        tags_list = []
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Должен присутствовать хотя бы 1 тег'
            )
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError('Этот тег уже добавлен')
            tags_list.append(tag)
        ingredients_list = []
        ingredients = data.get('recipeingredient')
        if not ingredients:
            raise serializers.ValidationError(
                'Должен присутствовать хотя бы 1 ингредиент'
            )
        for ingredient in ingredients:
            if ingredient.get('amount') < 1:
                raise serializers.ValidationError(
                    'Количестово ингредиента не может быть меньше чем 1'
                )
            if ingredient.get('id') in ingredients_list:
                raise serializers.ValidationError(
                    'Этот ингридиент уже добавлен'
                )
            ingredients_list.append(ingredient.get('id'))
            if not Ingredient.objects.filter(id=ingredient.get('id')).exists():
                raise serializers.ValidationError(
                    'Этого ингридиента нет в базе'
                )
        return data

    def recipe_ingredient_create(self, recipe, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            get_ingridient = get_object_or_404(
                Ingredient, id=ingredient.get('id')
            )
            amount = ingredient.get('amount')
            ingredients_list.append(
                RecipeIngredient(
                    recipe=recipe, ingredient=get_ingridient, amount=amount
                )
            )
        RecipeIngredient.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('recipeingredient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.recipe_ingredient_create(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipeingredient')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        self.recipe_ingredient_create(instance, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Уже в избранном',
            )
        ]

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError({'errors': 'Уже в избранном'})
        return data

    def to_representation(self, instance):
        return RecipeSmallSerializer(
            instance, context={'request': self.context.get('request')}
        ).data


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('user', 'recipe'),
            )
        ]

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if Cart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError({'errors': 'Уже в корзине'})
        return data

    def to_representation(self, instance):
        return RecipeSmallSerializer(
            instance, context={'request': self.context.get('request')}
        ).data
