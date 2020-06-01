# Generated by Django 3.0.4 on 2020-05-29 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userID', models.CharField(max_length=30)),
                ('calendarId', models.CharField(default='전공 필수', max_length=30)),
                ('title', models.CharField(max_length=30)),
                ('category', models.CharField(default='time', max_length=30)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('isAllDay', models.BooleanField(default=False)),
                ('state', models.CharField(default='Busy', max_length=20)),
                ('calendarClass', models.CharField(default='public', max_length=20)),
            ],
            options={
                'db_table': 'Calendar',
            },
        ),
        migrations.CreateModel(
            name='CalID',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('color', models.CharField(max_length=30)),
                ('bgColor', models.CharField(max_length=30)),
                ('dragBgColor', models.CharField(max_length=30)),
                ('borderColor', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'CalID',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'Department',
            },
        ),
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('userID', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('department', models.CharField(max_length=50)),
                ('username', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=128)),
                ('phone', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'Professor',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('userID', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('department', models.CharField(max_length=50)),
                ('studentID', models.CharField(max_length=30)),
                ('username', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=128)),
                ('phone', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'Student',
            },
        ),
        migrations.CreateModel(
            name='Student_lecture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=30)),
                ('code', models.CharField(max_length=20)),
                ('codeClass', models.CharField(default='A', max_length=5)),
                ('professor', models.CharField(max_length=20)),
                ('period', models.CharField(max_length=20)),
                ('lecture_type', models.CharField(max_length=10)),
                ('department', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'Student_lecture',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('code', models.CharField(max_length=20)),
                ('codeClass', models.CharField(default='A', max_length=5)),
                ('professor', models.CharField(max_length=20)),
                ('period', models.CharField(max_length=20)),
                ('lecture_type', models.CharField(max_length=10)),
                ('department', models.CharField(max_length=20)),
                ('stdCount', models.IntegerField(default=0)),
                ('total_stdCount', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'Subject',
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('professor_id', models.CharField(max_length=30)),
                ('code', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=30)),
                ('lecture_type', models.CharField(max_length=30)),
                ('vote_status', models.CharField(max_length=30)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('agree_votes', models.IntegerField()),
                ('reject_votes', models.IntegerField()),
                ('all_students', models.IntegerField()),
            ],
            options={
                'db_table': 'Vote',
            },
        ),
    ]
