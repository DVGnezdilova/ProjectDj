from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg
from django.db.models.functions import Cast
from django.db.models import FloatField

GENRE_CHOICES = (
    ('Фэнтези', 'Фэнтези'), 
    ('Фантастика', 'Фантастика '), 
    ('Любовный роман', 'Любовный роман'), 
    ('Детектив', 'Детектив'), 
    ('Приключения', 'Приключения'), 
    ('Классическая проза', 'Классическая проза'), 
    ('Современная проза', 'Современная проза'))

SALE_CHOICES = (
    ('10', '10'), 
    ('15', '15'), 
    ('20', '20'), 
    ('25', '25'),
    ('30', '30'))

COUNT_CHOICES = (
    ('1', '1'), 
    ('2', '2'), 
    ('3', '3'), 
    ('4', '4'),
    ('5', '5'))

STATUS_CHOICES = (
    ('Обрабатывается', 'Обрабатывается'), 
    ('На сборке', 'На сборке'), 
    ('В пути', 'В пути'), 
    ('Готов к выдаче', 'Готов к выдаче'), 
    ('Выполнен', 'Выполнен'), 
    ('Отменен', 'Отменен'))

STATUSREV_CHOICES = (
    ('Обрабатывается', 'Обрабатывается'), 
    ('Опубликован', 'Опубликован'), 
    ('Отказ в публикации', 'Отказ в публикации'))

CITIES_CHOICES = (
    ('Апрелевка', 'Апрелевка'),
    ('Балашиха', 'Балашиха'),
    ('Бронницы', 'Бронницы'),
    ('Верея', 'Верея'),
    ('Видное', 'Видное'),
    ('Волоколамск', 'Волоколамск'),
    ('Воскресенск', 'Воскресенск'),
    ('Высоковск', 'Высоковск'),
    ('Голицыно', 'Голицыно'),
    ('Дзержинский', 'Дзержинский'),
    ('Дмитров', 'Дмитров'),
    ('Долгопрудный', 'Долгопрудный'),
    ('Домодедово', 'Домодедово'),
    ('Дрезна', 'Дрезна'),
    ('Дубна', 'Дубна'),
    ('Егорьевск', 'Егорьевск'),
    ('Жуковский', 'Жуковский'),
    ('Зарайск', 'Зарайск'),
    ('Звенигород', 'Звенигород'),
    ('Ивантеевка', 'Ивантеевка'),
    ('Истра', 'Истра'),
    ('Кашира', 'Кашира'),
    ('Климовск', 'Климовск'),
    ('Клин', 'Клин'),
    ('Коломна', 'Коломна'),
    ('Королев', 'Королев'),
    ('Котельники', 'Котельники'),
    ('Красноармейск', 'Красноармейск'),
    ('Красногорск', 'Красногорск'),
    ('Краснозаводск', 'Краснозаводск'),
    ('Краснознаменск', 'Краснознаменск'),
    ('Кубинка', 'Кубинка'),
    ('Куровское', 'Куровское'),
    ('Ликино-Дулево', 'Ликино-Дулево'),
    ('Лобня', 'Лобня'),
    ('Лосино-Петровский', 'Лосино-Петровский'),
    ('Луховицы', 'Луховицы'),
    ('Лыткарино', 'Лыткарино'),
    ('Можайск', 'Можайск'),
    ('Москва', 'Москва'),
    ('Мытищи', 'Мытищи'),
    ('Наро-Фоминск', 'Наро-Фоминск'),
    ('Ногинск', 'Ногинск'),
    ('Одинцово', 'Одинцово'),
    ('Ожерелье', 'Ожерелье'),
    ('Орехово-Зуево', 'Орехово-Зуево'),
    ('Павловский Посад', 'Павловский Посад'),
    ('Пересвет', 'Пересвет'),
    ('Подольск', 'Подольск'),
    ('Протвино', 'Протвино'),
    ('Пушкино', 'Пушкино'),
    ('Пущино', 'Пущино'),
    ('Раменское', 'Раменское'),
    ('Реутов', 'Реутов'),
    ('Рошаль', 'Рошаль'),
    ('Руза', 'Руза'),
    ('Сергиев Посад', 'Сергиев Посад'),
    ('Серпухов', 'Серпухов'),
    ('Солнечногорск', 'Солнечногорск'),
    ('Старая Купавна', 'Старая Купавна'),
    ('Ступино', 'Ступино'),
    ('Талдом', 'Талдом'),
    ('Фрязино', 'Фрязино'),
    ('Химки', 'Химки'),
    ('Хотьково', 'Хотьково'),
    ('Черноголовка', 'Черноголовка'),
    ('Чехов', 'Чехов'),
    ('Шатура', 'Шатура'),
    ('Шаховская', 'Шаховская'),
    ('Щелково', 'Щелково'),
    ('Щербинка', 'Щербинка'),
    ('Электрогорск', 'Электрогорск'),
    ('Электросталь', 'Электросталь'),
    ('Электроугли', 'Электроугли'),
    ('Юбилейный', 'Юбилейный'),
    ('Яхрома', 'Яхрома'))

