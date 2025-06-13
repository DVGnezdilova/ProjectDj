from django.urls import path, include
from rest_framework.routers import DefaultRouter
from books.api.views import BookViewSet, FeedbackViewSet

# Создаём один роутер и регистрируем оба ViewSet
router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

# Теперь просто подключаем все маршруты из роутера
urlpatterns = [
    path('', include(router.urls)),  # ← всё API здесь
]