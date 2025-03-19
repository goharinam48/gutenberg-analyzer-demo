# Generated by Django 4.2.20 on 2025-03-18 16:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_id', models.CharField(max_length=20, unique=True)),
                ('text', models.TextField()),
                ('metadata', models.JSONField()),
                ('accessed_by', models.ManyToManyField(related_name='accessed_books', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
