from rest_framework import serializers
from data.models import Score


class ScoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Score
        fields = ('pk', 'score', 'date_registered')