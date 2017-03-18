# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-03-18 00:49
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='school', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=256)),
                ('subject1', models.CharField(blank=True, choices=[('al', 'Algebra'), ('nt', 'Number Theory'), ('ge', 'Geometry'), ('cp', 'Counting and Probability')], max_length=2, verbose_name='Subject 1')),
                ('subject2', models.CharField(blank=True, choices=[('al', 'Algebra'), ('nt', 'Number Theory'), ('ge', 'Geometry'), ('cp', 'Counting and Probability')], max_length=2, verbose_name='Subject 2')),
                ('size', models.IntegerField(choices=[(0, 'Default'), (1, 'Adult Small'), (2, 'Adult Medium'), (3, 'Adult Large'), (4, 'Adult Extra Large')], default=0)),
                ('attending', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('division', models.IntegerField(choices=[(1, 'Pascal'), (2, 'Ramanujan')])),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='frontend.School')),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='frontend.Team'),
        ),
    ]
