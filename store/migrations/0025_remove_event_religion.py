# Generated by Django 5.0.6 on 2024-08-13 05:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0024_remove_event_occasion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='religion',
        ),
    ]