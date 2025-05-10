from django.db.models import Avg
from .models import Book, Article, PublishingHouse, ShoppingCart, Favourite, Shop, Order, Review, Account
from django.contrib.auth.models import User

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import logout


def index(request):

    # Фильтрация книг для "Новинок"
    new_books = Book.objects.filter(
        year__year=2025  # Книги, выпущенные в 2024 году
    ).prefetch_related('id_writer')[:4] 

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

    # Получение уникальных жанров из базы данных
    genres = Book.objects.values_list('genre', flat=True).distinct()

    # Передаем данные в шаблон
    return render(request, 'index.html', {
        'new_books': new_books,
        'genres': genres  # Добавляем жанры в контекст
    })

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages

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
            return redirect('avtoriz')  # Перенаправляем на страницу авторизованного пользователя
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


def avtoriz(request):
    # Получаем книги
    recommended_books = Book.objects.filter(genre="Фэнтези").prefetch_related('id_writer')[:4]
    new_books = Book.objects.filter(year__year=2025).prefetch_related('id_writer')[:4]

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
        'genres': genres,
        'user_fav_books': fav_user,
        'cart_books_ids': cart_books_ids, 
        'cart_count': cart_count # ← Передаем в шаблон
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

    return HttpResponseRedirect(reverse('favourite'))

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
    # Получаем все заказы пользователя
    orders = Order.objects.filter(id_user=request.user).order_by('-date_ord')

    return render(request, 'lk.html', {
        'orders': orders,
    })

def profile(request):
    # Получаем все заказы пользователя

    user = request.user

    try:
        account = Account.objects.get(user=user)
    except Account.DoesNotExist:
        account = None

    return render(request, 'profile.html', {
        'account': account,
    })


def update_profile(request):
    account = Account.objects.get(user=request.user)

    if request.method == 'POST':
        account.surname = request.POST.get('surname', account.surname)
        account.name = request.POST.get('name', account.name)
        account.birthday = request.POST.get('birthday')

        if 'photo_acc' in request.FILES:
            account.photo_acc = request.FILES['photo_acc']

        account.save()
        return redirect('profile')

    return render(request, 'profile.html', {'account': account})


def reviews(request):


    # Получаем все отзывы пользователя
    reviews = Review.objects.filter(id_user=request.user).select_related('id_book')

    return render(request, 'reviews.html', {

        'reviews': reviews,

    })


def custom_logout(request):
    logout(request)
    return redirect('avtoriz')  # или 'index'