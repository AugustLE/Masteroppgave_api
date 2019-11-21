from django.contrib import admin
from .models import Team, Subject, Score, UserIsOnTeam, IsTeachingAssistantForSubject, EnrolledInSubject, \
    PreEnrollmentEntry, IsInstructorForSubject, IsResponsibleForTeam


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

    list_display = ('name', 'subject', 'last_average_score')
    search_fields = ('name', 'subject__code', 'subject__name')


class ScoreAdmin(admin.ModelAdmin):

    list_display = ('user', 'team', 'score', 'date_registered')
    # readonly_fields = ('date_registered',)


class IsTeachingAssistantAdmin(admin.ModelAdmin):

    list_display = ('teaching_assistant', 'subject')


class IsInstructorAdmin(admin.ModelAdmin):
    list_display = ('instructor', 'subject')


class UserIsOnTeamAdmin(admin.ModelAdmin):

    list_display = ('user', 'team')
    search_fields = ('user__username', 'team__name')


class EnrolledInSubjectAdmin(admin.ModelAdmin):

    list_display = ('user', 'subject')


class PreEnrollmentEntryAdmin(admin.ModelAdmin):

    list_display = ('student_name', 'subject')
    search_fields = ('student_name', 'subject__code', 'subject__name')


class IsResponsibleForTeamAdmin(admin.ModelAdmin):
    list_display = ('user', 'team')


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(IsTeachingAssistantForSubject, IsTeachingAssistantAdmin)
admin.site.register(UserIsOnTeam, UserIsOnTeamAdmin)
admin.site.register(EnrolledInSubject, EnrolledInSubjectAdmin)
admin.site.register(PreEnrollmentEntry, PreEnrollmentEntryAdmin)
admin.site.register(IsInstructorForSubject, IsInstructorAdmin)
admin.site.register(IsResponsibleForTeam, IsResponsibleForTeamAdmin)