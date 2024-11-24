# Generated by Django 5.1.3 on 2024-11-24 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0002_activeuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='PopularCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', models.IntegerField(unique=True)),
                ('views', models.IntegerField(default=0)),
            ],
        ),
    ]
