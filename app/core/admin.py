"""
Django admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
from django.utils.translation import gettext_lazy as _  # django translation utility

"""
Django translation utility imported as _ is a common best practice
used to automatically translate pages. We can import is as e.g. translate
but _ is just a convention to make code shorter, especially when it is used
very frequently. We don;t really need it to use it here because we do not intend
to have translated pages but it's just future proof - good practice
"""

"""
Note we are overwritting the original (base) UserAdmin class
We imported UserAdmin as BaseUserAdmin and then we overwrite
the UserAdmin class

How to create a super user in Django:
docker-compose run --rm app sh -c "python manage.py createsuperuser"
"""

class UserAdmin(BaseUserAdmin):
    """Defines (overwrites) the admin page for users"""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (  # we need it to make User Add form running after model customisation
        (None, {
            'classes': ('wide',),  # optional - it's just formatting
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),  # this must be a tupe (hence ,) or use list insted of tupples
    )



# Registering custom models
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
