# Generated by Django 5.1.6 on 2025-05-11 17:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_alter_account_birthday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='no_ord',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='books.order', verbose_name='Номер заказа (id)'),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], max_length=2, verbose_name='Рейтинг'),
        ),
        migrations.AlterField(
            model_name='shop',
            name='city',
            field=models.CharField(choices=[('Апрелевка', 'Апрелевка'), ('Балашиха', 'Балашиха'), ('Бронницы', 'Бронницы'), ('Верея', 'Верея'), ('Видное', 'Видное'), ('Волоколамск', 'Волоколамск'), ('Воскресенск', 'Воскресенск'), ('Высоковск', 'Высоковск'), ('Голицыно', 'Голицыно'), ('Дзержинский', 'Дзержинский'), ('Дмитров', 'Дмитров'), ('Долгопрудный', 'Долгопрудный'), ('Домодедово', 'Домодедово'), ('Дрезна', 'Дрезна'), ('Дубна', 'Дубна'), ('Егорьевск', 'Егорьевск'), ('Жуковский', 'Жуковский'), ('Зарайск', 'Зарайск'), ('Звенигород', 'Звенигород'), ('Ивантеевка', 'Ивантеевка'), ('Истра', 'Истра'), ('Кашира', 'Кашира'), ('Климовск', 'Климовск'), ('Клин', 'Клин'), ('Коломна', 'Коломна'), ('Королев', 'Королев'), ('Котельники', 'Котельники'), ('Красноармейск', 'Красноармейск'), ('Красногорск', 'Красногорск'), ('Краснозаводск', 'Краснозаводск'), ('Краснознаменск', 'Краснознаменск'), ('Кубинка', 'Кубинка'), ('Куровское', 'Куровское'), ('Ликино-Дулево', 'Ликино-Дулево'), ('Лобня', 'Лобня'), ('Лосино-Петровский', 'Лосино-Петровский'), ('Луховицы', 'Луховицы'), ('Лыткарино', 'Лыткарино'), ('Можайск', 'Можайск'), ('Москва', 'Москва'), ('Мытищи', 'Мытищи'), ('Наро-Фоминск', 'Наро-Фоминск'), ('Ногинск', 'Ногинск'), ('Одинцово', 'Одинцово'), ('Ожерелье', 'Ожерелье'), ('Орехово-Зуево', 'Орехово-Зуево'), ('Павловский Посад', 'Павловский Посад'), ('Пересвет', 'Пересвет'), ('Подольск', 'Подольск'), ('Протвино', 'Протвино'), ('Пушкино', 'Пушкино'), ('Пущино', 'Пущино'), ('Раменское', 'Раменское'), ('Реутов', 'Реутов'), ('Рошаль', 'Рошаль'), ('Руза', 'Руза'), ('Сергиев Посад', 'Сергиев Посад'), ('Серпухов', 'Серпухов'), ('Солнечногорск', 'Солнечногорск'), ('Старая Купавна', 'Старая Купавна'), ('Ступино', 'Ступино'), ('Талдом', 'Талдом'), ('Фрязино', 'Фрязино'), ('Химки', 'Химки'), ('Хотьково', 'Хотьково'), ('Черноголовка', 'Черноголовка'), ('Чехов', 'Чехов'), ('Шатура', 'Шатура'), ('Шаховская', 'Шаховская'), ('Щелково', 'Щелково'), ('Щербинка', 'Щербинка'), ('Электрогорск', 'Электрогорск'), ('Электросталь', 'Электросталь'), ('Электроугли', 'Электроугли'), ('Юбилейный', 'Юбилейный'), ('Яхрома', 'Яхрома')], max_length=20, verbose_name='Город'),
        ),
    ]
