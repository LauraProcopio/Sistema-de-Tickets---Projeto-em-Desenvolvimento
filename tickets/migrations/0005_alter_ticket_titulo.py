# Generated by Django 5.1.4 on 2025-01-29 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_ticket_titulo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='titulo',
            field=models.CharField(max_length=255),
        ),
    ]
