from django.contrib import admin
from books.models import Writer, PublishingHouse, BookWriter, Book, Account, Article, Shop, ShoppingCart, Favourite, Order, OrderItem, Review,Feedback
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

#from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('type', 'email', 'created_at')
    list_filter = ('type',)
    search_fields = ('email', 'message')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('type', 'message', 'email', 'created_at')
        }),
    )
    ordering = ('-created_at',)


@admin.register(Writer) 
class WriterAdmin(admin.ModelAdmin): 
    list_display = ('id', 'nickname', 'photo_writ', 'biography')
    list_display_links = ('nickname',)
    search_fields = ('nickname',)
    # def __str__(self):
    #     return self.nickname or "Без имени"
    


@admin.register(PublishingHouse) 
class PublishingHouseAdmin(admin.ModelAdmin): 
    list_display = ('id', 'name_publish', 'photo_publish', 'publish_description')
    filter_horizontal = ('id_writers',)
    list_display_links = ('name_publish',)
    search_fields = ('name_publish',)

#    @admin.display(description='Писатели')  #декоратор для кастомизации
#    def writer(self, obj): #метод для отображения связанных писателей в административной панели модели `Books`
#        return ', '.join([writer.nickname for writer in obj.id_writer.all()]) 


@admin.register(BookWriter) 
class BookWriterAdmin(admin.ModelAdmin): 
    list_display = ('id', 'book', 'writer', 'role')
    list_display_links = ('book','role',)
    search_fields = ('writer','book',)   #!!!!добавить поиск по писателю
    # raw_id_fields = ('id_publish',)

from simple_history.admin import SimpleHistoryAdmin

@admin.register(Book) 
class BookAdmin(SimpleHistoryAdmin): 
    list_display = ('id', 'isbn', 'title', 'photo','genre','id_publish','num_page','year','discount','sale','description')
    list_display_links = ('title',)
    search_fields = ('isbn','title','isbn')   #!!!!добавить поиск по писателю
    raw_id_fields = ('id_publish',)

    
    @admin.display(description='Писатели')  #декоратор для кастомизации
    def writer(self, obj): #метод для отображения связанных писателей в административной панели модели `Books`
        return ', '.join([writer.nickname for writer in obj.id_writer.all()]) 



class CustomUserAdmin(UserAdmin):
    # Переопределяем fieldsets для изменения метки "username"
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    # Переопределяем add_fieldsets для создания пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    # Переопределяем отображение списка пользователей
    list_display = ('username', 'is_staff', 'is_active')

    # Меняем метку "Имя пользователя" на "Номер пользователя"
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['username'].label = "Номер пользователя"
        return form

# Заменяем стандартную админку User на кастомную
admin.site.unregister(User)  # Убираем стандартную регистрацию
admin.site.register(User, CustomUserAdmin)

# Регистрируем модель Account
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'surname', 'name', 'birthday')  # Поля для отображения в списке
    search_fields = ('surname', 'name', 'user__username')  # Поля для поиска
    list_filter = ('birthday',)  # Фильтры для удобства
    list_display_links = ('surname', 'name')
    search_fields = ('surname', 'name')
    def photo_acc_preview(self, obj):
        if obj.photo_acc:
            return f'<img src="{obj.photo_acc.url}" width="100" />'
        return "Нет аватарки"
    photo_acc_preview.allow_tags = True

@admin.register(Article) 
class ArticleAdmin(admin.ModelAdmin): 
    list_display = ('id', 'title_article', 'id_book', 'photo_article', 'text_article')
    list_display_links = ('title_article',)
    search_fields = ('title_article',) #!!!!добавить поиск по книге

@admin.register(Shop) 
class ShopAdmin(admin.ModelAdmin): 
    list_display = ('id', 'city','street', 'transport')
    list_display_links = ('city','street')
    search_fields = ('city','street', 'transport','google_maps_url')

@admin.register(ShoppingCart) 
class ShoppingCartAdmin(admin.ModelAdmin):      #!!!!тянуть номер пользователя, а также название книги
    list_display = ('id', 'id_user','id_book', 'count_cart')
    list_display_links = ('id_user','id_book')
    search_fields = ('id_user','id_book')   #!!!!добавить поиск по книге и пользователю

@admin.register(Favourite) 
class FavouriteAdmin(admin.ModelAdmin):   #!!!!тянуть номер пользователя, а также название книги
    list_display = ('id', 'id_user','id_book')
    list_display_links = ('id_user','id_book')
    search_fields = ('id_user','id_book')     #!!!!добавить поиск по книге и пользователю

class OrderItemInline(admin.TabularInline):
    model = OrderItem

@admin.register(Order) 
class OrderAdmin(admin.ModelAdmin):    #!!!!тянуть номер пользователя
    list_display = ('id', 'date_ord', 'id_user', 'id_shop', 'status_ord', 'price')
    inlines = [OrderItemInline]
    date_hierarchy = 'date_ord'
    list_display_links = ('id','id_user')
    readonly_fields = ('price',)
    search_fields = ('id','id_user') #!!!!добавить поиск по номеру пользователя
    raw_id_fields = ('id_shop',)
    def receipt_link(self, obj):
        if obj.receipt:
            return f'<a href="{obj.receipt.url}" target="_blank">Скачать</a>'
        return "Чек не загружен"
    receipt_link.allow_tags = True

@admin.register(OrderItem) 
class OrderItemAdmin(admin.ModelAdmin): 
    list_display = ('id', 'no_ord', 'id_book','count_ord')
    list_display_links = ('id', 'no_ord')
    search_fields = ('no_ord',) 
    raw_id_fields = ('no_ord',)


@admin.register(Review) 
class ReviewAdmin(admin.ModelAdmin):    
    list_display = ('id', 'id_user', 'id_book','text_review','rating','status_rev', 'created_at')
    list_display_links = ('id', 'id_user', 'id_book')
    search_fields = ('id_user','id_book')   #!!!!добавить поиск по номеру пользователя


