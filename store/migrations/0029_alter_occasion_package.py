# Generated by Django 5.0.6 on 2024-08-21 08:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0028_alter_occasion_package'),
    ]

    operations = [
        migrations.AlterField(
            model_name='occasion',
            name='package',
            field=models.ForeignKey(blank=True, default=12, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.package'),
        ),
    ]
