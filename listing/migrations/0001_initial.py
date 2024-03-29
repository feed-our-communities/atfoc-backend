# Generated by Django 3.2.7 on 2021-11-15 01:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('identity', '0004_auto_20211106_0212'),
    ]

    operations = [
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('donation_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('description', models.TextField()),
                ('picture', models.FileField(upload_to='donations/')),
                ('expiration_date', models.DateField(blank=True, default=None)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('deactivation_time', models.DateTimeField(blank=True, default=None, null=True)),
                ('org_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='identity.organization')),
            ],
        ),
        migrations.CreateModel(
            name='DonationTraits',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trait', models.IntegerField(choices=[(0, 'is_cans'), (1, 'is_perishable')])),
                ('donation_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='listing.donation')),
            ],
        ),
    ]
