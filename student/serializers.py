from rest_framework import serializers
from data.models import Team


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ('pk', 'name', 'subject', 'last_average_score')