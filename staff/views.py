# coding=utf-8
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from data.models import Subject, Team, IsResponsibleForTeam, UserIsOnTeam, Score, PreTeamRegister, RequestAuthority, \
    PinOnTeam
from user.models import CustomUser
from data.serializers import SubjectSerializer
from data.serializers import TeamSerializer
from user.serializers import UserSerializer
import datetime


def get_teams_below(user):
    teams_below = Team.objects.filter(last_average_score__lte=2.5, diverse_scores=True)
    teams_below_data = TeamSerializer(teams_below, many=True).data
    for team in teams_below_data:
        db_team = Team.objects.get(pk=team['pk'])
        if PinOnTeam.objects.filter(user=user, team=db_team).count() > 0:
            team['pinned'] = True
    return teams_below_data


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
            if team.last_average_score > 0:
                total_sum += team.last_average_score
                counter += 1

        total_average = None
        if total_sum > 0 and counter > 0:
            total_average = round(total_sum/counter, 1)

        teams_below_data = get_teams_below(user)

        responsible_teams = Team.objects.filter(isresponsibleforteam__user=user, subject=subject)
        responsible_teams_data = None
        if responsible_teams.count() > 0:
            responsible_teams_data = TeamSerializer(responsible_teams, many=True).data

        return_object = {
            'total_average': total_average,
            'number_teams_below': len(teams_below_data),
            'teams_below': teams_below_data,
            'responsible_teams': responsible_teams_data,
            'subject': subject_data,
            'number_of_teams': number_of_teams,
            'number_of_teams_with_scores': counter
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

            db_team = Team.objects.get(pk=team['pk'])
            if PinOnTeam.objects.filter(user=user, team=db_team).count() > 0:
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
        responsible_email = None
        if team.responsible:
            responsible_name = team.responsible.name
            responsible_email = team.responsible.email

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

        if PinOnTeam.objects.filter(user=request.user, team=team).count() > 0:
            team_data['pinned'] = True

        responsible = {
            'name': responsible_name,
            'email': responsible_email
        }

        return_object = {
            'responsible': responsible,
            'responsible_email': responsible_email,
            'members': members,
            'team': team_data,
        }

        return Response(return_object, status=status.HTTP_200_OK)


class TeamUploader(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    ## Registrer PreTeamRegister .....
    @csrf_exempt
    def post(self, request):
        user = request.user
        team_json = request.data.get('team_json')
        for team in team_json:

            team_number_string = team['name'].split(' ')[1]
            team_number = int(team_number_string)
            user_subject = Subject.objects.get(pk=user.selected_subject_id)
            responsible = None

            if Team.objects.filter(name=team['name']).count() == 0:
                current_team = Team(name=team['name'], subject=user_subject, team_number=team_number)
                current_team.save()
            else:
                current_team = Team.objects.get(name=team['name'], subject=user_subject)

            role = 'TA'
            if not team['responsible'] and not team['instructor']:
                return Response({}, status=status.HTTP_200_OK)

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


class CheckAuthority(APIView):

    @csrf_exempt
    def get(self, request):

        user = request.user
        subject = Subject.objects.get(pk=user.selected_subject_id)
        if RequestAuthority.objects.filter(user=user, subject=subject, approved=True).count() > 0:
            return Response(True, status=status.HTTP_200_OK)

        if RequestAuthority.objects.filter(user=user, subject=subject, approved=False).count() == 0:
            return Response(None, status=status.HTTP_200_OK)

        return Response(False, status=status.HTTP_200_OK)

    @csrf_exempt
    def post(self, request):

        user = request.user
        subject = Subject.objects.get(pk=user.selected_subject_id)
        request_auth = RequestAuthority(user=user, subject=subject)
        request_auth.save()

        return Response(False, status=status.HTTP_200_OK)


class PinTeam(APIView):

    @csrf_exempt
    def post(self, request):

        user = request.user
        team_id = request.data.get('team_id')
        team = Team.objects.get(pk=team_id)
        if PinOnTeam.objects.filter(user=user, team=team).count() == 0:
            new_pin = PinOnTeam(user=user, team=team)
            new_pin.save()

        team_data = TeamSerializer(team, many=False).data
        team_data['pinned'] = True

        teams_below = get_teams_below(user)

        return_object = {
            'team': team_data,
            'teams_below': teams_below
        }
        return Response(return_object, status=status.HTTP_200_OK)

    @csrf_exempt
    def delete(self, request):

        user = request.user
        team_id = request.data.get('team_id')
        team = Team.objects.get(pk=team_id)
        old_pin = PinOnTeam.objects.get(user=user, team=team)
        old_pin.delete()
        team_data = TeamSerializer(team, many=False).data
        team_data['pinned'] = False
        teams_below = get_teams_below(user)

        return_object = {
            'team': team_data,
            'teams_below': teams_below
        }
        return Response(return_object, status=status.HTTP_200_OK)


class TeamHistory(APIView):

    @csrf_exempt
    def get(self, request, team_id):
        team = Team.objects.get(pk=team_id)
        scores = Score.objects.filter(team=team).order_by('-date_registered')

        history_dict = {}
        history_count_dict = {}
        next_monday_dict = {}
        user_score_dict = {}
        for score in scores:
            monday = score.date_registered - datetime.timedelta(days=score.date_registered.weekday())
            coming_monday_dt = score.date_registered + datetime.timedelta(days=-score.date_registered.weekday(), weeks=1)
            dict_key = str(monday.day) + '/' + str(monday.month) + '-' + str(monday.year)
            coming_monday = str(coming_monday_dt.day) + '/' + str(coming_monday_dt.month) + '-' + str(coming_monday_dt.year)

            if dict_key not in next_monday_dict:
                next_monday_dict[dict_key] = coming_monday

            if dict_key in history_dict.keys():
                history_dict[dict_key] += score.score
            else:
                history_dict[dict_key] = score.score

            if dict_key in history_count_dict.keys():
                history_count_dict[dict_key] += 1
            else:
                history_count_dict[dict_key] = 1

            user_data = UserSerializer(score.user, many=False).data
            score_date = str(score.date_registered.day) + '/' + str(score.date_registered.month)
            if dict_key not in user_score_dict:
                user_score_dict[dict_key] = [{'user': user_data, 'score': score.score, 'score_date': score_date}]
            else:
                user_score_dict[dict_key].append({'user': user_data, 'score': score.score, 'score_date': score_date})

        return_list = []
        for key in history_dict.keys():
            split_by_day = key.split('/')
            day = split_by_day[0]
            month = split_by_day[1].split('-')[0]
            year = key.split('-')[1]

            average_week = history_dict[key] / history_count_dict[key]
            first_monday = key.split('-')[0]
            last_monday = next_monday_dict[key].split('-')[0]
            week = first_monday + ' - ' + last_monday

            week_number = datetime.date(int(year), int(month), int(day)).isocalendar()[1]
            week_object = {
                'week': week,
                'week_number': week_number,
                'average': average_week,
                'year': year,
                'users': user_score_dict[key]
            }
            return_list.append(week_object)
        return Response(return_list, status=status.HTTP_200_OK)


class TeamUploader2(APIView):

    permission_classes = (permissions.IsAuthenticated,)

    @csrf_exempt
    def post(self, request):
        user = request.user
        user_subject = Subject.objects.get(pk=user.selected_subject_id)
        team_json = request.data.get('team_json')
        for team in team_json:

            team_number = int(team['team_number'])
            team_name = team['name']
            team_member = team['member']
            if Team.objects.filter(name=team_name, team_number=team_number, subject=user_subject).count() == 0:
                team = Team(name=team_name, team_number=team_number, subject=user_subject)
                team.save()
            else:
                team = Team.objects.get(name=team_name, team_number=team_number, subject=user_subject)

            if PreTeamRegister.objects.filter(feide_username=team_member, team=team, subject=user_subject).count() == 0:
                pre_member_register = PreTeamRegister(feide_username=team_member, role='SD', team=team, subject=user_subject)
                pre_member_register.save()

        return Response({}, status=status.HTTP_200_OK)