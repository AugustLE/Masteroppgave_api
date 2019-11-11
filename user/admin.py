from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import CustomUser
from data.models import Score
from django.utils.translation import gettext as _


class UserCreationForm(forms.ModelForm):

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('username',)

    def clear_password(self):

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):

        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        return self.initial["password"]


class ScoreInline(admin.StackedInline):

    model = Score
    extra = 0


class UserAdmin(BaseUserAdmin):

    inlines = [ScoreInline]

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'date_joined', 'is_admin', 'name', 'role')
    list_filter = ('is_admin', 'is_active', 'role')

    fieldsets = (
        (None, {'fields': ('username', 'user_id', 'password', 'name', 'role', 'selected_subject_id')}),
        ('Permissions', {'fields': ('is_admin', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
         ),
    )

    search_fields = ('username', 'name')
    ordering = ('name', )
    filter_horizontal = ()


admin.site.register(CustomUser, UserAdmin)
admin.site.unregister(Group)
