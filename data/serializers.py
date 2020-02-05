from rest_framework import serializers
from .models import Subject, EnrolledInSubject, Team, PrivacyConsent
from user.models import CustomUser


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = ('pk', 'code', 'name',)


class EnrollmentSerializer(serializers.ModelSerializer):

    subject_code = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), source='subject.code')
    subject_name = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), source='subject.name')
    subject_pk = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), source='subject.pk')

    class Meta:
        model = EnrolledInSubject
        fields = ('user', 'subject_code', 'subject_name', 'subject_pk', 'active')


class TeamSerializer(serializers.ModelSerializer):

    responsible = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(),
                                                     source='responsible.name',
                                                     default=None)

    class Meta:
        model = Team
        fields = ('pk', 'name', 'subject', 'last_average_score', 'responsible')


class PrivacyConsentSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrivacyConsent
        fields = ('pk', 'username', 'has_accepted')