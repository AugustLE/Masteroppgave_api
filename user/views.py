from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status
from .models import CustomUser
from data.models import PreEnrollmentEntry, AuthorizedInstructor, PreTeamRegister, UserIsOnTeam, IsResponsibleForTeam, PrivacyConsent

TEMP_PASSWORD = '094huersgifu3h'
###


class UserDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @csrf_exempt
    def get(self, request):
        user = request.user
        if user:
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'No user exists'}, status=status.HTTP_404_NOT_FOUND)


class CreateOrLoginUser(APIView):
    permission_classes = (permissions.AllowAny, )

    @csrf_exempt
    def post(self, request):

        userid = request.data.get('userid')
        username = request.data.get('username')
        name = request.data.get('name')
        auth_token = request.data.get('auth_token')

        if PrivacyConsent.objects.filter(username=username).count() == 0:
            return Response({}, status=status.HTTP_200_OK)
        else:
            privacy_object = PrivacyConsent.objects.get(username=username)
            if not privacy_object.has_accepted:
                return Response({}, status=status.HTTP_200_OK)

        if CustomUser.objects.filter(username=username).count() == 0:
            user = CustomUser(username=username, user_id=userid, name=name)
            user.set_password(TEMP_PASSWORD)
            user.save()

        user = authenticate(username=username, password=TEMP_PASSWORD)

        is_authorized_instructor = False
        if AuthorizedInstructor.objects.filter(feide_username=username).count() > 0:
            is_authorized_instructor = True

        if PreTeamRegister.objects.filter(feide_username=username).count() > 0:
            pre_registers = PreTeamRegister.objects.filter(feide_username=username)
            for pre_register in pre_registers:
                #user_on_team = UserIsOnTeam(user=user)
                if UserIsOnTeam.objects.filter(user=user, team=pre_register.team).count() == 0 and pre_register.role == 'SD':
                    new_user_on_team = UserIsOnTeam(user=user, team=pre_register.team)
                    new_user_on_team.save()

                if IsResponsibleForTeam.objects.filter(user=user, team=pre_register.team).count() == 0 and pre_register.role == 'IN':
                    new_responsible = IsResponsibleForTeam(user=user, team=pre_register.team)
                    new_responsible.save()

            #for pre_register in pre_registers:
             #   pre_register.delete()

        Token.objects.filter(user=user).delete()
        new_token = Token(user=user, key=auth_token)
        new_token.save()

        user_data = UserSerializer(user, many=False).data
        user_data['is_authorized_instructor'] = is_authorized_instructor
        return Response(user_data, status=status.HTTP_200_OK)


class ChangeUserRole(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @csrf_exempt
    def post(self, request):

        role_type = request.data.get('role')
        user = request.user

        if role_type == 'SD':
            is_student = PreEnrollmentEntry.objects.filter(feide_username=user.username,
                                                           student_name=user.name).count() > 0
            if not is_student:
                return Response({'error': 'It seems like you´re not registered in this course'},
                                status=status.HTTP_200_OK)
        elif role_type == 'TA' or role_type == 'IN':
            is_authorized_instructor = AuthorizedInstructor.objects.filter(feide_username=user.username).count() > 0
            if not is_authorized_instructor:
                return Response({'error': 'You are not authorized for this role..'}, status=status.HTTP_200_OK)

        user.role = role_type
        user.save()

        serializer = UserSerializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)




