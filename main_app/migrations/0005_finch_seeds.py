# Generated by Django 4.0.5 on 2022-07-07 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_seed_alter_feeding_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='finch',
            name='seeds',
            field=models.ManyToManyField(to='main_app.seed'),
        ),
    ]