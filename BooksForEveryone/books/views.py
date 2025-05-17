import os
from django.conf import settings
from django.db.models import Avg
from django.forms import FloatField
from django.db.models.functions import Cast

from .forms import AccountForm
from .forms import ReviewForm
from .forms import ModeratorReviewForm
from .models import Book, Article, PublishingHouse, ShoppingCart, Favourite, Shop, Order, Review, Account, OrderItem
from django.contrib.auth.models import User

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import logout

from django.db import models


def index(request):
    # Фильтрация книг для "Новинок"
    new_books = Book.objects.filter(
        year__year=2025  # Книги, выпущенные в 2024 году
    ).prefetch_related('id_writer')[:4] 

    best_books = Book.objects.filter(review__status_rev='Опубликован').annotate(
        avg_rating=Avg(Cast('review__rating', output_field=models.FloatField()))
    ).order_by('-avg_rating')[:4]

    latest_articles = Article.objects.all().order_by('-id')[:3]


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
    calculate_discounted_price(new_books)
    calculate_discounted_price(best_books)

    # Получение уникальных жанров из базы данных
    genres = Book.objects.values_list('genre', flat=True).distinct()

    # Передаем данные в шаблон
    return render(request, 'index.html', {
        'new_books': new_books,
        'genres': genres,  # Добавляем жанры в контекст
        'best_books': best_books,
        'articles': latest_articles
    })

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import COUNT_CHOICES

def vhod(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        # Проверяем, существует ли пользователь с таким username
        try:
            user = User.objects.get(username=phone)
        except User.DoesNotExist:
            messages.error(request, "Аккаунта с таким номером телефона не существует. Рекомендуется зарегистрироваться.")
            return redirect('vhod')

        # Проверяем пароль
        auth_user = authenticate(username=user.username, password=password)
        if auth_user is not None:
            login(request, auth_user)
            if auth_user.is_staff:
                return redirect('moderator_dashboard')  # ← панель модератора
            else:
                return redirect('avtoriz')  # ← главная для обычных пользователей
        else:
            messages.error(request, "Неправильный пароль.")
            return redirect('vhod')

    return render(request, 'vhod.html')


def regist(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Проверяем, что пароли совпадают
        if password != confirm_password:
            messages.error(request, "Пароли не совпадают.")
            return redirect('regist')

        # Проверяем, существует ли уже пользователь с таким username
        if User.objects.filter(username=phone).exists():
            messages.error(request, "Пользователь с таким номером телефона уже существует.")
            return redirect('regist')

        # Создаем нового пользователя
        user = User.objects.create_user(username=phone, password=password)
        user.save()
        messages.success(request, "Аккаунт успешно создан. Теперь вы можете войти.")
        return redirect('vhod')

    return render(request, 'regist.html')

def moderator_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('vhod')
    
    if not request.user.is_staff:
        messages.error(request, "Доступ запрещён")
        return redirect('vhod')

    new_books = Book.objects.filter(year__year=2025).prefetch_related('id_writer')[:4]

    # Расчет цен со скидкой
    def calculate_discounted_price(books):
        for book in books:
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount - (book.discount * discount_percentage / 100))
            else:
                book.discounted_price = book.discount


    calculate_discounted_price(new_books)

    genres = Book.objects.values_list('genre', flat=True).distinct()

    return render(request, 'moderator_dashboard.html', {
        'new_books': new_books,
        'genres': genres,
    })

def moderator_panel(request):
    if not request.user.is_staff:
        messages.error(request, "Доступ запрещён")
        return redirect('vhod')

    query = request.GET.get('q')
    status_filter = request.GET.get('status')

    reviews_list = Review.objects.all().order_by('-created_at')

    if status_filter:
        reviews_list = reviews_list.filter(status_rev=status_filter)

    if query:
        reviews_list = reviews_list.filter(
            Q(id_book__title__icontains=query) |
            Q(id_user__username__icontains=query) |
            Q(id_user__account__name__icontains=query) |
            Q(id_user__account__surname__icontains=query)
        ).distinct()

    # Получаем всех пользователей и книги для формы
    users = User.objects.all()
    books = Book.objects.all()

    paginator = Paginator(reviews_list, 5)
    page_number = request.GET.get('page')
    reviews = paginator.get_page(page_number)
    genres = Book.objects.values_list('genre', flat=True).distinct()

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
    review = get_object_or_404(Review, id=review_id)

    if not request.user.is_staff:
        messages.error(request, "Только модератор может удалять отзывы")
        return redirect('vhod')

    review.delete()
    messages.success(request, "Отзыв удален")
    return redirect('moderator_panel')

def get_books_for_moderator(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'books': []})

    # Книги, купленные этим пользователем со статусом "Выполнен" И без отзыва
    books = Book.objects.filter(
        orderitem__id_order__id_user=user_id,
        orderitem__id_order__status_ord='Выполнен'
    ).exclude(review__id_user=user_id).distinct()

    data = [{'id': b.id, 'title': b.title} for b in books]
    return JsonResponse({'books': data})


