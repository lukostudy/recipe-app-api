"""
Tests for ingredients API.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Create and return an ingredient detail url"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='user@example.com', password='pass123'):
    """Create and return a user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    """Test auauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_is_required(self):
       """Test auth is required to retrieve a list of ingredients"""
       res = self.client.get(INGREDIENTS_URL)
       self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.user2 = create_user(email='user2@example.com')
        self.client.force_authenticate(self.user)
        #self.client.force_authenticate(self.user2)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Vanilla')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test retrieving a list of ingredientd only belonging to am authenticated user"""
        Ingredient.objects.create(user=self.user2, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')

        payload = {'name': 'Coriander'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name='Lettuce')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients by those assigned to recipes."""
        in1 = Ingredient.objects.create(user=self.user, name='Pepper')
        in2 = Ingredient.objects.create(user=self.user, name='Salt')
        recipe = Recipe.objects.create(
            title='Soup',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only':1})

        in1s = IngredientSerializer(in1)
        in2s = IngredientSerializer(in2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(in1s.data, res.data)
        self.assertNotIn(in2s.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list."""
        in1 = Ingredient.objects.create(user=self.user, name='Pepper')
        Ingredient.objects.create(user=self.user, name='Salt')
        recipe1 = Recipe.objects.create(
            title='Soup',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Boiled eggs',
            time_minutes=7,
            price=Decimal('6.50'),
            user=self.user,
        )
        recipe1.ingredients.add(in1)
        recipe2.ingredients.add(in1)
        in1s = IngredientSerializer(in1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertIn(in1s.data, res.data)




