# Generated by Django 5.1.3 on 2024-12-06 05:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labour', '0004_alter_labourpersonalinformation_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labourpersonalinformation',
            name='date_of_birth',
            field=models.DateField(default=datetime.date(2000, 1, 1)),
        ),
        migrations.AlterField(
            model_name='labourpersonalinformation',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], default='O', max_length=10),
        ),
    ]
