"""Код для воспроизведения сайта проекта"""
import os
from io import BytesIO
from django.conf import settings
from django.db.models import Avg, Case, When, IntegerField
from django.db.models.functions import Cast

from .forms import AccountForm, ReviewForm
from .models import Book, Article, PublishingHouse
from .models import ShoppingCart, Favourite, Shop, Order, Review, Account, OrderItem
from django.contrib.auth.models import User

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import logout

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from django.db import models
from django.db import transaction
from .models import COUNT_CHOICES


def index(request):
    """ Функция вывода главной страницы для неавторизованного пользователя"""
    new_books = Book.objects.filter(year__year=2025
    ).prefetch_related('id_writer')[:4]

    latest_articles = Article.objects.all().order_by('-id')[:3]

    #Расчет цены со скидкой для всех книг
    def calculate_discounted_price(books):
        for book in books:
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount-(book.discount*discount_percentage/100))
            else:
                book.discounted_price = book.discount

    calculate_discounted_price(new_books)
    genres = Book.objects.values_list('genre', flat=True).distinct()

    return render(request, 'index.html', {
        'new_books': new_books,
        'genres': genres,  
        'articles': latest_articles
    })


def vhod(request):
    """Функция для страницы авторизации"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        #Проверяем, существует ли пользователь с таким username
        try:
            user = User.objects.get(username=phone)
        except User.DoesNotExist:
            messages.error(request, "Аккаунта с таким номером телефона не существует.")
            return redirect('vhod')

        #Проверяем пароль
        auth_user = authenticate(username=user.username, password=password)
        if auth_user is not None:
            login(request, auth_user)
            if auth_user.is_staff:
                return redirect('moderator_dashboard')
            else:
                return redirect('avtoriz')
        else:
            messages.error(request, "Неправильный пароль.")
            return redirect('vhod')

    return render(request, 'vhod.html')


def regist(request):
    """Функция для страницы регистрации"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Пароли не совпадают.")
            return redirect('regist')

        if User.objects.filter(username=phone).exists():
            messages.error(request, "Пользователь с таким номером телефона уже существует.")
            return redirect('regist')

        #Создаем нового пользователя
        user = User.objects.create_user(username=phone, password=password)
        user.save()
        messages.success(request, "Аккаунт успешно создан. Теперь вы можете войти.")
        return redirect('vhod')

    return render(request, 'regist.html')


def moderator_dashboard(request):
    """ Функция вывода главной страницы для модератора"""
    if not request.user.is_authenticated:
        return redirect('vhod')

    if not request.user.is_staff:
        messages.error(request, "Доступ запрещён")
        return redirect('vhod')

    new_books = Book.objects.filter(year__year=2025).prefetch_related('id_writer')[:4]
    # new_orders = Book.objects.exclude(year__year=2025)  исключит книги 2025
    latest_articles = Article.objects.all().order_by('-id')[:3]

    def calculate_discounted_price(books):
        for book in books:
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount-(book.discount*discount_percentage/100))
            else:
                book.discounted_price = book.discount

    calculate_discounted_price(new_books)
    genres = Book.objects.values_list('genre', flat=True).distinct()

    return render(request, 'moderator_dashboard.html', {
        'new_books': new_books,
        'genres': genres,
        'articles': latest_articles
    })


def moderator_panel(request):
    """ Функция вывода страницы модератора"""
    if not request.user.is_staff:
        messages.error(request, "Доступ запрещён")
        return redirect('vhod')

    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    reviews_list = Review.objects.all().order_by('-id')

    if status_filter:
        reviews_list = reviews_list.filter(status_rev=status_filter)

    if query:
        reviews_list = reviews_list.filter(
            Q(id_book__title__icontains=query) |
            Q(id_user__username__icontains=query) |
            Q(id_user__account__name__icontains=query) |
            Q(id_user__account__surname__icontains=query)
        ).distinct()

    paginator = Paginator(reviews_list, 5)
    page_number = request.GET.get('page')
    reviews = paginator.get_page(page_number)
    genres = Book.objects.values_list('genre', flat=True).distinct()
    users = User.objects.all()
    books = Book.objects.all()

    return render(request, 'panel.html', {
        'reviews': reviews,
        'genres': genres,
        'users': users,
        'books': books,
        'query': query,
        'status_filter': status_filter,
        'COUNT_CHOICES': COUNT_CHOICES,
    })


