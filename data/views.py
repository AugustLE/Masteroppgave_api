from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from .serializers import EnrollmentSerializer, SubjectSerializer
from .serializers import TeamSerializer
from .models import Subject, EnrolledInSubject, PreEnrollmentEntry, UserIsOnTeam, Team, Score, IsResponsibleForTeam
from user.models import CustomUser
from user.serializers import UserSerializer
import random
import datetime


class EnrollmentList(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    # This method enroll the student in the registered courses, and sends back the enrolled courses
    @csrf_exempt
    def post(self, request):

        user = request.user
        entries = PreEnrollmentEntry.objects.filter(student_name__contains=user.name)

        for entry in entries:
            if EnrolledInSubject.objects.filter(subject=entry.subject, user=user).count() == 0:
                enroll_student = EnrolledInSubject(user=user, subject=entry.subject)
                enroll_student.save()
                entry.enrolled = True
                entry.save()
        enrollment_list = EnrolledInSubject.objects.filter(user=user)
        serializer = EnrollmentSerializer(enrollment_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @csrf_exempt
    def get(self, request):

        user = request.user
        enrollment_list = EnrolledInSubject.objects.filter(user=user)
        serializer = EnrollmentSerializer(enrollment_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SelectSubject(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def post(self, request):

        user = request.user
        subject_id = request.data.get('subject_id')
        subject = Subject.objects.get(pk=subject_id)

        if user.role == 'SD':
            enrolled = EnrolledInSubject.objects.filter(user=user, active=True)
            if enrolled.count() > 0:
                for entry in enrolled:
                    entry.active = False
                    entry.save()

            active_enrollment = EnrolledInSubject.objects.get(subject=subject, user=user)
            active_enrollment.active = True
            active_enrollment.save()

        user.selected_subject_id = subject_id
        user.save()
        serializer = UserSerializer(user, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ApiUser(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user, many=False)

        subject = None
        subject_data = None
        if Subject.objects.filter(pk=user.selected_subject_id).count() > 0:
            subject = Subject.objects.get(pk=user.selected_subject_id)
            subject_data = SubjectSerializer(subject, many=False).data

        return_object = {
            'api_user': serializer.data,
            'subject': subject_data
        }

        if user.role == 'SD':
            team = None
            team_data = None
            if subject:
                team = UserIsOnTeam.objects.get(user=user, team__subject=subject).team

            if team:
                team_data = TeamSerializer(team, many=False).data

            return_object = {
                'api_user': serializer.data,
                'team': team_data,
                'subject': subject_data
            }

        return Response(return_object, status=status.HTTP_200_OK)


### THIS IS A TEST FUNCTION TO GENERATE TEST DATA
class TestData(APIView):

    permission_classes = (permissions.AllowAny, )

    @csrf_exempt
    def get(self, request):

        user_counter = 3
        for i in range(50):
            subject = Subject.objects.get(pk=1)
            name = 'Team ' + str(i + 2)
            new_team = Team(name=name, password='123', subject=subject)
            new_team.save()

            tas = CustomUser.objects.filter(role='TA')
            ta = tas[i % tas.count()]
            is_res = IsResponsibleForTeam(user=ta, team=new_team)
            is_res.save()
            new_team.responsible = ta
            new_team.save()


            team_sum = 0
            team_score_counter = 0

            for h in range(4):
                user_name = 'Testuser ' + str(user_counter)
                user_id = 'test-' + str(user_counter)

                test_user = CustomUser(
                    username=user_name,
                    user_id=user_id,
                    name=user_name,
                    role='SD',
                    selected_subject_id=1
                )
                test_user.save()

                is_on_team = UserIsOnTeam(user=test_user, team=new_team)
                is_on_team.save()

                for k in range(10):
                    score_value = random.randint(1, 5)
                    date = datetime.datetime.now()
                    test_score = Score(score=score_value, user=test_user, team=new_team, date_registered=date)
                    test_score.save()

                    team_score_counter += 1
                    team_sum += score_value

                user_counter += 1

            team_average = team_sum / team_score_counter
            new_team.last_average_score = team_average
            new_team.save()

        return Response('data generated', status=status.HTTP_200_OK)