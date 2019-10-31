from rest_framework import serializers
from .models import Subject
from .models import EnrolledInSubject


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


