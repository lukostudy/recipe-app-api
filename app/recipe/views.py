"""
Views for recipe APIs
"""

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe, Tag, Ingredient
from recipe import serializers
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

# we use ViewSet not a View, brcause VieSets have a lot of CRUD
# operations done
# the extend_schema_view is for the documentation used by drf_scpectacular
@extend_schema_view(
    list=extend_schema(  # we want extend schema for the list endpoint
        parameters=[  # parameters that can be passed to the get request
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tags IDs [int] \
                      to filter the get query.'
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredients IDs [int] \
                    to filter the get query.'
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for manage recipe APIs"""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]  # type of auth we use
    permission_classes = [IsAuthenticated]  # authentication required

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers like 1,4,5,2 """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        # return self.queryset.filter(user=self.request.user).order_by('-id')
        # self.request has authenticated user id inside
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user).order_by('-id').distinct()
        # order_by('id') standard asc order
        # order_by('-id') reverse order


    def get_serializer_class(self):
        """Return serializer class for a request"""
        if self.action == 'list':  # a default action - see the doc
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':  # a custom action - see below
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload_image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewSet(
    mixins.DestroyModelMixin, # delete functionality needed only this import
    mixins.UpdateModelMixin, #update functionality needed only this import
    mixins.ListModelMixin,
    viewsets.GenericViewSet # this import should be hte last one!!
    ):
    """Base class for a recipe attributes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter query set to authenticated users"""
        return self.queryset.filter(user=self.request.user).order_by('-name')



class TagViewSet(BaseRecipeAttrViewSet): # this import should be hte last one!!!
    """Managr tags in the database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


# mixins.UpdateModelMixin mixins.Update adds automatically router url recipe:ingredient-detail
class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