def delete_review_mod(request, review_id):
    """ Функция вывода для удаления отзывов модератором"""
    review = get_object_or_404(Review, id=review_id)

    if not request.user.is_staff:
        messages.error(request, "Только модератор может удалять отзывы")
        return redirect('vhod')

    review.delete()
    messages.success(request, "Отзыв удален")
    return redirect('moderator_panel')


def get_books_for_moderator(request):
    """ Функция вывода книг для создания отзыва модератором"""
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'books': []})

    books = Book.objects.filter(
        orderitem__id_order__id_user=user_id,
        orderitem__id_order__status_ord='Выполнен'
    ).exclude(review__id_user=user_id).distinct()

    data = [{'id': b.id, 'title': b.title} for b in books]
    return JsonResponse({'books': data})


def get_users_for_moderator(request):
    """ Функция вывода пользователей для создания отзыва модератором"""
    book_id = request.GET.get('book_id')
    if not book_id:
        return JsonResponse({'users': []})

    users = User.objects.filter(
        order__items__id_book=book_id,
        order__status_ord='Выполнен'
    ).exclude(review__id_book=book_id).distinct()

    data = [{
        'id': u.id,
        'username': u.username,
        'name': u.account.name or '',
        'surname': u.account.surname or ''
    } for u in users]
    return JsonResponse({'users': data})


def create_review_mod(request):
    """ Функция создания отзыва модератором"""
    if not request.user.is_staff:
        return redirect('vhod')

    if request.method == 'POST':
        user_id = request.POST.get('user')
        book_id = request.POST.get('book')
        text_review = request.POST.get('text_review')
        rating = request.POST.get('rating')

        try:
            user = User.objects.get(id=user_id)
            book = Book.objects.get(id=book_id)
        except (User.DoesNotExist, Book.DoesNotExist):
            messages.error(request, "Неверный пользователь или книга")
            return redirect('moderator_panel')

        has_order = OrderItem.objects.filter(
            no_ord__id_user=user,
            no_ord__status_ord='Выполнен',
            id_book=book
        ).exists()

        already_reviewed = Review.objects.filter(
            id_user=user,
            id_book=book
        ).exists()

        if not has_order:
            messages.error(request, "Пользователь не покупал эту книгу")
            return redirect('moderator_panel')

        if already_reviewed:
            messages.warning(request, "Отзыв уже существует")
            return redirect('moderator_panel')

        Review.objects.create(
            id_user=user,
            id_book=book,
            text_review=text_review,
            rating=rating,
            status_rev='Опубликован'
        )

        messages.success(request, "Отзыв добавлен успешно")

    return redirect('moderator_panel')


def publish_review(request, review_id):
    """ Функция для публикации отзыва модератором"""
    if not request.user.is_staff:
        return redirect('vhod')

    review = get_object_or_404(Review, id=review_id)
    review.status_rev = 'Опубликован'
    review.save()

    return redirect('moderator_panel')


def reject_review(request, review_id):
    """ Функция для отказа в публикации отзыва модератором"""
    if not request.user.is_staff:
        return redirect('vhod')

    review = get_object_or_404(Review, id=review_id)
    review.status_rev = 'Отказ в публикации'
    review.save()

    return redirect('moderator_panel')


def revert_review(request, review_id):
    """ Функция для возвращения отзыва в статус обработки модератором"""
    if not request.user.is_staff:
        return redirect('vhod')

    review = get_object_or_404(Review, id=review_id)

    if review.status_rev in ['Опубликован', 'Отказ в публикации']:
        review.status_rev = 'Обрабатывается'
        review.save()
        messages.success(request, "Отзыв отправлен обратно на модерацию")
    else:
        messages.warning(request, "Невозможно вернуть в обработку")

    return redirect('moderator_panel')


