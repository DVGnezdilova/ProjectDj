from django.db.models import Avg
from .models import Book, Article
from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def index(request):

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
            return redirect('avtoriz.html')  # Перенаправляем на страницу авторизованного пользователя
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

    # Получение уникальных жанров из базы данных
    genres = Book.objects.values_list('genre', flat=True).distinct()

    # Передаем данные в шаблон
    return render(request, 'avtoriz.html', {
        'recommended_books': recommended_books,
        'new_books': new_books,
        'genres': genres  # Добавляем жанры в контекст
    })


def journal(request):                                        #функция по работе страницы авторизации
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

    # Получение уникальных жанров из базы данных
    genres = Book.objects.values_list('genre', flat=True).distinct()

    # Получаем все статьи из базы данных
    articles = Article.objects.all()


    # Передаем данные в шаблон
    return render(request, 'journal.html', {
        # 'recommended_books': recommended_books,
        # 'new_books': new_books,
        'articles': articles,
        'genres': genres  # Добавляем жанры в контекст
    })

def catalog(request, genre):
    # Фильтрация книг по жанру
    new_books = Book.objects.filter(genre=genre).prefetch_related('id_writer')
    
    # Расчет цены со скидкой
    def calculate_discounted_price(books):
        for book in books:
            if book.sale:
                discount_percentage = int(book.sale)
                book.discounted_price = round(book.discount - (book.discount * discount_percentage / 100))
            else:
                book.discounted_price = book.discount
    
    calculate_discounted_price(new_books)
    
    # Получение всех жанров (для фильтров на странице каталога)
    genres = Book.objects.values_list('genre', flat=True).distinct()
    
    return render(request, 'catalog.html', {
        'new_books': new_books,
        'genres': genres,
        'current_genre': genre,
    })

