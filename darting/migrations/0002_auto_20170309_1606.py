# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-09 16:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('darting', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='turn',
            name='dart1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='turn1', to='darting.Dart'),
        ),
        migrations.AlterField(
            model_name='turn',
            name='dart2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='turn2', to='darting.Dart'),
        ),
        migrations.AlterField(
            model_name='turn',
            name='dart3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='turn3', to='darting.Dart'),
        ),
    ]
