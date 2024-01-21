"""
serializers for recipe APIs
"""

from rest_framework import serializers
from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']

    # helper function that gets or creates tags
    def _get_or_create_tags(self, tags, recipe):
        # context is passed to the serializer by the view which calls the serializer
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user =auth_user,
                **tag   # we could use name = tag['name']
                        # but this way we could add all fields of a tag
                        # if any is added in the future
                        # ... I don't know if it's worth since the model must be modified ...?
            )
            recipe.tags.add(tag_obj)

    # we need to overwrite a standard create because the standard one
    # does not support nested srializers - they work as read only by default
    def create(self, validated_data):
        """Create a recipe with nested tags list"""
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        return recipe

    # we need to overwrite the update like we did for the create method
    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


