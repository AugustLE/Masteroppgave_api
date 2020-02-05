from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status
from .models import CustomUser
from data.models import PreEnrollmentEntry, AuthorizedInstructor

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

        if CustomUser.objects.filter(username=username).count() == 0:
            user = CustomUser(username=username, user_id=userid, name=name)
            user.set_password(TEMP_PASSWORD)
            user.save()

        user = authenticate(username=username, password=TEMP_PASSWORD)

        is_authorized_instructor = False
        if AuthorizedInstructor.objects.filter(feide_username=username).count() > 0:
            is_authorized_instructor = True

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

#

#role_type = request.data.get('role')
#if role_type == 'student':
#    role = 'SD'
#else:
#    role = 'IN'
#
#
#
