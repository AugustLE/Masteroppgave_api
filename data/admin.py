from django.contrib import admin
from .models import Team, Subject, Score, UserIsOnTeam, \
    IsResponsibleForTeam, PrivacyConsent, PreTeamRegister


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


class UserIsOnTeamAdmin(admin.ModelAdmin):

    list_display = ('user', 'team')
    search_fields = ('user__username', 'team__name')


class IsResponsibleForTeamAdmin(admin.ModelAdmin):
    list_display = ('user', 'team')


class PrivacyConsentAdmin(admin.ModelAdmin):
    list_display = ('username', 'date_accepted', 'has_accepted')
    search_fields = ('username', 'date_accepted', 'has_accepted')
    list_filter = ('has_accepted', )


class PreTeamRegisterAdmin(admin.ModelAdmin):

    list_display = ('feide_username', 'team', 'role')
    search_fields = ('feide_username', 'team_name')
    list_filter = ('role',)


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(UserIsOnTeam, UserIsOnTeamAdmin)
admin.site.register(IsResponsibleForTeam, IsResponsibleForTeamAdmin)
admin.site.register(PrivacyConsent, PrivacyConsentAdmin)
admin.site.register(PreTeamRegister, PreTeamRegisterAdmin)
