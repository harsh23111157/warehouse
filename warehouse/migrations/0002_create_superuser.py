from django.db import migrations

def create_default_superuser(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.filter(username='admin').first()
    if not user:
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    else:
        user.set_password('admin123')
        user.is_staff = True
        user.is_superuser = True
        user.save()

def remove_default_superuser(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_superuser, reverse_code=remove_default_superuser),
    ]
