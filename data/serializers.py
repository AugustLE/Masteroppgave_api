from rest_framework import serializers
from .models import Subject, Team, PrivacyConsent
from user.models import CustomUser


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = ('pk', 'code', 'name',)


class TeamSerializer(serializers.ModelSerializer):

    responsible = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(),
                                                     source='responsible.name',
                                                     default=None)

    class Meta:
        model = Team
        fields = ('pk', 'name', 'subject', 'last_average_score', 'responsible', 'number_of_scores', 'diverse_scores')


class PrivacyConsentSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrivacyConsent
        fields = ('pk', 'username', 'has_accepted')