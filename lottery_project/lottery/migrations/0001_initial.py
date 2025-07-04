# Generated by Django 5.2.3 on 2025-06-26 17:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LotteryDraw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('draw_name', models.CharField(max_length=50)),
                ('draw_date', models.DateField()),
                ('draw_time', models.TimeField()),
                ('result_pdf', models.FileField(upload_to='lottery_results/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Prize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prize_type', models.CharField(choices=[('1st', '1st Prize'), ('2nd', '2nd Prize'), ('3rd', '3rd Prize'), ('cons', 'Consolation Prize'), ('4th', '4th Prize'), ('5th', '5th Prize'), ('6th', '6th Prize'), ('7th', '7th Prize'), ('8th', '8th Prize'), ('9th', '9th Prize')], max_length=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('ticket_code', models.CharField(max_length=20)),
                ('location', models.CharField(blank=True, max_length=100, null=True)),
                ('lottery_draw', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lottery.lotterydraw')),
            ],
        ),
    ]
