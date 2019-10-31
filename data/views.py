from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .serializers import EnrollmentSerializer
from .models import Subject
from .models import EnrolledInSubject
from .models import PreEnrollmentEntry
from rest_framework import status


class EnrollmentList(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    # This method enroll the student in the registered courses, and sends back the enrolled courses
    @csrf_exempt
    def post(self, request):

        user = request.user

        entries = PreEnrollmentEntry.objects.filter(student_name__contains=user.name, enrolled=False)

        for entry in entries:
            if EnrolledInSubject.objects.filter(subject=entry.subject, user=user).count() == 0:
                enroll_student = EnrolledInSubject(user=user, subject=entry.subject)
                enroll_student.save()
                entry.enrolled = True
                entry.save()

        enrollment_list = EnrolledInSubject.objects.filter(user=user)
        serializer = EnrollmentSerializer(enrollment_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @csrf_exempt
    def get(self, request):

        user = request.user
        enrollment_list = EnrolledInSubject.objects.filter(user=user)
        serializer = EnrollmentSerializer(enrollment_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)