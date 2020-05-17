from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)

# https://www.django-rest-framework.org/api-guide/routers/
# URL pattern: ^ingredients/$ Name: 'ingredient-list'
# URL pattern: ^ingredients/{pk}/$ Name: 'ingredient-detail'
# URL pattern: ^recipes/$ Name: 'recipe-list'
# URL pattern: ^recipes/{pk}/$ Name: 'recipe-detail'

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
