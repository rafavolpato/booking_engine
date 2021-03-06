# Generated by Django 3.2 on 2022-01-28 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Blocked',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in', models.DateField()),
                ('check_out', models.DateField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('hotel_room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blocked', to='listings.hotelroom')),
                ('listing', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blocked', to='listings.listing')),
            ],
        ),
    ]
