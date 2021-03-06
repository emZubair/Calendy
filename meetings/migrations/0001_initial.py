# Generated by Django 3.2 on 2022-02-16 18:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('slot_duration_in_minutes', models.PositiveIntegerField(choices=[(15, 15), (30, 30), (45, 45)], default=15)),
                ('reserver_name', models.CharField(blank=True, max_length=256, null=True)),
                ('reserver_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meetings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
