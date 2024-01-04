"""
Views for recipe APIs
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe
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