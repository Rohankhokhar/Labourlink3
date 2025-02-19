# Generated by Django 5.1.3 on 2025-02-13 10:17

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('labour', '0005_alter_labourpersonalinformation_date_of_birth_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartiesDetail',
            fields=[
                ('llid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('firm_name', models.CharField(max_length=255)),
                ('party_name', models.CharField(max_length=255)),
                ('party_mobile', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('description', models.TextField()),
                ('labour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parties_details', to='labour.labour')),
            ],
            options={
                'verbose_name': 'Party Detail',
                'verbose_name_plural': 'Parties Details',
                'ordering': ['party_name'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_description', models.TextField()),
                ('assign_date', models.DateField(auto_now_add=True)),
                ('complete_date', models.DateField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('received_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('pending_amount', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('payment_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('partial', 'Partially Paid')], default='pending', max_length=10)),
                ('party', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='parties.partiesdetail')),
            ],
        ),
    ]