# @cache_page(60 * 15)  # кэш на 15 минут
def avtoriz(request):
    """ Функция вывода главной страницы для авторизованного пользователя"""
    recommended_books = Book.objects.filter(genre="Фэнтези").prefetch_related('id_writer')[:4]
    new_books = Book.objects.filter(year__year=2025).prefetch_related('id_writer')[:4]
    latest_articles = Article.objects.all().order_by('-id')[:3]
    viewed_book_ids = request.session.get('viewed_books', [])

    viewed_books = []
    if viewed_book_ids:
        viewed_books = Book.objects.filter(id__in=viewed_book_ids).order_by(Case(*[When(id=id, then=pos) for pos, id in enumerate(viewed_book_ids)],output_field=models.IntegerField()))

    def calculate_discounted_price(books):
        for book in books:
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount-(book.discount*discount_percentage/100))
            else:
                book.discounted_price = book.discount

    calculate_discounted_price(recommended_books)
    calculate_discounted_price(new_books)
    calculate_discounted_price(viewed_books)
    genres = Book.objects.values_list('genre', flat=True).distinct()

    fav_user = []
    cart_books_ids = []
    cart_count = 0

    if request.user.is_authenticated:
        fav_user = list(Favourite.objects.filter(id_user=request.user).values_list('id_book__id', flat=True))
        cart_books_ids = list(
            ShoppingCart.objects.filter(id_user=request.user).values_list('id_book__id', flat=True)
        )
        cart_count = ShoppingCart.objects.filter(id_user=request.user).count()

    return render(request, 'avtoriz.html', {
        'recommended_books': recommended_books,
        'new_books': new_books,
        'articles': latest_articles,
        'genres': genres,
        'user_fav_books': fav_user,
        'cart_books_ids': cart_books_ids,
        'cart_count': cart_count,
        'viewed_books': viewed_books,
        'show_viewed_section': len(viewed_book_ids) > 0
    })


def journal(request):
    """ Функция вывода статей для неавторизованного пользователя"""
    query = request.GET.get('q', '')

    if query:
        articles = Article.objects.filter(
            Q(title_article__icontains=query) | Q(text_article__icontains=query)
        )
    else:
        articles = Article.objects.all()

    genres = Book.objects.values_list('genre', flat=True).distinct()

    return render(request, 'journal.html', {
        'articles': articles,
        'genres': genres,  # Передаем жанры в шаблон
        'query': query,
    })


def catalog(request, genre=None):
    """ Функция вывода каталога для неавторизованного пользователя"""
    query = request.GET.get('q', '')
    selected_publishers = request.GET.getlist('publisher')
    price_range = request.GET.get('price_range', '')
    exclude_no_rating = request.GET.get('exclude_no_rating', '')
    books = Book.objects.all()

    if exclude_no_rating:
        books = books.annotate(
            avg_rating=Avg(
                Cast('review__rating', output_field=IntegerField()),
                filter=Q(review__status_rev='Опубликован')
            )
        ).filter(~Q(avg_rating__isnull=True))

    if genre:
        books = books.filter(genre=genre)

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(id_writer__nickname__icontains=query)
        ).distinct()

    if selected_publishers:
        books = books.filter(id_publish_id__in=selected_publishers)

    if price_range:
        if price_range == '0-500':
            books = books.extra(
                where= ["CAST((discount * (100-CAST(sale AS INTEGER))/100) AS DECIMAL(10,2)) < 500"]
            )
        elif price_range == '500-1000':
            books = books.extra(
                where=[
                    "CAST((discount * (100 - CAST(sale AS INTEGER))/100) AS DECIMAL(10,2)) >= 500",
                    "CAST((discount * (100 - CAST(sale AS INTEGER))/100) AS DECIMAL(10,2)) <= 1000"
                ]
            )
        elif price_range == '1000-2000':
            books = books.extra(
                where=[
                    "CAST((discount * (100 - CAST(sale AS INTEGER))/100) AS DECIMAL(10,2)) >= 1000",
                    "CAST((discount * (100 - CAST(sale AS INTEGER)) 100) AS DECIMAL(10,2)) <= 2000"
                ]
            )
        elif price_range == '2000+':
            books = books.extra(
                where=["CAST((discount * (100-CAST(sale AS INTEGER))/100) AS DECIMAL(10,2)) > 2000"]
            )

    paginator = Paginator(books, 3)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    for book in page_obj:
        if not hasattr(book, 'discounted_price'):
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount-(book.discount*discount_percentage/100))
            else:
                book.discounted_price = book.discount

    all_publishers = PublishingHouse.objects.all()
    genres = Book.objects.values_list('genre', flat=True).distinct()

    return render(request, 'catalog.html', {
        'page_obj': page_obj,
        'genres': genres,
        'query': query,
        'current_genre': genre,
        'publishers': all_publishers,
        'selected_publishers': selected_publishers,
        'price_range': price_range,
        'exclude_no_rating': exclude_no_rating,
    })


