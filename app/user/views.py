"""
Views for the user API
"""

from rest_framework import generics, authentication, permissions
from user.serializers import UserSerializer, AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings



# we use standard view from rest_framework.generics
# the CreateAPIView creates an object in the database model
# the view uses UserSerializer that we defined
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for a user"""
    # we user our serializer instead of the default one
    # we needed a customized serializer here because we changed
    # default authorizatio - we do not use username, we use email
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

# this is a generic view to gen and update model objects
# with methods GET, PUT
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the logged in user"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # we ovewrite this method which normally returns a generic
    # model object
    def get_object(self):
        """Retrieve and return an authenticated user"""
        # here we just return a user from the request
        return self.request.user


