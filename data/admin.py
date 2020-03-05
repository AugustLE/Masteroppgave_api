from django.contrib import admin
from .models import Team, Subject, Score, UserIsOnTeam, \
    IsResponsibleForTeam, PrivacyConsent, PreTeamRegister, RequestAuthority, PinOnTeam


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
    search_fields = ('user__name', 'team__name')
    # readonly_fields = ('date_registered',)


class UserIsOnTeamAdmin(admin.ModelAdmin):

    list_display = ('user', 'team')
    search_fields = ('user__username', )


class IsResponsibleForTeamAdmin(admin.ModelAdmin):
    list_display = ('user', 'team')


class PrivacyConsentAdmin(admin.ModelAdmin):
    list_display = ('username', 'date_accepted', 'has_accepted')
    search_fields = ('username', 'date_accepted', 'has_accepted')
    list_filter = ('has_accepted', )


class PreTeamRegisterAdmin(admin.ModelAdmin):

    list_display = ('feide_username', 'team', 'role')
    search_fields = ('feide_username', 'team__name')
    list_filter = ('role',)


class PinOnTeamAdmin(admin.ModelAdmin):

    list_display = ('user', 'team')


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(UserIsOnTeam, UserIsOnTeamAdmin)
admin.site.register(IsResponsibleForTeam, IsResponsibleForTeamAdmin)
admin.site.register(PrivacyConsent, PrivacyConsentAdmin)
admin.site.register(PreTeamRegister, PreTeamRegisterAdmin)
admin.site.register(RequestAuthority)
admin.site.register(PinOnTeam, PinOnTeamAdmin)