def publishers_list(request):
    """ Функция вывода издательств для неавторизованного пользователя"""
    publishers = PublishingHouse.objects.all()

    def calculate_discounted_price(books_list):
        for book in books_list:
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount-(book.discount*discount_percentage/100))
            else:
                book.discounted_price = book.discount

    publishers_with_books = []
    genres = Book.objects.values_list('genre', flat=True).distinct()
    for publisher in publishers:
        best_books = list(Book.objects.filter(id_publish=publisher).order_by('-year')[:3])

        calculate_discounted_price(best_books)
        publishers_with_books.append({
            'publisher': publisher,
            'best_books': best_books,
        })

    return render(request, 'publishers.html', {
        'publishers_with_books': publishers_with_books,
        'genres': genres
    })


def journal2(request):
    """ Функция вывода статей для авторизованного пользователя"""
    query = request.GET.get('q', '')

    if query:
        articles = Article.objects.filter(
            Q(title_article__icontains=query) | Q(text_article__icontains=query)
        )
    else:
        articles = Article.objects.all()

    genres = Book.objects.values_list('genre', flat=True).distinct()
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = ShoppingCart.objects.filter(id_user=request.user).count()

    return render(request, 'journal2.html', {
        'articles': articles,
        'genres': genres,  
        'query': query,
        'cart_count': cart_count
    })


def catalog2(request, genre=None):
    """ Функция вывода каталога для авторизованного пользователя"""
    query = request.GET.get('q', '')
    selected_publishers = request.GET.getlist('publisher')
    price_range = request.GET.get('price_range', '')
    exclude_no_rating = request.GET.get('exclude_no_rating', '')
    books = Book.objects.all()

    if exclude_no_rating:
        books = books.annotate(
            avg_rating=Avg(
                Cast('review__rating', output_field=IntegerField()),
                filter=Q(review__status_rev='Опубликован')
            )
        ).filter(~Q(avg_rating__isnull=True))

    if genre:
        books = books.filter(genre=genre)

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(id_writer__nickname__icontains=query)
        ).distinct()

    if selected_publishers:
        books = books.filter(id_publish_id__in=selected_publishers)

    if price_range:
        if price_range == '0-500':
            books = books.extra(
                where= ["CAST((discount * (100-CAST(sale AS INTEGER))/100) AS DECIMAL(10,2)) < 500"]
            )
        elif price_range == '500-1000':
            books = books.extra(
                where=[
                    "CAST((discount * (100 - CAST(sale AS INTEGER))/100) AS DECIMAL(10,2)) >= 500",
                    "CAST((discount * (100 - CAST(sale AS INTEGER))/100) AS DECIMAL(10,2)) <= 1000"
                ]
            )
        elif price_range == '1000-2000':
            books = books.extra(
                where=[
                    "CAST((discount * (100 - CAST(sale AS INTEGER))/100) AS DECIMAL(10,2)) >= 1000",
                    "CAST((discount * (100 - CAST(sale AS INTEGER))/100) AS DECIMAL(10,2)) <= 2000"
                ]
            )
        elif price_range == '2000+':
            books = books.extra(
                where=["CAST((discount * (100-CAST(sale AS INTEGER))/100) AS DECIMAL(10,2)) > 2000"]
            )

    paginator = Paginator(books, 3)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    for book in page_obj:
        if not hasattr(book, 'discounted_price'):
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount-(book.discount*discount_percentage/100))
            else:
                book.discounted_price = book.discount

    all_publishers = PublishingHouse.objects.all()
    genres = Book.objects.values_list('genre', flat=True).distinct()
    cart_books_ids = []
    fav_user = []
    cart_count = 0
    if request.user.is_authenticated:
        fav_user = list(
            Favourite.objects.filter(id_user=request.user).values_list('id_book__id', flat=True)
        )
        cart_count = ShoppingCart.objects.filter(id_user=request.user).count()
        cart_books_ids = list(
            ShoppingCart.objects.filter(id_user=request.user).values_list('id_book__id', flat=True)
        )
    else:
        fav_user = []

    return render(request, 'catalog2.html', {
        'page_obj': page_obj,
        'genres': genres,
        'query': query,
        'current_genre': genre,
        'user_fav_books': fav_user,
        'cart_books_ids': cart_books_ids,
        'cart_count': cart_count,
        'publishers': all_publishers,
        'selected_publishers': selected_publishers,
        'price_range': price_range,
        'exclude_no_rating': exclude_no_rating,
    })


