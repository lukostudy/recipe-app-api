"""
Test fir the tags API
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag details url"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user - helper function"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API  requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):

    def setUp(self):
        self.user1 = create_user()
        self.user2 = create_user(email='user2@example.com')
        self.client = APIClient()
        self.client.force_authenticate(self.user1)


    def test_retrieve_tags(self):
        """Test authenticated API requests"""
        Tag.objects.create(user=self.user1, name='Vegan')
        Tag.objects.create(user=self.user1, name='Dessert')
        Tag.objects.create(user=self.user1, name='Soup')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_tags_limited_to_user(self):
        """Test liat of tags is limitted to authenticated user"""
        Tag.objects.create(user=self.user2, name='Fruity')
        tag = Tag.objects.create(user=self.user1, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user1, name='Afer Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag_id=tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting the tag"""

        tag = Tag.objects.create(user=self.user1, name='Breakfast')
        url = detail_url(tag_id=tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user1)
        self.assertFalse(tags.exists())


    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags by those assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user1, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user1, name='Dinner')
        recipe = Recipe.objects.create(
            title='Soup',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user1,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only':1})

        tag1s = TagSerializer(tag1)
        tag2s = TagSerializer(tag2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag1s.data, res.data)
        self.assertNotIn(tag2s.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list."""
        tag1 = Tag.objects.create(user=self.user1, name='Breakfast')
        Tag.objects.create(user=self.user1, name='Dinner')
        recipe1 = Recipe.objects.create(
            title='Soup',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user1,
        )
        recipe2 = Recipe.objects.create(
            title='Boiled eggs',
            time_minutes=7,
            price=Decimal('6.50'),
            user=self.user1,
        )

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag1)
        tag1s = TagSerializer(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertIn(tag1s.data, res.data)