def get_users_for_moderator(request):
    book_id = request.GET.get('book_id')
    if not book_id:
        return JsonResponse({'users': []})

    # Пользователи, купившие эту книгу со статусом "Выполнен" и без отзыва
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
            no_ord__id_user=user,   # ← здесь мы используем no_ord, а не id_order
            no_ord__status_ord='Выполнен',  # статус заказа
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

        # Создаём новый отзыв
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
    if not request.user.is_staff:
        return redirect('vhod')  # или страница доступа запрещена

    review = get_object_or_404(Review, id=review_id)
    review.status_rev = 'Опубликован'
    review.save()

    return redirect('moderator_panel')


def reject_review(request, review_id):
    if not request.user.is_staff:
        return redirect('vhod')

    review = get_object_or_404(Review, id=review_id)
    review.status_rev = 'Отказ в публикации'
    review.save()

    return redirect('moderator_panel')

def revert_review(request, review_id):
    if not request.user.is_staff:
        return redirect('vhod')

    review = get_object_or_404(Review, id=review_id)
    
    # Проверяем текущий статус отзыва
    if review.status_rev in ['Опубликован', 'Отказ в публикации']:
        review.status_rev = 'Обрабатывается'
        review.save()
        messages.success(request, "Отзыв отправлен обратно на модерацию")
    else:
        messages.warning(request, "Невозможно вернуть в обработку")

    return redirect('moderator_panel')

# def vhod(request):                                        #функция по работе страницы авторизации
    # if request.method == 'POST':
    #     username = request.POST.get('username')
    #     password = request.POST.get('password')
    #     action = request.POST.get('btn')
    #     if action == 'Войти':
    #         account = Accounts.objects.filter(username=username, password=password).first() #Если QuerySet пуст, то метод first() вернет None
    #         if account:
    #             messages.success(request, "Вход выполнен успешно!")
    #             request.session['user_id'] = account.id
    #             if account.id == 1:
    #                 return redirect('admin:login')
    #             else:
    #                 return redirect('hello_page_lk')
    #         else:
    #             messages.error(request, "Неверные имя пользователя или пароль.")
    #     elif action == 'Регистрация':
    #         try:
    #             Accounts.objects.get(username=username)
    #             messages.error(request, "Пользователь с таким именем уже существует.")
    #         except Accounts.DoesNotExist:
    #             new_account = Accounts.objects.create(username=username, password=password)
    #             messages.success(request, "Регистрация прошла успешно!")
    #             request.session['user_id'] = new_account.id                                           
    #             return redirect('hello_page_lk') 
    # return render(request, 'vhod.html')


# def regist(request):                                        #функция по работе страницы авторизации

    # return render(request, 'regist.html')

# from django.views.decorators.cache import cache_page
from django.db.models import Case, When, Value, IntegerField
# @cache_page(60 * 15)  # кэш на 15 минут
def avtoriz(request):
    # Получаем книги
    recommended_books = Book.objects.filter(genre="Фэнтези").prefetch_related('id_writer')[:4]
    new_books = Book.objects.filter(year__year=2025).prefetch_related('id_writer')[:4]

    best_books = Book.objects.filter(review__status_rev='Опубликован').annotate(
        avg_rating=Avg(Cast('review__rating', output_field=models.FloatField()))
    ).order_by('-avg_rating')[:4]

    latest_articles = Article.objects.all().order_by('-id')[:3]

    viewed_book_ids = request.session.get('viewed_books', [])

    viewed_books = []
    if viewed_book_ids:
        viewed_books = Book.objects.filter(id__in=viewed_book_ids).order_by(Case(*[When(id=id, then=pos) for pos, id in enumerate(viewed_book_ids)],output_field=models.IntegerField()))


    # Расчет цен со скидкой
    def calculate_discounted_price(books):
        for book in books:
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount - (book.discount * discount_percentage / 100))
            else:
                book.discounted_price = book.discount

    calculate_discounted_price(recommended_books)
    calculate_discounted_price(new_books)
    calculate_discounted_price(viewed_books)
    calculate_discounted_price(best_books)


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
        'best_books': best_books,
        'articles': latest_articles,
        'genres': genres,
        'user_fav_books': fav_user,
        'cart_books_ids': cart_books_ids, 
        'cart_count': cart_count, 
        'viewed_books': viewed_books,
        'show_viewed_section': len(viewed_book_ids) > 0
    })



