# Generated by Django 3.2 on 2021-05-01 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signups', '0009_auto_20210501_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signup',
            name='order_number',
            field=models.PositiveIntegerField(default=1),
        ),
    ]