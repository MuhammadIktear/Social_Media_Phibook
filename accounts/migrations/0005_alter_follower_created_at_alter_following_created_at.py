# Generated by Django 5.0.6 on 2024-08-20 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_follower_created_at_following_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='follower',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='following',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
