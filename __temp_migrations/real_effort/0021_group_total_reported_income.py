# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-06-17 23:28
from __future__ import unicode_literals

from django.db import migrations
import otree.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('real_effort', '0020_player_spanish'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='total_reported_income',
            field=otree.db.models.CurrencyField(null=True),
        ),
    ]