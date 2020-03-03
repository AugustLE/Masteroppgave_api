from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from data.models import Team, Subject, UserIsOnTeam, Score
from data.serializers import SubjectSerializer
from data.serializers import TeamSerializer
from user.serializers import UserSerializer
from .serializers import ScoreSerializer
from django.db.models import Sum
import datetime
import pytz


def get_current_oslo_time():
    tz = pytz.timezone('Europe/Oslo')
    utc_time = datetime.datetime.utcnow()
    date_created = pytz.utc.localize(utc_time, is_dst=None).astimezone(tz)
    date_created = date_created.replace(tzinfo=None)
    return date_created


class TeamList(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def get(self, request):

        user = request.user
        subject_id = user.selected_subject_id

        subject = Subject.objects.get(pk=subject_id)
        team = None
        user_on_team = UserIsOnTeam.objects.filter(user=user, team__subject=subject)
        if user_on_team.count() > 0:
            team = TeamSerializer(user_on_team[0].team, many=False).data

        teams = Team.objects.filter(subject=subject)
        serializer_many = TeamSerializer(teams, many=True)

        return Response({'team': team, 'teams': serializer_many.data}, status=status.HTTP_200_OK)


class SelectTeam(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def post(self, request):

        user = request.user
        team_id = request.data.get('team_id')
        team = Team.objects.get(pk=team_id)
        """team_password = request.data.get('team_password')
        team = Team.objects.get(pk=team_id)
        if team_password != team.password:
            return Response({'message': 'wrong_password'})"""

        register_on_team = UserIsOnTeam(team=team, user=user)
        register_on_team.save()

        team_serializer = TeamSerializer(team, many=False)

        return Response(team_serializer.data, status=status.HTTP_200_OK)


class TeamStatus(APIView):

    @csrf_exempt
    def get(self, request):

        user = request.user
        subject = Subject.objects.get(pk=user.selected_subject_id)
        team = UserIsOnTeam.objects.get(user=user, team__subject=subject).team

        subject_serializer = SubjectSerializer(subject, many=False)
        team_serializer = TeamSerializer(team, many=False)

        ordered_scores = Score.objects.filter(user=user, team=team).order_by('-date_registered')
        last_score = None
        last_score_value = None
        if ordered_scores.count() > 0:
            last_score = ordered_scores[0]
            last_score_value = last_score.score

        today = datetime.date.today()
        last_monday = today - datetime.timedelta(days=today.weekday())
        # coming_monday = today + datetime.timedelta(days=-today.weekday(), weeks=1)

        has_rated_this_week = False
        if last_score and last_score.date_registered.date() >= last_monday:
            has_rated_this_week = True

        responsible_name = team.responsible.name

        is_on_teams = UserIsOnTeam.objects.filter(team=team)
        member_names = []
        for member in is_on_teams:
            member_names.append(member.user.name)

        return_object = {
            'subject': subject_serializer.data,
            'team': team_serializer.data,
            'last_score': last_score_value,
            'has_rated_this_week': has_rated_this_week,
            'team_members': member_names,
            'team_responsible': responsible_name
        }

        return Response(return_object, status=status.HTTP_200_OK)


class RegisterScore(APIView):

    @csrf_exempt
    def post(self, request):

        score_value = request.data.get('score_value')
        team_id = request.data.get('team_id')

        team = Team.objects.get(pk=team_id)
        all_scores = Score.objects.filter(team=team)
        number_of_scores = all_scores.count()
        score_sum = all_scores.aggregate(Sum('score'))['score__sum']
        if not score_sum:
            score_sum = 0

        participants = []
        anonymous_scores = 0
        for score in all_scores:
            if score.user:
                participant = score.user.username
                if participant not in participants:
                    participants.append(participant)
            else:
                anonymous_scores += 1

        diverse_scores = False
        if len(participants) + anonymous_scores > 3:
            diverse_scores = True

        time_now = get_current_oslo_time()
        new_score = Score(score=score_value, user=request.user, team=team, date_registered=time_now)
        new_score.save()

        new_average = (score_sum + score_value) / (number_of_scores + 1)
        team.last_average_score = new_average
        team.number_of_scores = number_of_scores + 1
        team.diverse_scores = diverse_scores
        team.save()

        team_data = TeamSerializer(team, many=False).data

        return_object = {
            'team': team_data,
            'last_score': score_value,
            'has_rated_this_week': True
        }

        return Response(return_object, status=status.HTTP_200_OK)


class UnregisterFromTeam(APIView):

    @csrf_exempt
    def post(self, request):

        user = request.user
        subject = Subject.objects.get(pk=user.selected_subject_id)
        user_on_team = UserIsOnTeam.objects.get(user=user, team__subject=subject)
        user_on_team.delete()
        return Response({}, status=status.HTTP_200_OK)


class ContactInfo(APIView):

    @csrf_exempt
    def get(self, request):

        user = request.user
        subject = Subject.objects.get(pk=user.selected_subject_id)
        team = UserIsOnTeam.objects.get(user=user, team__subject=subject).team
        responsible = team.responsible
        response_data = UserSerializer(responsible, many=False).data
        return Response(response_data, status=status.HTTP_200_OK)


class History(APIView):

    @csrf_exempt
    def get(self, request):

        user = request.user
        subject = Subject.objects.get(pk=user.selected_subject_id)
        scores = Score.objects.filter(user=user, team__subject=subject)
        scores = scores.order_by('-date_registered')
        return_object = ScoreSerializer(scores, many=True).data

        return Response(return_object, status=status.HTTP_200_OK)

