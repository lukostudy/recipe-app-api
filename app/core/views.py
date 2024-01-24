"""
Core views for app.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response

# that's a method for a short simple implementation
@api_view(['GET'])
def health_check(request):
    """Return just a simple response: I'm OK"""
    return Response({'healthy': True})