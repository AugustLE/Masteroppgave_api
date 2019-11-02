from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from data.models import Team, Subject
from .serializers import TeamSerializer


class TeamList(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def get(self, request, subject_id):

        subject = Subject.objects.get(pk=subject_id)
        teams = Team.objects.filter(subject=subject)
        serializer = TeamSerializer(teams, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

