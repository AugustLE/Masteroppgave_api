from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


ROLES = [
        ('SD', 'Student'),
        ('TA', 'Teaching assistant'),
        ('IN', 'Instructor'),
    ]


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            username=username, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(
            username,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    username = models.CharField(
        verbose_name='username',
        max_length=200,
        unique=True,
    )
    user_id = models.CharField(verbose_name='user_id', max_length=200)
    date_joined = models.DateTimeField(verbose_name='date_joined', auto_now_add=True)
    name = models.CharField(verbose_name='name', max_length=100)
    role = models.CharField(verbose_name='role', max_length=40, choices=ROLES, blank=True, null=True)
    selected_subject_id = models.CharField(max_length=10000, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def get_username(self):
        return self.username

    def get_name(self):
        return self.name

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


def userprofile_dirctory_path(instance, filename):
    return 'imagedir/userprofiles/{0}/{1}'.format(instance.id, filename)