def journal(request):
    query = request.GET.get('q', '')  # Получаем поисковый запрос

    if query:
        # Ищем совпадения в заголовках или текстах статей
        articles = Article.objects.filter(
            Q(title_article__icontains=query) | Q(text_article__icontains=query)
        )
    else:
        # Если поисковый запрос пустой — показываем все статьи
        articles = Article.objects.all()

    # Получение всех жанров для выпадающего меню каталога
    genres = Book.objects.values_list('genre', flat=True).distinct()
    

    return render(request, 'journal.html', {
        'articles': articles,
        'genres': genres,  # Передаем жанры в шаблон
        'query': query,
    })

def catalog(request, genre=None):
    query = request.GET.get('q', '')  # Получаем поисковый запрос
    page = request.GET.get('page', 1)  # Получаем номер страницы

    # Фильтрация по жанру и поиску
    if genre:
        books = Book.objects.filter(genre=genre)
    else:
        books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) | 
            Q(id_writer__nickname__icontains=query)
        ).distinct()

    # Пагинация
    paginator = Paginator(books, 4)  # 2 элемента на странице
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Расчет цены со скидкой
    for book in page_obj:
        if book.sale:
            discount_percentage = int(book.sale)
            book.discounted_price = round(book.discount - (book.discount * discount_percentage / 100))
        else:
            book.discounted_price = book.discount

    genres = Book.objects.values_list('genre', flat=True).distinct()

    return render(request, 'catalog.html', {
        'page_obj': page_obj,
        'genres': genres,
        'query': query,
        'current_genre': genre,
    })

def publishers_list(request):
    # Получаем все издательства
    publishers = PublishingHouse.objects.all()

    # Функция расчета цены (можно вынести в utils.py для переиспользования)
    def calculate_discounted_price(books_list):
        for book in books_list:
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount - (book.discount * discount_percentage / 100))
            else:
                book.discounted_price = book.discount

    # Создаем список издательств с лучшими книгами
    publishers_with_books = []
    genres = Book.objects.values_list('genre', flat=True).distinct()
    for publisher in publishers:
        best_books = list(Book.objects.filter(id_publish=publisher).order_by('-year')[:3])
 # Превращаем в список
        calculate_discounted_price(best_books)  # Рассчитываем скидки
        publishers_with_books.append({
            'publisher': publisher,
            'best_books': best_books,
        })

    return render(request, 'publishers.html', {
        'publishers_with_books': publishers_with_books,
        'genres': genres
    })


def journal2(request):
    query = request.GET.get('q', '')  # Получаем поисковый запрос

    if query:
        # Ищем совпадения в заголовках или текстах статей
        articles = Article.objects.filter(
            Q(title_article__icontains=query) | Q(text_article__icontains=query)
        )
    else:
        # Если поисковый запрос пустой — показываем все статьи
        articles = Article.objects.all()

    # Получение всех жанров для выпадающего меню каталога
    genres = Book.objects.values_list('genre', flat=True).distinct()
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = ShoppingCart.objects.filter(id_user=request.user).count()


    return render(request, 'journal2.html', {
        'articles': articles,
        'genres': genres,  # Передаем жанры в шаблон
        'query': query,
        'cart_count': cart_count
    })


def catalog2(request, genre=None):
    query = request.GET.get('q', '')  # Получаем поисковый запрос
    page = request.GET.get('page', 1)  # Получаем номер страницы

    # Фильтрация по жанру и поиску
    if genre:
        books = Book.objects.filter(genre=genre)
    else:
        books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) | 
            Q(id_writer__nickname__icontains=query)
        ).distinct()

    # Пагинация
    paginator = Paginator(books, 4)  # 2 элемента на странице
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Расчет цены со скидкой
    for book in page_obj:
        if book.sale:
            discount_percentage = int(book.sale)
            book.discounted_price = round(book.discount - (book.discount * discount_percentage / 100))
        else:
            book.discounted_price = book.discount

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
        'cart_count': cart_count
    })


