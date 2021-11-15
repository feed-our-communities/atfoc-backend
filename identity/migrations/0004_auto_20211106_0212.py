# Generated by Django 3.2.7 on 2021-11-06 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0003_orgapplication_unique_user_pending'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='orgapplication',
            name='unique_user_pending',
        ),
        migrations.AddConstraint(
            model_name='joinrequest',
            constraint=models.UniqueConstraint(condition=models.Q(('status', 0)), fields=('user', 'organization'), name='unique_user_pending_joinrequest'),
        ),
        migrations.AddConstraint(
            model_name='orgapplication',
            constraint=models.UniqueConstraint(condition=models.Q(('status', 0)), fields=('user',), name='unique_user_pending_orgapplication'),
        ),
    ]