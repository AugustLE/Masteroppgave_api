from django.db import models
from user.models import CustomUser


class Subject(models.Model):

    code = models.CharField(verbose_name='code', max_length=20)
    name = models.CharField(verbose_name='name', max_length=150)
    instructor = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.code + ' - ' + self.name


class Team(models.Model):

    name = models.CharField(verbose_name='name', max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    password = models.CharField(max_length=20)
    last_average_score = models.DecimalField(max_digits=10, decimal_places=1, default=0)

    def __str__(self):
        return self.name


class UserIsOnTeam(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)


class Score(models.Model):

    score = models.IntegerField(verbose_name='score')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    date_registered = models.DateTimeField(verbose_name='date_registered') ## in prod auto_now_add=True

    def __str__(self):
        return self.user.name


class IsTeachingAssistantForSubject(models.Model):

    teaching_assistant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)


class IsInstructorForSubject(models.Model):

    instructor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)


class EnrolledInSubject(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)


class PreEnrollmentEntry(models.Model):

    student_name = models.CharField(verbose_name='student_name', max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    enrolled = models.BooleanField(default=False)


class IsResponsibleForTeam(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'team')