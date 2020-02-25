from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from data.models import Subject, Team, IsResponsibleForTeam, UserIsOnTeam, Score, PreTeamRegister
from user.models import CustomUser
from data.serializers import SubjectSerializer
from data.serializers import TeamSerializer


class Overview(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def get(self, request):
        user = request.user
        subject = Subject.objects.get(pk=user.selected_subject_id)
        subject_data = SubjectSerializer(subject, many=False).data
        teams = Team.objects.filter(subject=subject)
        number_of_teams = teams.count()
        total_sum = 0
        counter = 0
        for team in teams:
            total_sum += team.last_average_score
            counter += 1

        total_average = None
        if total_sum > 0 and counter > 0:
            total_average = round(total_sum/counter, 1)

        teams_below = Team.objects.filter(last_average_score__lte=2.5, diverse_scores=True).count()
        responsible_teams = Team.objects.filter(isresponsibleforteam__user=user, subject=subject)
        responsible_teams_data = None
        if responsible_teams.count() > 0:
            responsible_teams_data = TeamSerializer(responsible_teams, many=True).data

        return_object = {
            'total_average': total_average,
            'number_teams_below': teams_below,
            'responsible_teams': responsible_teams_data,
            'subject': subject_data,
            'number_of_teams': number_of_teams
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

        for team in team_data:
            if team['responsible'] == user.name:
                team['pinned'] = True
                team_data.insert(0, team_data.pop(team_data.index(team)))

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
        responsible_name = None
        if team.responsible:
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
        print(return_object)

        return Response(return_object, status=status.HTTP_200_OK)


class TeamUploader(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    ## Registrer PreTeamRegister .....
    @csrf_exempt
    def post(self, request):
        user = request.user
        team_json = request.data.get('team_json')
        for team in team_json:

            user_subject = Subject.objects.get(pk=user.selected_subject_id)
            responsible = None

            if Team.objects.filter(name=team['name']).count() == 0:
                current_team = Team(name=team['name'], subject=user_subject)
                current_team.save()
            else:
                current_team = Team.objects.get(name=team['name'], subject=user_subject)

            role = 'TA'
            feide_username = team['responsible']
            if team['instructor']:
                role = 'IN'
                feide_username = team['instructor']

            if CustomUser.objects.filter(username=feide_username).count() > 0:
                responsible = CustomUser.objects.get(username=feide_username)
                responsible.role = role
                responsible.save()

            if PreTeamRegister.objects.filter(feide_username=feide_username, team=current_team, subject=user_subject).count() == 0:
                pre_ta_register = PreTeamRegister(
                    feide_username=feide_username,
                    role=role,
                    team=current_team,
                    subject=user_subject
                )
                pre_ta_register.save()
            else:
                pre_ta_register = PreTeamRegister.objects.get(feide_username=feide_username, team=current_team, subject=user_subject)
                pre_ta_register.role = role
                pre_ta_register.save()



            # Dette må også gjøres når en TA registrerer seg etter et team er laget
            if responsible and IsResponsibleForTeam.objects.filter(user=responsible, team=current_team).count() == 0:
                new_responsible = IsResponsibleForTeam(user=responsible, team=current_team)
                new_responsible.save()
                current_team.responsible = responsible
                current_team.save()

            for member in team['members']:
                if CustomUser.objects.filter(username=member).count() > 0:
                    current_member = CustomUser.objects.get(username=member)
                    if UserIsOnTeam.objects.filter(user=current_member, team__subject=user_subject).count() == 0:
                        new_onteam = UserIsOnTeam(user=current_member, team=current_team)
                        new_onteam.save()
                else:
                    if PreTeamRegister.objects.filter(feide_username=member).count() == 0:
                        pre_student_register = PreTeamRegister(
                            feide_username=member,
                            team=current_team,
                            role='SD',
                            subject=user_subject
                        )
                        pre_student_register.save()

        return Response({}, status=status.HTTP_200_OK)
