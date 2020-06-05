# Generated by Django 3.0.4 on 2020-06-04 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toast_cal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PubCalendar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=30)),
                ('calendarId', models.CharField(default='적음', max_length=30)),
                ('title', models.CharField(max_length=30)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('count', models.IntegerField()),
                ('conutPer', models.FloatField()),
            ],
            options={
                'db_table': 'PubCalendar',
            },
        ),
        migrations.CreateModel(
            name='PubCalID',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('color', models.CharField(max_length=30)),
                ('bgColor', models.CharField(max_length=30)),
                ('dragBgColor', models.CharField(max_length=30)),
                ('borderColor', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'PubCalID',
            },
        ),
    ]