WRIT_CHOICES = (
    ('Главный автор', 'Главный автор'),
    ('Соавтор', 'Соавтор'),
    ('Помощник', 'Помощник'))

ERROR_TYPES_CHOICES =(
    ('Проблема с заказом', 'Проблема с заказом'),
    ('Проблема с отзывом', 'Проблема с отзывом'),
    ('Ошибка в личных данных', 'Ошибка в личных данных'),
    ('Ошибка в информации на сайте', 'Ошибка в информации на сайте'),
    ('Другое', 'Другое'))

STATUSFEED_CHOICES = (
    ('Новый', 'Новый'), 
    ('Обработан', 'Обработан'))

class Feedback(models.Model):
    type = models.CharField(choices=ERROR_TYPES_CHOICES, verbose_name="Тип ошибки", null=False, blank=False) 
    message = models.TextField(verbose_name="Сообщение")
    email = models.EmailField(null=False, blank=False,verbose_name="Email пользователя")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания заявки")
    status_feed = models.CharField(choices=STATUSFEED_CHOICES, verbose_name="Статус заявки", default="Новый", null=False, blank=False) 
    def __str__(self):
        return f"{self.get_type_display()} — {self.email}"
    class Meta:
        verbose_name = "заявка" #надпись сверху страницы таблицы
        verbose_name_plural = "Обратная связь" #переименовали таблицы на русский


class Writer(models.Model):
    nickname = models.CharField(max_length=60, verbose_name="Псевдоним", null=False, blank=False)
    photo_writ = models.TextField(verbose_name="Фото", default='https://vmulebki.gosuslugi.ru/netcat_files/9/148/1.jpg', blank=False)
    biography = models.TextField(verbose_name="Биография", null=True, blank=True)

    class Meta:
        verbose_name = "запись о писателе" #надпись сверху страницы таблицы
        verbose_name_plural = "Писатели" #переименовали таблицы на русский

    def __str__(self):
        return self.nickname

class PublishingHouse (models.Model):
    id_writers = models.ManyToManyField(Writer, verbose_name="id_wr", blank=False)
    name_publish = models.CharField(max_length=50, verbose_name="Название",null=False, blank=False)
    photo_publish = models.TextField(verbose_name="Фото",null=True, blank=True)
    publish_description = models.TextField(verbose_name="Описание",null=True, blank=True)

    class Meta:
        verbose_name = "запись об издательстве"
        verbose_name_plural = "Издательства"

    def __str__(self):
        return self.name_publish

class BookWriter(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE, verbose_name="Книга")
    writer = models.ForeignKey('Writer', on_delete=models.CASCADE, verbose_name="Автор")
    role = models.CharField(choices=WRIT_CHOICES, verbose_name="Роль", null=False, blank=False)  # Например: "Главный автор", "Соавтор"

    class Meta:
        verbose_name = "запись о роли автора в книге"
        verbose_name_plural = "Роли авторов в книгах"

    def __str__(self):
        return f"{self.writer.nickname} - {self.book.title} ({self.role})"


from simple_history.models import HistoricalRecords