def publishers_list2(request):
    """ Функция вывода издательств для авторизованного пользователя"""
    publishers = PublishingHouse.objects.all()

    def calculate_discounted_price(books_list):
        for book in books_list:
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount-(book.discount*discount_percentage/100))
            else:
                book.discounted_price = book.discount

    publishers_with_books = []
    genres = Book.objects.values_list('genre', flat=True).distinct()
    for publisher in publishers:
        best_books = list(Book.objects.filter(id_publish=publisher).order_by('-year')[:3])
        calculate_discounted_price(best_books)
        publishers_with_books.append({
            'publisher': publisher,
            'best_books': best_books,
        })

    fav_user = []
    cart_books_ids = []
    cart_count = 0
    if request.user.is_authenticated:
        fav_user = list(Favourite.objects.filter(id_user=request.user).values_list('id_book__id', flat=True))
        cart_count = ShoppingCart.objects.filter(id_user=request.user).count()
        cart_books_ids = list(
            ShoppingCart.objects.filter(id_user=request.user).values_list('id_book__id', flat=True)
        )
    else:
        fav_user = []

    return render(request, 'publishers2.html', {
        'publishers_with_books': publishers_with_books,
        'genres': genres,
        'user_fav_books': fav_user,
        'cart_books_ids': cart_books_ids,
        'cart_count': cart_count
    })


def shopcart(request):
    """ Функция вывода корзины"""
    cart_items = ShoppingCart.objects.filter(id_user=request.user).select_related('id_book')
    total_price = 0
    items_with_prices = []
    genres = Book.objects.values_list('genre', flat=True).distinct()

    for item in cart_items:
        book = item.id_book
        quantity = int(item.count_cart)

        if book.sale:
            discount_percentage = int(book.sale)
            discounted_price = round(book.discount * (1 - discount_percentage / 100))
        else:
            discounted_price = book.discount

        total_item_price = discounted_price * quantity
        items_with_prices.append({
            'item': item,
            'book': book,
            'quantity': quantity,
            'discounted_price': discounted_price,
            'total_item_price': total_item_price,
        })
        total_price += total_item_price

    shops = Shop.objects.all()
    for shop in shops:
        if ',' in shop.street:
            shop.street_short = shop.street.split(',', 1)[0]
        else:
            shop.street_short = shop.street
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = ShoppingCart.objects.filter(id_user=request.user).count()

    return render(request, 'shopcart.html', {
        'items_with_prices': items_with_prices,
        'total_price': total_price,
        'genres': genres,
        'shops': shops,
        'cart_count': cart_count  
    })

def cart_change_quantity(request, item_id, action):
    """ Функция изменения количества товаров в корзине"""
    cart_item = get_object_or_404(ShoppingCart, id=item_id, id_user=request.user)
    quantity = int(cart_item.count_cart)

    if action == 'increase':
        if quantity >= 5:
            messages.warning(request, "Нельзя добавить больше 5 шт.")
        else:
            quantity += 1
    elif action == 'decrease' and quantity > 1:
        quantity -= 1

    cart_item.count_cart = str(quantity)
    cart_item.save()

    return HttpResponseRedirect(reverse('shopcart'))


def remove_from_cart(request, item_id):
    """ Функция удаления товара из корзины на любой странице кроме корзины"""
    cart_item = get_object_or_404(ShoppingCart, id=item_id, id_user=request.user)
    cart_item.delete()
    return HttpResponseRedirect(reverse('shopcart'))

