from django.contrib import admin
from .models import Team
from .models import Subject
from .models import Score
from .models import UserIsOnTeam
from .models import IsTeachingAssistantForSubject
from .models import EnrolledInSubject


class TeamInline(admin.StackedInline):

    model = Team
    extra = 1


class UserIsOnTeamInline(admin.StackedInline):

    model = UserIsOnTeam
    extra = 0


class SubjectAdmin(admin.ModelAdmin):

    inlines = [TeamInline]


class TeamAdmin(admin.ModelAdmin):

    inlines = [UserIsOnTeamInline]

    list_display = ('name', 'subject')
    search_fields = ('name', 'subject')


class ScoreAdmin(admin.ModelAdmin):

    list_display = ('user', 'team')


class IsTeachingAssistantAdmin(admin.ModelAdmin):

    list_display = ('teaching_assistant', 'subject')


class UserIsOnTeamAdmin(admin.ModelAdmin):

    list_display = ('user', 'team')


class EnrolledInSubjectAdmin(admin.ModelAdmin):

    list_display = ('user', 'subject')


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(IsTeachingAssistantForSubject, IsTeachingAssistantAdmin)
admin.site.register(UserIsOnTeam, UserIsOnTeamAdmin)
admin.site.register(EnrolledInSubject, EnrolledInSubjectAdmin)