class Book(models.Model):
    isbn = models.CharField(max_length=17,verbose_name="ISBN",null=False, blank=False)
    title = models.CharField(max_length=50, verbose_name="Название",null=False, blank=False)
    id_writer = models.ManyToManyField(
        Writer,
        through='BookWriter',  # Указываем промежуточную модель
        verbose_name="id_wr",
        blank=False
    )
    photo = models.TextField(verbose_name="Фото",null=False, blank=False)
    genre = models.CharField(max_length=30, choices=GENRE_CHOICES,verbose_name="Жанр", null=False, blank=False)
    id_publish = models.ForeignKey(PublishingHouse, on_delete=models.CASCADE, verbose_name="id_pb", null=False, blank=False)
    num_page = models.SmallIntegerField(verbose_name="Страницы",null=True, blank=True)
    year = models.DateTimeField(verbose_name="Год выпуска",null=True, blank=True)  
    discount = models.PositiveSmallIntegerField(verbose_name="Цена", null=False, blank=False)
    sale = models.CharField(max_length=3, choices=SALE_CHOICES, verbose_name="Скидка", null=True, blank=False)
    description = models.TextField(verbose_name="Описание", null=False, blank=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "книгу"
        verbose_name_plural = "Книги"

        #собст. функц. метод
    
    def get_avg_rating(self):
        avg = self.review.filter(status_rev='Опубликован').annotate(
            rating_as_float=Cast('rating', output_field=FloatField())
        ).aggregate(avg_rating=Avg('rating_as_float'))
        return round(avg['avg_rating'], 1) if avg['avg_rating'] else 0
    
    
    
    def get_published_reviews(self):
        return self.review.filter(status_rev='Опубликован')
    
    def get_articles(self):
        return Article.objects.filter(id_book=self)
    
    def __str__(self):
        return self.title

class Account(models.Model):                              
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Номер телефона", null=False, blank=False)     #вход по телефону в username
    surname = models.CharField(max_length=30, verbose_name="Фамилия",null=True, blank=True)
    name = models.CharField(max_length=30, verbose_name="Имя",null=True, blank=True)
    birthday = models.DateField(null=True, blank=True, verbose_name="День рождения")
    photo_acc = models.ImageField(
        upload_to='profile_photos/',  # Путь для сохранения фотографий
        null=True,                   # Поле может быть пустым
        blank=True,                  # Поле необязательно для заполнения
        verbose_name="Фото профиля"
    )

    class Meta:
        verbose_name = "профиль пользователя"
        verbose_name_plural = "Аккаунты"
    
    def __str__(self): #над редактированием записи выводится надпись поясняющая
        return f"Пользователь {self.surname} {self.name}"


class Article(models.Model):                                        #можно mtm, но не буду
    title_article = models.CharField(max_length=100, verbose_name="Название", null=False, blank=False)
    id_book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="id_bk", null=False, blank=False)
    photo_article = models.TextField(verbose_name="Фото",null=True, blank=True)
    text_article = models.TextField(verbose_name="Содержание", null=False, blank=False)
    
    class Meta:
        verbose_name = "статью"
        verbose_name_plural = "Статьи"
        
    def __str__(self):
        return self.title_article

class Shop(models.Model): 
    city = models.CharField(max_length=20, choices=CITIES_CHOICES, verbose_name="Город", null=False, blank=False)   
    street = models.TextField(verbose_name="Адрес", null=False, blank=False)
    transport = models.TextField(verbose_name="Траспорт",null=True, blank=True)
    google_maps_url = models.URLField(
        verbose_name="Ссылка на Google Maps",
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "запись о магазине"
        verbose_name_plural = "Магазины"

    def __str__(self):
        return self.street

class ShoppingCart(models.Model):   #расчет цены на прям сайте 
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="id_us", null=False, blank=False)
    id_book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="id_bk", null=False, blank=False)
    count_cart = models.CharField(max_length=2, choices=COUNT_CHOICES, verbose_name="Количество",null=False, blank=False)
        
    class Meta:
        verbose_name = "товар в корзине"
        verbose_name_plural = "Корзина"
    
    def __str__(self):
        return f"{self.id_book.title} — {self.count_cart} шт."
    
class Favourite(models.Model):    
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="id_us",null=False, blank=False)
    id_book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="id_bk",null=False, blank=False)
        
    class Meta:
        verbose_name = "запись об избранном товаре"
        verbose_name_plural = "Избранное"

    def __str__(self):
        return self.id_book.title 

class Order(models.Model):   #ДОП УСЛОВИЕ ДЛЯ АДМИНКИ: СТАТУС ЗАКАЗА НЕ МОЖЕТ БЫТЬ НА СБОРКЕ, ПОКА СУММА ЗАКАЗА = 0        это валидация)))))
    date_ord = models.DateField(auto_now_add=True,verbose_name="Дата заказа", null=False, blank=False)    
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="id_us",null=False, blank=False)
    id_shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name="id_sp",null=False, blank=False)
    status_ord = models.CharField(max_length=15, choices=STATUS_CHOICES, verbose_name="Статус",null=False, blank=False)
    price = models.PositiveSmallIntegerField(default=0, verbose_name="Сумма заказа",null=True, blank=True)
    receipt = models.FileField(
        upload_to='receipts/',  # Путь для сохранения файлов
        null=True,              # Поле может быть пустым
        blank=True,             # Поле необязательно для заполнения
        verbose_name="Чек"
    )
    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-date_ord']  # Сортировка по дате создания (новые сверху)

    def save(self, *args, **kwargs):
        # Если объект только создаётся (нет ID), установим статус по умолчанию
        if not self.pk and not self.status_ord:
            self.status_ord = 'Обрабатывается'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}"
    

