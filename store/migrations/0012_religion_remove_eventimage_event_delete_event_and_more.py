# Generated by Django 5.0.6 on 2024-08-01 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_delete_passwordreset'),
    ]

    operations = [
        migrations.CreateModel(
            name='Religion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('religion', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='eventimage',
            name='event',
        ),
        migrations.DeleteModel(
            name='Event',
        ),
        migrations.DeleteModel(
            name='EventImage',
        ),
    ]