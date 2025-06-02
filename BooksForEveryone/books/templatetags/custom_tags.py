from django import template
from books.models import Book, Review

register = template.Library()

@register.simple_tag
def total_reviews():
    return Review.objects.count()

from books.models import Order

@register.simple_tag(takes_context=True)
def user_orders_count(context):
    request = context['request']
    if request.user.is_authenticated:
        return Order.objects.filter(id_user=request.user).count()
    return 0

@register.simple_tag
def get_similar_books(book_id):
    # Получаем книгу
    current_book = Book.objects.get(id=book_id)
    return Book.objects.filter(genre=current_book.genre).exclude(id=current_book.id)[:3]