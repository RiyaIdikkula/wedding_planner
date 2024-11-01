# Generated by Django 5.0.6 on 2024-09-22 16:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0033_remove_occasionimage_occasion_bookeditem_weddinginfo_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.package')),
            ],
        ),
        migrations.CreateModel(
            name='DressImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='dress_images/')),
                ('dress', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='store.dress')),
            ],
        ),
    ]