class OrderItem(models.Model): 
    no_ord = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Номер заказа (id)", related_name='items',null=False, blank=False) #можно делать вызов кодом всех элементов order.orderitem.all() все позиции с номером заказа
    id_book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="id_bk", related_name='orderitem',null=False, blank=False) #можно делать вызов кодом всех элементов books.orderitem.all() все позиции с конкретной книгой 
    count_ord = models.CharField(max_length=2, choices=COUNT_CHOICES, verbose_name="Количество",null=False, blank=False)
     
    class Meta:
        verbose_name = "запись о купленном товаре"
        verbose_name_plural = "Позиции заказов"

    def __str__(self):
        return f"{self.no_ord}"

#      !!!!! НЕ РАБОТАЕТ!!!!!!

# class ReviewManager(models.Manager):  #СОБСТВЕННЫЙ МОДАЛЬНЫЙ МЕНЕДЖЕР
#     def get_queryset(self):
#         # Сначала выбираем неопубликованные отзывы, отсортированные по дате создания (старые выше)
#         unpublished = super().get_queryset().filter(status_rev='Обрабатывается').order_by('created_at')
        
#         # Затем выбираем опубликованные отзывы, отсортированные по дате создания (новые выше)
#         published = super().get_queryset().filter(status_rev='Опубликован').order_by('-created_at')

#         #Отклоненные отзывы (в конце, старые сверху)
#         rejected = super().get_queryset().filter(status_rev='Отказ в публикации').order_by('-created_at')
        
#         # Объединяем QuerySet'ы: сначала неопубликованные, затем опубликованные, потом отклоненные
#         return unpublished.union(published, rejected, all=True)
# from itertools import chain

# class ReviewManager(models.Manager):
#     def get_queryset(self):
#         unpublished = super().get_queryset().filter(status_rev='Обрабатывается').order_by('created_at')
#         published = super().get_queryset().filter(status_rev='Опубликован').order_by('-created_at')
#         rejected = super().get_queryset().filter(status_rev='Отказ в публикации').order_by('created_at')
#         return chain(unpublished, published, rejected)

# class ReviewManager(models.Manager):
#     def get_queryset(self):
#         # Получаем все отзывы
#         queryset = super().get_queryset()

#         # Группа 1: Отзывы в статусе "Обрабатывается" (старые сверху)
#         processing = queryset.filter(status_rev='Обрабатывается').order_by('created_at')

#         # Группа 2: Остальные отзывы (например, опубликованные и отклоненные) (новые сверху)
#         others = queryset.exclude(status_rev='Обрабатывается').order_by('-created_at')

#         # Объединяем QuerySet'ы: сначала "Обрабатывается", затем остальные
#         return list(processing) + list(others)

from .managers import ReviewManager
class Review(models.Model):
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="id_us", related_name='review',null=False, blank=False) #можно делать вызов кодом всех элементов users.review.all() все отзывы конкретного пользователя
    id_book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="id_bk", related_name='review',null=False, blank=False) #можно делать вызов кодом всех элементов book.review.all() все отзывы на конкретную книгу
    text_review = models.TextField(verbose_name="Текст отзыва",null=False, blank=False)
    rating = models.CharField(max_length=2, choices=COUNT_CHOICES, verbose_name="Рейтинг",null=False, blank=False)
    status_rev = models.CharField(max_length=20, choices=STATUSREV_CHOICES, verbose_name="Статус",null=False, blank=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Время создания отзыва",null=False, blank=False)  #записывает дату создания отзыва

    # objects = ReviewManager()
    objects = models.Manager()  # стандартный менеджер
    custom_order = ReviewManager()  # наш новый менеджер
    
    def save(self, *args, **kwargs):
        # Если объект только создаётся (нет ID), установим статус по умолчанию
        if not self.pk and not self.status_rev:
            self.status_rev = 'Обрабатывается'
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = "отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']  # сортировка по дате создания (новые сверху), 

    def __str__(self):
        return f"Отзыв от пользователя {self.id_user}"

