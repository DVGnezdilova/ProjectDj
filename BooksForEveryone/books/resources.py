from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from books.models import Book, Writer, PublishingHouse
from django.db.models import Avg
from django.db.models.functions import Cast
from django.db.models import FloatField


class BookResource(resources.ModelResource):
    # 1. Автор(ы) книги через запятую
    writers = fields.Field(
        attribute='id_writer',
        column_name='Авторы',
        widget=ManyToManyWidget(Writer, field='nickname', separator=', ')
    )

    # 2. Средний рейтинг книги
    avg_rating = fields.Field(column_name='Средний рейтинг')

    def dehydrate_avg_rating(self, book):
        return round(book.get_avg_rating(), 1) if book.get_avg_rating() else 0

    # 3. Цена со скидкой
    discounted_price = fields.Field(column_name='Цена со скидкой')

    def dehydrate_discounted_price(self, book):
        if book.sale:
            discount_percentage = int(book.sale)
            return round(book.discount * (100 - discount_percentage) / 100, 2)
        return book.discount

    # 4. Название издательства
    publisher = fields.Field(column_name='Издательство')

    def dehydrate_publisher(self, book):
        return book.id_publish.name_publish if book.id_publish else ''

    # 5. Фильтруем только книги дешевле 1000 ₽
    def get_export_queryset(self, queryset):
        queryset = super().get_export_queryset(queryset)
        return queryset.filter(discount__lt=1000)

    class Meta:
        model = Book
        fields = (
            'title', 'writers', 'genre', 'publisher',
            'discount', 'sale', 'discounted_price', 'avg_rating'
        )
        export_order = (
            'title', 'writers', 'genre', 'publisher',
            'discount', 'sale', 'discounted_price', 'avg_rating'
        )