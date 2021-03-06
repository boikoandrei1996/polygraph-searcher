# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-05 10:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=255, unique=True)),
                ('title', models.TextField()),
                ('content', models.TextField()),
                ('domain', models.CharField(db_index=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='StemDocumentRelationModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count_stem', models.IntegerField()),
                ('type_stem', models.IntegerField()),
                ('rank_weight', models.FloatField()),
                ('doc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polygraph_web.DocumentModel')),
            ],
        ),
        migrations.CreateModel(
            name='StemModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stem', models.CharField(max_length=255, unique=True)),
                ('idf', models.FloatField()),
            ],
        ),
        migrations.AddField(
            model_name='stemdocumentrelationmodel',
            name='stem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polygraph_web.StemModel'),
        ),
    ]
