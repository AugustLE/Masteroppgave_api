from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from .serializers import EnrollmentSerializer
from .models import Subject
from .models import EnrolledInSubject
from .models import PreEnrollmentEntry
from user.serializers import UserSerializer


class EnrollmentList(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    # This method enroll the student in the registered courses, and sends back the enrolled courses
    @csrf_exempt
    def post(self, request):

        user = request.user

        entries = PreEnrollmentEntry.objects.filter(student_name__contains=user.name)

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


class SelectSubject(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def post(self, request):

        user = request.user
        subject_id = request.data.get('subject_id')
        subject = Subject.objects.get(pk=subject_id)

        enrolled = EnrolledInSubject.objects.filter(user=user, active=True)
        if enrolled.count() > 0:
            for entry in enrolled:
                entry.active = False
                entry.save()

        user.selected_subject_id = subject_id
        user.save()
        active_enrollment = EnrolledInSubject.objects.get(subject=subject)
        active_enrollment.active = True
        active_enrollment.save()

        serializer = UserSerializer(user, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)



