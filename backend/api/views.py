from django.shortcuts import get_object_or_404, HttpResponse
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from food.models import (
    Cart,
    Favorite,
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
)
from users.models import Subscription, User
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    CartSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    TagSerializer,
    PostRecipeSerializer,
    RecipeSerializer,
    RecipeSmallSerializer,
    UserSubscriptionSerializer,
    SubscriptionSerializer,
)


class CustomUserViewSet(UserViewSet):
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        url_path='subscribe',
        url_name='subscribe',
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        serializer = SubscriptionSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request},
        )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = UserSubscriptionSerializer(
                author,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        sub = Subscription.objects.filter(user=request.user, author=author)
        if not sub.exists():
            return Response(
                {'errors': 'Подписка не существует'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        sub.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=[
            'get',
        ],
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
        url_name='subscriptions',
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        paginate = self.paginate_queryset(queryset)
        serializer = UserSubscriptionSerializer(
            paginate, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return PostRecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, **kwargs):
        if request.method == 'POST':
            if not Recipe.objects.filter(id=kwargs['pk']).exists():
                return Response(
                    {'error_message': 'Нет такого рецепта'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id},
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = RecipeSmallSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
            if not Favorite.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'error_message': 'Нет в избранном'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Favorite.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(
                {'detail': 'Удаленно успешно'},
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, **kwargs):
        if request.method == 'POST':
            if not Recipe.objects.filter(id=kwargs['pk']).exists():
                return Response(
                    {'error_message': 'Нет такого рецепта'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
            serializer = CartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id},
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = RecipeSmallSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
            if not Cart.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'error_message': 'Нет в избранном'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Cart.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(
                {'detail': 'Удаленно успешно'},
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(recipe__cart__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .order_by('ingredient__name')
            .annotate(ingredient_total=Sum('amount'))
        )
        shopping_list = ['К покупке:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_total']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_cart.txt"'
        return response
