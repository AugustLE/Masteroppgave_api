from rest_framework import serializers
from user.models import CustomUser
from project_api import settings


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('pk', 'username', 'auth_token', 'date_joined')

