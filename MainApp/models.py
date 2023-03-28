from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext as _

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, name, last_name, password=None, is_superuser=False):
        if not email:
            raise ValueError("Debes digitar un email")
        if not password:
            raise ValueError("Debes digitar una contraseña")
        if not name:
            raise ValueError("Debes digitar un nombre")
        if not last_name:
            raise ValueError("Debes digitar un apellido")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.name = name
        user.last_name = last_name
        user.set_password(password)  # change password to hash
        user.is_superuser = is_superuser
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("El usuario debe tener un email")
        if not password:
            raise ValueError("El usuario debe tener una contraseña")
        if not name:
            raise ValueError("Debes digitar un nombre")
        if not last_name:
            raise ValueError("Debes digitar un apellido")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.name = name
        user.last_name = last_name
        user.set_password(password)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    name = models.CharField(_("Nombre/s"), max_length=80)
    last_name = models.CharField(_("Apellido/s"), max_length=80)
    email = models.EmailField(_("Correo"), max_length=254, unique=True)
    password = models.CharField(_("Contraseña"), max_length=128)
    last_login = models.DateTimeField(_("Último Login"), null=True)
    created_at = models.DateTimeField(_("Creado"), auto_now_add=True, max_length=0)
    is_superuser = models.BooleanField(_("Estado Super Usuario"), default=0)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['name', 'last_name']

    objects = UserManager()

class Audio(models.Model):
    user = models.ForeignKey(User, verbose_name=_("Usuario"), on_delete=models.CASCADE)
    name_audio = models.CharField(_("Nombre Audio"), max_length=150)
