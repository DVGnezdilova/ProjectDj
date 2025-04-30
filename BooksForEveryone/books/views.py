from django.db.models import Avg
from django.shortcuts import render
from .models import Book


from django.shortcuts import render
from .models import Book

def index(request):
    # Фильтрация книг для "Персональных рекомендаций"
    recommended_books = Book.objects.filter(
        genre="Фэнтези"  # Книги жанра "Фантастика"
    ).prefetch_related('id_writer')

    # Фильтрация книг для "Новинок"
    new_books = Book.objects.filter(
        year__year=2025  # Книги, выпущенные в 2024 году
    ).prefetch_related('id_writer')

    # Расчет цены со скидкой для всех книг
    def calculate_discounted_price(books):
        for book in books:
            # Расчет цены со скидкой с округлением до целых чисел
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount - (book.discount * discount_percentage / 100))
            else:
                book.discounted_price = book.discount

    # Применяем расчет цены со скидкой к обоим наборам книг
    calculate_discounted_price(recommended_books)
    calculate_discounted_price(new_books)

    # Передаем данные в шаблон
    return render(request, 'index.html', {
        'recommended_books': recommended_books,
        'new_books': new_books
    })