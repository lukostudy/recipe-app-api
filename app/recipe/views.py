"""
Views for recipe APIs
"""

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe, Tag, Ingredient
from recipe import serializers


# we use ViewSet not a View, brcause VieSets have a lot of CRUD
# operations done
class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for manage recipe APIs"""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]  # type of auth we use
    permission_classes = [IsAuthenticated]  # authentication required

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
        # self.request has authenticated user id inside

    def get_serializer_class(self):
        """Return serializer class for a request"""
        if self.action == 'list':
            return serializers.RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)


class TagViewSet(mixins.DestroyModelMixin, # delete functionality needed only this import
                mixins.UpdateModelMixin, #update functionality needed only this import
                mixins.ListModelMixin,
                viewsets.GenericViewSet): # this import should be hte last one!!!
    """Managr tags in the database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter query set to authenticated users"""
        return self.queryset.filter(user=self.request.user).order_by('-name')


# mixins.UpdateModelMixin mixins.Update adds automatically router url recipe:ingredient-detail
class IngredientViewSet(mixins.DestroyModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to an authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')