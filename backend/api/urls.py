from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
    CustomUserViewSet,
)

router = SimpleRouter()
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'users', CustomUserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
