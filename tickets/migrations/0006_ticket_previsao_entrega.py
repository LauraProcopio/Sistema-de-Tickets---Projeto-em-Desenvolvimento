# Generated by Django 5.1.4 on 2025-01-29 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0005_alter_ticket_titulo'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='previsao_entrega',
            field=models.DateField(blank=True, null=True),
        ),
    ]
