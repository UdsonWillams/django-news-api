import logging

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations

logger = logging.getLogger(__name__)


def create_default_admin(apps, schema_editor):
    User = apps.get_model("users", "CustomUser")

    admin_username = getattr(settings, "DEFAULT_ADMIN_USERNAME")
    admin_email = getattr(settings, "DEFAULT_ADMIN_EMAIL")
    admin_password = getattr(settings, "DEFAULT_ADMIN_PASSWORD")

    if not User.objects.filter(username=admin_username).exists():
        User.objects.create(
            username=admin_username,
            email=admin_email,
            password=make_password(admin_password),
            first_name="Administrador",
            last_name="JOTA",
            is_staff=True,
            is_superuser=True,
            user_type="admin",
        )
        logger.info(f"Default admin user '{admin_username}' created successfully")
    else:
        logger.info(f"Admin user '{admin_username}' already exists")


def revert_default_admin(apps, schema_editor):
    User = apps.get_model("users", "CustomUser")
    admin_username = getattr(settings, "DEFAULT_ADMIN_USERNAME")
    admin_email = getattr(settings, "DEFAULT_ADMIN_EMAIL")

    deleted, _ = User.objects.filter(
        username=admin_username, email=admin_email
    ).delete()
    if deleted:
        logger.info(f"Default admin user '{admin_username}' removed")


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [migrations.RunPython(create_default_admin, revert_default_admin)]