def add_to_cart(request, book_id):
    """ Функция добавления товара в корзину"""
    book = get_object_or_404(Book, id=book_id)

    if request.user.is_authenticated:
        cart_item, created = ShoppingCart.objects.get_or_create(
            id_user=request.user,
            id_book=book,
            defaults={'count_cart': '1'}
        )
        if not created:
        #Если книга уже есть в корзине — не увеличиваем количество
            pass

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def remove_from_cart_by_book_id(request, book_id):
    """ Функция удаления товара из корзины на странице корзины""" 
    if request.user.is_authenticated:
        ShoppingCart.objects.filter(id_user=request.user, id_book__id=book_id).delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def checkout(request):
    """ Функция оформления заказа в корзине""" 
    cart_items = ShoppingCart.objects.filter(id_user=request.user).select_related('id_book')

    if not cart_items.exists():
        messages.error(request, "В корзине нет товаров для оформления заказа")
        return redirect('shopcart')

    #Начинаем транзакцию
    with transaction.atomic():
        order = Order.objects.create(
            id_user=request.user,
            status_ord='Обрабатывается',
            id_shop_id=1)
        total_price = 0

        #Проходим по всем элементам корзины и создаём OrderItem
        for item in cart_items:
            book = item.id_book
            quantity = int(item.count_cart)

            if book.sale:
                discount_percentage = int(book.sale)
                discounted_price = round(book.discount * (1 - discount_percentage / 100))
            else:
                discounted_price = book.discount

            OrderItem.objects.create(
                no_ord=order,
                id_book=book,
                count_ord=item.count_cart
            )

            total_price += discounted_price * quantity

        order.price = total_price
        order.save()

        cart_items.delete()

    messages.success(request, "Заказ успешно оформлен")
    return redirect('shopcart')


