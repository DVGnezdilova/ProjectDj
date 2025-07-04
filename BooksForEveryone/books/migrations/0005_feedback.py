# Generated by Django 5.1.6 on 2025-06-04 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_historicalbook'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Проблема с заказом', 'Проблема с заказом'), ('Проблема с отзывом', 'Проблема с отзывом'), ('Ошибка в личных данных', 'Ошибка в личных данных'), ('Ошибка в информации на сайте', 'Ошибка в информации на сайте'), ('Другое', 'Другое')], verbose_name='Тип ошибки')),
                ('message', models.TextField(verbose_name='Сообщение')),
                ('email', models.EmailField(max_length=254, verbose_name='Email пользователя')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания заявки')),
            ],
            options={
                'verbose_name': 'заявка',
                'verbose_name_plural': 'Обратная связь',
            },
        ),
    ]
