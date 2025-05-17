"""
URL configuration for BooksForEveryone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from books.views import index, vhod, regist,moderator_dashboard,moderator_panel,delete_review_mod,create_review_mod, get_books_for_moderator, get_users_for_moderator, publish_review, reject_review,revert_review, avtoriz, journal, catalog, publishers_list, journal2, catalog2, publishers_list2, shopcart, checkout, cart_change_quantity, remove_from_cart, add_to_cart,favourite,remove_from_favourite, add_to_favourite, remove_from_cart_by_book_id, lk,  add_review, custom_logout, profile, update_profile, reviews, delete_review, book_detail, book_detail2, article, article2
from django.urls import include, path
from books.views import generate_receipt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('vhod/', vhod, name='vhod'),
    path('regist/', regist, name='regist'),
    path('moderator/', moderator_dashboard, name='moderator_dashboard'),
    path('moderator_panel/', moderator_panel, name='moderator_panel'),
    path('review/delete/<int:review_id>/', delete_review_mod, name='delete_review_mod'),
    path('moderator/get_books/', get_books_for_moderator, name='get_books_for_moderator'),
    path('moderator/get_users/', get_users_for_moderator, name='get_users_for_moderator'),
    path('moderator/review/add/', create_review_mod, name='create_review_mod'),
    path('review/publish/<int:review_id>/', publish_review, name='publish_review'),
    path('review/reject/<int:review_id>/', reject_review, name='reject_review'),
    path('review/revert/<int:review_id>/', revert_review, name='revert_review'),
    path('avtoriz/', avtoriz, name='avtoriz'),
    path('journal/', journal, name='journal'),
    path('catalog/<str:genre>/', catalog, name='catalog'),
    path('publishers/', publishers_list, name='publishers'),
    path('journal2/', journal2, name='journal2'),
    path('catalog2/<str:genre>/', catalog2, name='catalog2'),
    path('publishers2/', publishers_list2, name='publishers2'),
    path('shopcart/', shopcart, name='shopcart'),
    path('checkout/', checkout, name='checkout'),
    path('cart/change-quantity/<int:item_id>/<str:action>/', cart_change_quantity, name='cart_change_quantity'),
    path('shopcart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/add/<int:book_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/book/<int:book_id>/', remove_from_cart_by_book_id, name='remove_from_cart_by_book'),
    path('favourite/', favourite, name='favourite'),
    path('favourite/remove/<int:item_id>/', remove_from_favourite, name='remove_from_favourite'),
    path('favourite/add/<int:book_id>/', add_to_favourite, name='add_to_favourite'),
    path('lk/', lk, name='lk'),
    path('receipt/<int:order_id>/', generate_receipt, name='generate_receipt'),
    path('add-review/', add_review, name='add_review'),
    path('profile/', profile, name='profile'),
    path('lk/update/', update_profile, name='update_profile'),
    path('reviews/', reviews, name='reviews'),
    path('delete-review/<int:review_id>/', delete_review, name='delete_review'),
    path('logout/', custom_logout, name='logout'),
    path('book/<int:book_id>/', book_detail, name='book_detail'),
    path('book2/<int:book_id>/', book_detail2, name='book_detail2'),
    path('article/<int:article_id>/', article, name='article'),
    path('article2/<int:article_id>/', article2, name='article2'),
    path('__debug__/', include('debug_toolbar.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

