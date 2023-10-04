from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from food.views import (
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
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]