def favourite(request):
    """ Функция вывода страницы избранное""" 
    fav_items = Favourite.objects.filter(id_user=request.user).select_related('id_book')

    def calculate_discounted_price(books):
        for book in books:
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount-(book.discount*discount_percentage/100))
            else:
                book.discounted_price = book.discount

    books = [item.id_book for item in fav_items]
    calculate_discounted_price(books)

    paginator = Paginator(fav_items, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    genres = Book.objects.values_list('genre', flat=True).distinct()
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = ShoppingCart.objects.filter(id_user=request.user).count()

    return render(request, 'favourite.html', {
        'page_obj': page_obj,
        'genres': genres,
        'cart_count': cart_count
    })


def remove_from_favourite(request, item_id):
    """ Функция удаления из избранного на странице избранного""" 
    if request.user.is_authenticated:
        fav_item = get_object_or_404(Favourite, id=item_id, id_user=request.user)
        fav_item.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def add_to_favourite(request, book_id):
    """ Функция добавления/удаления избранного товара с любой страницы кроме избранного""" 
    book = get_object_or_404(Book, id=book_id)

    if request.user.is_authenticated:
        fav_item = Favourite.objects.filter(id_user=request.user, id_book=book).first()
        if fav_item:
            fav_item.delete()
        else:
            Favourite.objects.create(id_user=request.user, id_book=book)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def lk(request):
    """ Функция вывода страницы заказы в личном кабинете""" 
    orders = Order.objects.filter(id_user=request.user).prefetch_related(
        'items__id_book__review', 
    ).order_by('-date_ord')
    try:
        account = Account.objects.get(user=request.user)
    except Account.DoesNotExist:
        account = None

    user_reviews_books = Review.objects.filter(id_user=request.user).values_list('id_book_id', flat=True)

    for order in orders:
        order_items = order.items.all()
        order.total_order_price = 0
        order.items_list = []

        for item in order_items:
            book = item.id_book

            if book.sale and book.sale.isdigit():
                discount_percentage = int(book.sale)
                final_price = round(book.discount * (1 - discount_percentage / 100))
            else:
                final_price = book.discount

            item.final_price = final_price
            item.total_price = final_price * int(item.count_ord)
            order.total_order_price += item.total_price
            item.has_review = book.review.filter(id_user=request.user).exists()
            order.items_list.append(item)

    genres = Book.objects.values_list('genre', flat=True).distinct()
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = ShoppingCart.objects.filter(id_user=request.user).count()

    review_form = ReviewForm()

    return render(request, 'lk.html', {
        'orders': orders,
        'account': account,
        'genres': genres,
        'cart_count': cart_count,
        'user_reviews_books': user_reviews_books,
        'form': review_form,
    })


def generate_receipt(request, order_id):
    """ Функция создания пдф файла чека""" 
    order = get_object_or_404(Order.objects.prefetch_related('items__id_book'), id=order_id)

    if order.id_user != request.user and not request.user.is_staff:
        return HttpResponse("Доступ запрещён", status=403)

    #Регистрация шрифтов
    FONTS_DIR = os.path.join(settings.BASE_DIR, 'fonts')

    try:
        pdfmetrics.getFont('DejaVuSans')
    except KeyError:
        font_path = os.path.join(FONTS_DIR, 'DejaVuSans.ttf')
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        else:
            raise FileNotFoundError(f"Файл шрифта не найден: {font_path}")

    try:
        pdfmetrics.getFont('DejaVuSans-Bold')
    except KeyError:
        bold_font_path = os.path.join(FONTS_DIR, 'DejaVuSans-Bold.ttf')
        if os.path.exists(bold_font_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_font_path))
        else:
            raise FileNotFoundError(f"Файл шрифта не найден: {bold_font_path}")

    #Генерация PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    styles['Title'].fontName = 'DejaVuSans-Bold'
    styles['Normal'].fontName = 'DejaVuSans'

    elements.append(Paragraph(f"Чек заказа #{order.id}", styles['Title']))
    elements.append(Spacer(1, 24))

    elements.append(Paragraph(f"Дата: {order.date_ord.strftime('%d.%m.%Y')}", styles['Normal']))
    elements.append(Paragraph(f"Номер покупателя: {request.user.username}", styles['Normal']))
    elements.append(Paragraph(f"Магазин: {order.id_shop.street}", styles['Normal']))
    elements.append(Spacer(1, 12))

    data = [['Книга', 'Автор(ы)', 'Цена', 'Кол-во', 'Сумма']]
    total_price = 0

    for item in order.items.all():
        book = item.id_book
        count = int(item.count_ord)

        if book.sale and book.sale.isdigit():
            price = round(book.discount * (1 - int(book.sale) / 100))
        else:
            price = book.discount

        total_item = price * count
        total_price += total_item

        authors = ", ".join(writer.nickname for writer in book.id_writer.all())
        data.append([book.title, authors, f"{price} ₽", str(count), f"{total_item} ₽"])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#34495e')),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 24))

    elements.append(Paragraph(f"<b>Общая сумма:</b> {total_price} ₽", styles['Normal']))

    doc.build(elements)
    pdf_value = buffer.getvalue()
    buffer.close()

    #Сохраняем в модель Order
    receipt_dir = os.path.join(settings.MEDIA_ROOT, 'receipts')
    os.makedirs(receipt_dir, exist_ok=True)

    receipt_path = os.path.join(receipt_dir, f'receipt_{order.id}.pdf')
    with open(receipt_path, 'wb') as f:
        f.write(pdf_value)

    order.receipt.name = f'receipts/receipt_{order.id}.pdf'
    order.save(update_fields=['receipt'])

    response = HttpResponse(pdf_value, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=receipt_{order.id}.pdf'

    return response


def add_review(request):
    """ Функция добавления отзыва на книгу пользователем """ 
    if request.method == "POST":
        book_id = request.POST.get('book_id')
        book = get_object_or_404(Book, id=book_id)
        existing_review = Review.objects.filter(id_book=book, id_user=request.user).exists()
        if existing_review:
            messages.warning(request, "Вы уже оставили отзыв на эту книгу.")
            return redirect('lk')

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.id_user = request.user
            review.id_book = book
            review.status_rev = 'Обрабатывается'
            review.save()
            messages.success(request, "Ваш отзыв успешно отправлен.")
            return redirect('lk')
        else:
            messages.error(request, "Ошибка при сохранении отзыва.")
    return redirect('lk')


def profile(request):
    """ Функция вывода страницы данных в личном кабинете""" 
    user = request.user
    try:
        account = Account.objects.get(user=user)
    except Account.DoesNotExist:
        account = None

    form = AccountForm(instance=account)
    genres = Book.objects.values_list('genre', flat=True).distinct()
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = ShoppingCart.objects.filter(id_user=request.user).count()

    return render(request, 'profile.html', {
        'account': account,
        'genres': genres,
        'cart_count': cart_count,
        'form': form
    })


def update_profile(request):
    """ Функция редактирования данных в личном кабинете""" 
    account  = Account.objects.get(user=request.user)

    if request.method == "POST":
        form = AccountForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = AccountForm(instance=account)

    return render(request, 'profile.html', {'form': form, 'account': account})


def reviews(request):
    """ Функция вывода страницы отзывы в личном кабинете""" 
    reviews = Review.objects.filter(id_user=request.user).select_related('id_book')
    genres = Book.objects.values_list('genre', flat=True).distinct()
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = ShoppingCart.objects.filter(id_user=request.user).count()

    return render(request, 'reviews.html', {
        'reviews': reviews,
        'genres': genres,
        'cart_count': cart_count
    })


def delete_review(request, review_id):
    """ Функция удаления отзыва в личном кабинете пользователем""" 
    review = get_object_or_404(Review, id=review_id, id_user=request.user)
    review.delete()
    return redirect('reviews')


def custom_logout(request):
    """ Функция выхода из аккаунта в личном кабинете пользователем""" 
    logout(request)
    return redirect('index')  # или 'index'


def book_detail(request, book_id):
    """ Функция выхода страницы книги для авторизованного пользователя""" 
    book = get_object_or_404(Book.objects.prefetch_related(
        'id_writer',
        'review__id_user__account'
    ), id=book_id)

    if book.sale and book.sale.isdigit():
        discount_percentage = int(book.sale)
        book.discounted_price = round(book.discount * (1 - discount_percentage / 100))
    else:
        book.discounted_price = book.discount

    reviews = book.review.filter(status_rev='Опубликован')
    articles = Article.objects.filter(id_book=book)
    in_cart = False
    in_favourite = False

    if request.user.is_authenticated:
        in_cart = ShoppingCart.objects.filter(id_user=request.user, id_book=book).exists()
        in_favourite = Favourite.objects.filter(id_user=request.user, id_book=book).exists()

    genres = Book.objects.values_list('genre', flat=True).distinct()
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = ShoppingCart.objects.filter(id_user=request.user).count()

    viewed_books = request.session.get('viewed_books', [])

    if book.id not in viewed_books:
        viewed_books.insert(0, book.id)
        viewed_books = viewed_books[:4]
        request.session['viewed_books'] = viewed_books

    return render(request, 'book_detail.html', {
        'book': book,
        'reviews': reviews,
        'articles': articles,
        'in_cart': in_cart,
        'in_favourite': in_favourite,
        'genres': genres,
        'cart_count': cart_count
    })


def book_detail2(request, book_id):
    """ Функция выхода страницы книги для неавторизованного пользователя""" 
    book = get_object_or_404(Book.objects.prefetch_related(
        'id_writer',
        'review__id_user__account'
    ), id=book_id)

    if book.sale and book.sale.isdigit():
        discount_percentage = int(book.sale)
        book.discounted_price = round(book.discount * (1 - discount_percentage / 100))
    else:
        book.discounted_price = book.discount

    reviews = book.review.filter(status_rev='Опубликован')
    articles = Article.objects.filter(id_book=book)
    genres = Book.objects.values_list('genre', flat=True).distinct()

    return render(request, 'book_detail2.html', {
        'book': book,
        'reviews': reviews,
        'articles': articles,
        'genres': genres,
    })


def article(request, article_id):
    """ Функция выхода страницы статьи для неавторизованного пользователя""" 
    article = get_object_or_404(Article.objects.select_related('id_book'), id=article_id)
    book = article.id_book
    writers = book.id_writer.all()

    if book.sale and book.sale.isdigit():
        discount_percentage = int(book.sale)
        discounted_price = round(book.discount * (1 - discount_percentage / 100))
    else:
        discounted_price = book.discount

    genres = Book.objects.values_list('genre', flat=True).distinct()

    return render(request, 'article.html', {
        'article': article,
        'book': book,
        'writers': writers,
        'discounted_price': discounted_price,
        'genres': genres,

    })

def article2(request, article_id):
    """ Функция выхода страницы статьи для авторизованного пользователя""" 
    article = get_object_or_404(Article.objects.select_related('id_book'), id=article_id)
    book = article.id_book
    writers = book.id_writer.all()

    if book.sale and book.sale.isdigit():
        discount_percentage = int(book.sale)
        discounted_price = round(book.discount * (1 - discount_percentage / 100))
    else:
        discounted_price = book.discount

    cart_books_ids = []
    cart_count = 0
    user_fav_books = []

    if request.user.is_authenticated:
        cart_books_ids = list(
            ShoppingCart.objects.filter(id_user=request.user).values_list('id_book__id', flat=True)
        )
        cart_count = ShoppingCart.objects.filter(id_user=request.user).count()
        user_fav_books = list(request.user.favourite_set.values_list('id_book__id', flat=True))
    genres = Book.objects.values_list('genre', flat=True).distinct()

    return render(request, 'article2.html', {
        'article': article,
        'book': book,
        'writers': writers,
        'discounted_price': discounted_price,
        'cart_count': cart_count,
        'cart_books_ids': cart_books_ids,
        'user_fav_books': user_fav_books,
        'genres': genres
    })


