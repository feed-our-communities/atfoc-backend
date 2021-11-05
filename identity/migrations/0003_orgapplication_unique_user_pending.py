# Generated by Django 3.2.7 on 2021-11-05 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0002_auto_20211103_0429'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='orgapplication',
            constraint=models.UniqueConstraint(condition=models.Q(('status', 0)), fields=('user',), name='unique_user_pending'),
        ),
    ]
