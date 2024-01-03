"""
Serializers for user API View.
"""

from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _
# it's a convention to import django translation as _

# serializers converts text structures like json into python data structures
# they also make all required validation to keep the model correct and secure
# serializers are defined by django - we can inherit them and adjust to our needs
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    # in Meta class we define data details that are to be serialized
    class Meta:
        model = get_user_model()
        fields = ['email','password','name']
        extra_kwargs = {'password' : {'write_only': True, 'min_length': 5}}

    # this method will be called by the serializer if all the validation was ok
    # in case of issues discovered, this method will not be called
    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.setr_password(password)
            user.save()


# this is a simpler Serializer, not Model.Serializer
class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type':'password'},
                                    trim_whitespace=False)

    # this function will be called if the previous code is ok -> no errors
    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _("Unable to authenticate. Check email and password.")
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


