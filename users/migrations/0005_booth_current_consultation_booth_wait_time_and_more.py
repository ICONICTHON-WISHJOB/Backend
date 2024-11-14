# Generated by Django 5.1.3 on 2024-11-14 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_booth_day_alter_booth_floor'),
    ]

    operations = [
        migrations.AddField(
            model_name='booth',
            name='current_consultation',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booth',
            name='wait_time',
            field=models.IntegerField(default=0),
        ),
        migrations.RemoveField(
            model_name='booth',
            name='queue',
        ),
        migrations.AddField(
            model_name='booth',
            name='queue',
            field=models.JSONField(default=list),
        ),
    ]