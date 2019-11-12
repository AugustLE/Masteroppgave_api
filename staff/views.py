from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from data.models import Subject, Team, IsResponsibleForTeam, UserIsOnTeam, Score
from data.serializers import SubjectSerializer
from data.serializers import TeamSerializer


class SubjectList(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def get(self, request):
        user = request.user
        subjects = Subject.objects.filter(isinstructorforsubject__instructor=user)
        serializer = SubjectSerializer(subjects, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class Overview(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def get(self, request):
        user = request.user
        subject = Subject.objects.get(pk=user.selected_subject_id)
        subject_data = SubjectSerializer(subject, many=False).data
        teams = Team.objects.filter(subject=subject)
        total_sum = 0
        counter = 0
        for team in teams:
            total_sum += team.last_average_score
            counter += 1

        total_average = None
        if total_sum > 0 and counter > 0:
            total_average = total_sum/counter

        teams_below = Team.objects.filter(last_average_score__lte=2.5).count()
        responsible_teams = Team.objects.filter(isresponsibleforteam__user=user, subject=subject)
        responsible_teams_data = None
        if responsible_teams.count() > 0:
            responsible_teams_data = TeamSerializer(responsible_teams, many=True).data

        return_object = {
            'total_average': total_average,
            'number_teams_below': teams_below,
            'responsible_teams': responsible_teams_data,
            'subject': subject_data
        }

        return Response(return_object, status=status.HTTP_200_OK)


class TeamList(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def get(self, request):

        user = request.user
        subject = Subject.objects.get(pk=user.selected_subject_id)
        teams = Team.objects.filter(subject=subject)

        team_data = TeamSerializer(teams, many=True).data
        subject_data = SubjectSerializer(subject, many=False).data

        return_object = {
            'teams': team_data,
            'subject': subject_data
        }

        return Response(return_object, status=status.HTTP_200_OK)


class TeamInfo(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def get(self, request, team_id):

        team = Team.objects.get(pk=team_id)
        team_data = TeamSerializer(team, many=False).data
        responsible_name = team.responsible.name

        is_on_teams = UserIsOnTeam.objects.filter(team=team)
        members = []
        for member in is_on_teams:

            member_scores = Score.objects.filter(user=member.user, team=team)
            sum_scores = 0
            counter = 0
            member_average = None
            for score in member_scores:
                sum_scores += score.score
                counter += 1

            if counter > 0 and sum_scores > 0:
                member_average = sum_scores/counter

            members.append({'name': member.user.name, 'average_score': member_average})

        return_object = {
            'responsible': responsible_name,
            'members': members,
            'team': team_data
        }

        return Response(return_object, status=status.HTTP_200_OK)
