from django.db import models
from user.models import CustomUser
from user.models import ROLES


class Subject(models.Model):

    code = models.CharField(verbose_name='code', max_length=20)
    name = models.CharField(verbose_name='name', max_length=150)
    instructor = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.code + ' - ' + self.name


class Team(models.Model):

    name = models.CharField(verbose_name='name', max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    last_average_score = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    responsible = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL)
    number_of_scores = models.IntegerField(default=0)
    diverse_scores = models.BooleanField(default=False)
    team_number = models.IntegerField()

    class Meta:
        unique_together = ('name', 'subject',)

    def __str__(self):
        return self.name


class UserIsOnTeam(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'team')


class Score(models.Model):

    score = models.IntegerField(verbose_name='score')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    date_registered = models.DateTimeField(verbose_name='date_registered') ## in prod auto_now_add=True

    def __str__(self):
        return self.user.name


class IsResponsibleForTeam(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'team')


class PrivacyConsent(models.Model):
    has_accepted = models.BooleanField(default=False)
    date_accepted = models.DateTimeField(verbose_name='privacyConsent_date', null=True, blank=True)
    username = models.CharField(max_length=100, unique=True)


class AuthorizedInstructor(models.Model):

    feide_username = models.CharField(max_length=100, unique=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.feide_username


class PreTeamRegister(models.Model):

    feide_username = models.CharField(max_length=100)
    role = models.CharField(verbose_name='role', max_length=40, choices=ROLES, blank=True, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('feide_username', 'team',)