def publishers_list2(request):
    # Получаем все издательства
    publishers = PublishingHouse.objects.all()

    # Функция расчета цены (можно вынести в utils.py для переиспользования)
    def calculate_discounted_price(books_list):
        for book in books_list:
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount - (book.discount * discount_percentage / 100))
            else:
                book.discounted_price = book.discount

    # Создаем список издательств с лучшими книгами
    publishers_with_books = []
    genres = Book.objects.values_list('genre', flat=True).distinct()
    for publisher in publishers:
        best_books = list(Book.objects.filter(id_publish=publisher).order_by('-year')[:3])
 # Превращаем в список
        calculate_discounted_price(best_books)  # Рассчитываем скидки
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
    # Получаем книги из корзины
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

    # Получаем все магазины для выпадающего списка
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
        'cart_count': cart_count  # Передаем в шаблон
    })

def cart_change_quantity(request, item_id, action):
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


def remove_from_cart(request, item_id):  # ← Обязательно должен быть item_id
    cart_item = get_object_or_404(ShoppingCart, id=item_id, id_user=request.user)
    cart_item.delete()
    return HttpResponseRedirect(reverse('shopcart'))


def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.user.is_authenticated:
        cart_item, created = ShoppingCart.objects.get_or_create(
            id_user=request.user,
            id_book=book,
            defaults={'count_cart': '1'}
        )
        if not created:
            # Если книга уже есть в корзине — не увеличиваем количество
            pass

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def remove_from_cart_by_book_id(request, book_id):
    if request.user.is_authenticated:
        # Удаляем все записи корзины с данной книгой
        ShoppingCart.objects.filter(id_user=request.user, id_book__id=book_id).delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

from django.db import transaction
def checkout(request):
    # Получаем все товары в корзине пользователя
    cart_items = ShoppingCart.objects.filter(id_user=request.user).select_related('id_book')

    if not cart_items.exists():
        messages.error(request, "В корзине нет товаров для оформления заказа")
        return redirect('shopcart')

    # Начинаем транзакцию
    with transaction.atomic():
        # Создаём заказ
        order = Order.objects.create(
            id_user=request.user,
            status_ord='Обрабатывается',
            id_shop_id=1  # ← можно выбрать магазин через форму или оставить по умолчанию
        )

        total_price = 0

        # Проходим по всем элементам корзины и создаём OrderItem
        for item in cart_items:
            book = item.id_book
            quantity = int(item.count_cart)

            # Расчёт цены книги со скидкой
            if book.sale:
                discount_percentage = int(book.sale)
                discounted_price = round(book.discount * (1 - discount_percentage / 100))
            else:
                discounted_price = book.discount

            # Сохраняем позиции заказа
            OrderItem.objects.create(
                no_ord=order,
                id_book=book,
                count_ord=item.count_cart
            )

            # Обновляем общую сумму заказа
            total_price += discounted_price * quantity

        # Обновляем цену заказа
        order.price = total_price
        order.save()

        # Очищаем корзину после оформления
        cart_items.delete()

    messages.success(request, "Заказ успешно оформлен")
    return redirect('shopcart')

