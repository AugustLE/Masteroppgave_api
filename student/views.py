from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from data.models import Team, Subject, UserIsOnTeam
from .serializers import TeamSerializer


class TeamList(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def get(self, request, subject_id):

        user = request.user

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
        team_password = request.data.get('team_password')
        team = Team.objects.get(pk=team_id)
        if team_password != team.password:
            return Response({'message': 'wrong_password'})

        register_on_team = UserIsOnTeam(team=team, user=user)
        register_on_team.save()

        team_serializer = TeamSerializer(team, many=False)

        return Response(team_serializer.data, status=status.HTTP_200_OK)
