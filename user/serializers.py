from rest_framework import serializers
from user.models import CustomUser
from project_api import settings


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('pk', 'username', 'date_joined', 'role',)