def favourite(request):
    # Получаем все записи из избранного пользователя
    fav_items = Favourite.objects.filter(id_user=request.user).select_related('id_book')

    # Расчет цены со скидкой для всех книг
    def calculate_discounted_price(books):
        for book in books:
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount - (book.discount * discount_percentage / 100))
            else:
                book.discounted_price = book.discount

    books = [item.id_book for item in fav_items]
    calculate_discounted_price(books)

    # Пагинация: теперь page_obj содержит записи из Favourite
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
    if request.user.is_authenticated:
        fav_item = get_object_or_404(Favourite, id=item_id, id_user=request.user)
        fav_item.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def add_to_favourite(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.user.is_authenticated:
        # Проверяем, есть ли такая запись в избранном
        fav_item = Favourite.objects.filter(id_user=request.user, id_book=book).first()

        if fav_item:
            # Если уже в избранном — удаляем
            fav_item.delete()
        else:
            # Иначе добавляем
            Favourite.objects.create(id_user=request.user, id_book=book)

    # Возвращаем пользователя туда, откуда он пришёл
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def lk(request):
    # Получаем все заказы пользователя + предзагрузка связанных данных
    orders = Order.objects.filter(id_user=request.user).prefetch_related(
        'items__id_book__review',  # ← важно: prefetch по related_name='review'
    ).order_by('-date_ord')
    try:
        account = Account.objects.get(user=request.user)
    except Account.DoesNotExist:
        account = None

    user_reviews_books = Review.objects.filter(id_user=request.user).values_list('id_book_id', flat=True)
    # Расчёт цен для книг в заказах
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

            # Добавляем флаг наличия отзыва
            item.has_review = book.review.filter(id_user=request.user).exists()

            order.items_list.append(item)
        
    genres = Book.objects.values_list('genre', flat=True).distinct()
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = ShoppingCart.objects.filter(id_user=request.user).count() # Можно передать как отдельное свойство

    review_form = ReviewForm()

    return render(request, 'lk.html', {
        'orders': orders,
        'account': account,
        'genres': genres,
        'cart_count': cart_count,         
        'user_reviews_books': user_reviews_books, 
        'form': review_form,
    })

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Регистрация шрифта

from io import BytesIO
def generate_receipt(request, order_id):
    # Получаем заказ
    order = get_object_or_404(Order.objects.prefetch_related('items__id_book'), id=order_id)

    # Проверяем доступ
    if order.id_user != request.user and not request.user.is_staff:
        return HttpResponse("Доступ запрещён", status=403)

    
    # Регистрация шрифтов
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

    # Генерация PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    # Заголовок с жирным шрифтом
    styles['Title'].fontName = 'DejaVuSans-Bold'
    styles['Normal'].fontName = 'DejaVuSans'

    elements.append(Paragraph(f"Чек заказа #{order.id}", styles['Title']))
    elements.append(Spacer(1, 24))

    # Детали заказа
    elements.append(Paragraph(f"Дата: {order.date_ord.strftime('%d.%m.%Y')}", styles['Normal']))
    elements.append(Paragraph(f"Номер покупателя: {request.user.username}", styles['Normal']))
    elements.append(Paragraph(f"Магазин: {order.id_shop.street}", styles['Normal']))
    elements.append(Spacer(1, 12))


    # Данные таблицы
    data = [['Книга', 'Автор(ы)', 'Цена', 'Кол-во', 'Сумма']]
    total_price = 0

    for item in order.items.all():
        book = item.id_book
        count = int(item.count_ord)

        # Рассчитываем цену со скидкой
        if book.sale and book.sale.isdigit():
            price = round(book.discount * (1 - int(book.sale) / 100))
        else:
            price = book.discount

        total_item = price * count
        total_price += total_item

        authors = ", ".join(writer.nickname for writer in book.id_writer.all())
        data.append([book.title, authors, f"{price} ₽", str(count), f"{total_item} ₽"])

    # Таблица с оформлением
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),  # Темно-синий фон для заголовков
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

    # Итого
    elements.append(Paragraph(f"<b>Общая сумма:</b> {total_price} ₽", styles['Normal']))

    # Генерируем PDF
    doc.build(elements)
    pdf_value = buffer.getvalue()
    buffer.close()

    # Сохраняем в модель Order
    receipt_dir = os.path.join(settings.MEDIA_ROOT, 'receipts')
    os.makedirs(receipt_dir, exist_ok=True)

    receipt_path = os.path.join(receipt_dir, f'receipt_{order.id}.pdf')
    with open(receipt_path, 'wb') as f:
        f.write(pdf_value)

    order.receipt.name = f'receipts/receipt_{order.id}.pdf'
    order.save(update_fields=['receipt'])

    # Возвращаем файл пользователю
    response = HttpResponse(pdf_value, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=receipt_{order.id}.pdf'

    return response

def add_review(request):
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

# def lk(request):
#     orders = Order.objects.filter(id_user=request.user).prefetch_related(
#         'items__id_book', 
#         'items__id_book__review_set'
#     ).order_by('-date_ord')

#     try:
#         account = Account.objects.get(user=request.user)
#     except Account.DoesNotExist:
#         account = None

#     # Список книг, по которым пользователь уже оставил отзыв
#     user_reviews_books = Review.objects.filter(id_user=request.user).values_list('id_book_id', flat=True)

#     for order in orders:
#         order_items = order.items.all()
#         order.total_order_price = 0
#         order.items_list = []

#         for item in order_items:
#             book = item.id_book

#             if book.sale and book.sale.isdigit():
#                 discount_percentage = int(book.sale)
#                 final_price = round(book.discount * (1 - discount_percentage / 100))
#             else:
#                 final_price = book.discount

#             item.final_price = final_price
#             item.total_price = final_price * int(item.count_ord)
#             order.total_order_price += item.total_price

#             # Добавляем флаг наличия отзыва
#             item.has_review = book.id in user_reviews_books

#             order.items_list.append(item)

#     return render(request, 'lk.html', {
#         'orders': orders,
#         'account': account,
#         'user_reviews_books': user_reviews_books
#     })

def profile(request):
    user = request.user
    try:
        account = Account.objects.get(user=user)
    except Account.DoesNotExist:
        account = None

    # Передаем форму для модального окна
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

# def update_profile(request):
#     account = Account.objects.get(user=request.user)

#     if request.method == 'POST':
#         account.surname = request.POST.get('surname', account.surname)
#         account.name = request.POST.get('name', account.name)
#         account.birthday = request.POST.get('birthday')

#         if 'photo_acc' in request.FILES:
#             account.photo_acc = request.FILES['photo_acc']

#         account.save()
#         return redirect('profile')

#     return render(request, 'profile.html', {'account': account})

def update_profile(request):
    account  = Account.objects.get(user=request.user)

    if request.method == "POST":
        form = AccountForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            form.save()
            return redirect('profile')

    else:
        form = AccountForm(instance=account)

    # Вместо отдельного шаблона передаем в lk.html
    return render(request, 'profile.html', {'form': form, 'account': account})


def reviews(request):
    # Получаем все отзывы пользователя
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
    review = get_object_or_404(Review, id=review_id, id_user=request.user)
    review.delete()
    return redirect('reviews')

def custom_logout(request):
    logout(request)
    return redirect('index')  # или 'index'


def book_detail(request, book_id):
    # Получаем книгу с prefetch_related для оптимизации
    book = get_object_or_404(Book.objects.prefetch_related(
        'id_writer', 
        'review__id_user__account'
    ), id=book_id)

    # Рассчитываем цену со скидкой внутри view
    if book.sale and book.sale.isdigit():
        discount_percentage = int(book.sale)
        book.discounted_price = round(book.discount * (1 - discount_percentage / 100))
    else:
        book.discounted_price = book.discount

    # Получаем отзывы
    reviews = book.review.filter(status_rev='Опубликован')

    # Получаем статьи по книге
    articles = Article.objects.filter(id_book=book)

    # Проверяем, есть ли книга в корзине/избранном
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
        viewed_books.insert(0, book.id)  # В начало списка
        viewed_books = viewed_books[:4]  # Ограничиваем до 5 последних книг
        request.session['viewed_books'] = viewed_books
    # Передаём всё в шаблон
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
    # Получаем книгу с prefetch_related для оптимизации
    book = get_object_or_404(Book.objects.prefetch_related(
        'id_writer', 
        'review__id_user__account'
    ), id=book_id)

    # Рассчитываем цену со скидкой внутри view
    if book.sale and book.sale.isdigit():
        discount_percentage = int(book.sale)
        book.discounted_price = round(book.discount * (1 - discount_percentage / 100))
    else:
        book.discounted_price = book.discount

    # Получаем отзывы
    reviews = book.review.filter(status_rev='Опубликован')

    # Получаем статьи по книге
    articles = Article.objects.filter(id_book=book)

    genres = Book.objects.values_list('genre', flat=True).distinct()

    # Передаём всё в шаблон
    return render(request, 'book_detail2.html', {
        'book': book,
        'reviews': reviews,
        'articles': articles,      
        'genres': genres,

    })

def article(request, article_id):
    # Получаем статью по ID
    article = get_object_or_404(Article.objects.select_related('id_book'), id=article_id)
    
    book = article.id_book  # Получаем книгу из статьи
    
    # Так как id_writer ManyToMany, используем prefetch_related (или просто .all() при выводе)
    writers = book.id_writer.all()  # ← так можно получить авторов

    # Рассчитываем цену книги со скидкой
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
    # Получаем статью по ID
    article = get_object_or_404(Article.objects.select_related('id_book'), id=article_id)
    
    book = article.id_book  # Получаем книгу из статьи
    
    # Так как id_writer ManyToMany, используем prefetch_related (или просто .all() при выводе)
    writers = book.id_writer.all()  # ← так можно получить авторов

    # Рассчитываем цену книги со скидкой
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
