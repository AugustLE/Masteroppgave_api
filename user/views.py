from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status
from .models import CustomUser


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
        name = request.data.get('name')
        auth_token = request.data.get('auth_token')
        password = request.data.get('password')

        if CustomUser.objects.filter(username=userid).count() == 0:
            user = CustomUser(username=userid, name=name)
            user.set_password(password)
            user.save()

        user = authenticate(username=userid, password=password)

        Token.objects.filter(user=user).delete()
        new_token = Token(user=user, key=auth_token)
        new_token.save()

        serializer = UserSerializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangeUserRole(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @csrf_exempt
    def post(self, request):

        role_type = request.data.get('role')
        user = request.user
        if role_type == 'SD':
            role = 'SD'
        else:
            role = 'IN'

        user.role = role
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
