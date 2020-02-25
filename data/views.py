from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from .serializers import SubjectSerializer
from .serializers import TeamSerializer, PrivacyConsentSerializer
from .models import Subject, UserIsOnTeam, Team, Score, \
    IsResponsibleForTeam, PrivacyConsent, AuthorizedInstructor, PreTeamRegister
from user.models import CustomUser
from user.serializers import UserSerializer
import random
import datetime
from project_api.settings import SECRET_KEY


class SelectSubject(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def post(self, request):

        user = request.user
        subject_id = request.data.get('subject_id')
        subject = Subject.objects.get(pk=subject_id)

        if AuthorizedInstructor.objects.filter(subject=subject, feide_username=user.username).count() > 1:
            user.role = 'IN'
            user.save()

        permission = False
        if PreTeamRegister.objects.filter(feide_username=user.username, subject=subject).count() > 0:
            permission = True
            pre_register = PreTeamRegister.objects.get(feide_username=user.username, subject=subject)
            user.role = pre_register.role
            if pre_register.role == 'SD':
                new_on_team = UserIsOnTeam(team=pre_register.team, user=user)
                new_on_team.save()
            elif pre_register.role == 'IN' or pre_register.role == 'TA':
                if IsResponsibleForTeam.objects.filter(user=user, team=pre_register.team).count() == 0:
                    new_responsible = IsResponsibleForTeam(user=user, team=pre_register.team)
                    new_responsible.save()

                pre_register.team.responsible = user
                pre_register.team.save()

            user.selected_subject_id = subject_id

        user.save()

        user_data = UserSerializer(user, many=False).data
        if not permission:
            user_data['error'] = 'You dont have permission to this course'
        return Response(user_data, status=status.HTTP_200_OK)


class SelectSubjectWithTeams(APIView):

    @csrf_exempt
    def post(self, request):

        user = request.user
        subject_id = request.data.get('subject_id')
        subject = Subject.objects.get(pk=subject_id)

        if AuthorizedInstructor.objects.filter(subject=subject, feide_username=user.username).count() > 1:
            user.role = 'IN'
            user.save()

        user.selected_subject_id = subject_id
        user.role = 'SD'
        user.save()

        teams = Team.objects.filter(subject=subject)
        team_data = TeamSerializer(teams, many=True).data

        user_data = UserSerializer(user, many=False).data
        return_object = {'user': user_data, 'teams': team_data}

        return Response(return_object, status=status.HTTP_200_OK)


class TeamList(APIView):

    @csrf_exempt
    def get(self, request):
        user = request.user
        subject_id = user.selected_subject_id
        subject = Subject.objects.get(pk=subject_id)

        teams = Team.objects.filter(subject=subject)
        team_data = TeamSerializer(teams, many=True).data

        return Response(team_data, status=status.HTTP_200_OK)


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
            if subject and UserIsOnTeam.objects.filter(user=user, team__subject=subject).count() > 0:
                team = UserIsOnTeam.objects.get(user=user, team__subject=subject).team

            if team:
                team_data = TeamSerializer(team, many=False).data

            return_object = {
                'api_user': serializer.data,
                'team': team_data,
                'subject': subject_data
            }
        print(return_object)
        return Response(return_object, status=status.HTTP_200_OK)


class GetPrivacyConsent(APIView):

    permission_classes = (permissions.AllowAny, )

    @csrf_exempt
    def get(self, request, username):

        #if secret_key != SECRET_KEY:
         #   return Response({'error': 'No authorization'}, status=status.HTTP_200_OK)

        if PrivacyConsent.objects.filter(username=username).count() > 0:

            consent = PrivacyConsent.objects.get(username=username)
            data = PrivacyConsentSerializer(consent, many=False).data
            return Response(data, status=status.HTTP_200_OK)

        return Response({'username': username, 'has_accepted': False}, status=status.HTTP_200_OK)

    @csrf_exempt
    def post(self, request):

        has_accepted = request.data.get('has_accepted')
        feide_username = request.data.get('feide_username')
        date = datetime.datetime.now()
        if PrivacyConsent.objects.filter(username=feide_username).count() == 0:
            privacy_object = PrivacyConsent(username=feide_username, has_accepted=has_accepted, date_accepted=date)
        else:
            privacy_object = PrivacyConsent.objects.get(username=feide_username)
            privacy_object.has_accepted = has_accepted
        privacy_object.save()
        data = PrivacyConsentSerializer(privacy_object, many=False).data

        return Response(data, status=status.HTTP_200_OK)


class SubjectList(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def get(self, request):
        subjects = Subject.objects.all()
        response_data = SubjectSerializer(subjects, many=True).data
        return Response(response_data, status=status.HTTP_200_OK)


### TEST FUNCTION TO GENERATE TEST DATA
class TestData(APIView):

    permission_classes = (permissions.AllowAny, )

    @csrf_exempt
    def get(self, request):

        """for team in Team.objects.all():
            name = team.name

            number_str = name.split(' ')[1]
            try:
                number = int(number_str)
            except ValueError:
                number = 0

            team.team_number = number
            team.save()"""


        user_counter = 3
        for i in range(50):
            subject = Subject.objects.get(pk=1)
            number = i + 1
            name = 'Team ' + str(number)
            new_team = Team(name=name, subject=subject, team_number=number)
            new_team.save()

            tas = CustomUser.objects.filter(role='TA')
            ta = tas[i % tas.count()]
            is_res = IsResponsibleForTeam(user=ta, team=new_team)
            is_res.save()
            new_team.responsible = ta
            new_team.save()
            pre_reg_ta = PreTeamRegister(feide_username=ta.username, role='TA', team=new_team, subject=subject)
            pre_reg_ta.save()

            team_sum = 0
            team_score_counter = 0

            for h in range(4):
                username = 'testuser' + str(user_counter)
                user_id = 'test-' + str(user_counter)

                test_user = CustomUser(
                    username=username,
                    user_id=user_id,
                    name=username,
                    role='SD',
                    selected_subject_id=1
                )
                test_user.save()

                is_on_team = UserIsOnTeam(user=test_user, team=new_team)
                is_on_team.save()
                pre_reg = PreTeamRegister(feide_username=username, role='SD', team=new_team, subject=subject)
                pre_reg.save()

                for k in range(5):
                    score_value = random.randint(1, 5)
                    date = datetime.datetime.now()
                    test_score = Score(score=score_value, user=test_user, team=new_team, date_registered=date)
                    test_score.save()

                    team_score_counter += 1
                    team_sum += score_value

                user_counter += 1

            team_average = team_sum / team_score_counter
            new_team.last_average_score = team_average
            new_team.diverse_scores = True
            new_team.number_of_scores = team_score_counter
            new_team.save()

        return Response('data generated', status=status.HTTP_200_OK)