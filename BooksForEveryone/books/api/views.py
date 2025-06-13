from rest_framework import viewsets,  status
from rest_framework.decorators import api_view
from books.models import Book, Favourite, ShoppingCart, Feedback
from books.api.serializers import BookSerializer
from django.db.models.functions import Cast
from django.db.models import Avg, FloatField
from rest_framework.decorators import action
from rest_framework.response import Response

@api_view(['GET'])
def get_cart_books(request):
    if request.user.is_authenticated:
        return Response(list(ShoppingCart.objects.filter(id_user=request.user).values_list('id_book_id', flat=True)))
    return Response([])

@api_view(['GET'])
def get_favourite_books(request):
    if request.user.is_authenticated:
        return Response(list(Favourite.objects.filter(id_user=request.user).values_list('id_book_id', flat=True)))
    return Response([])

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    # 🔹 Действие для всех книг: GET /api/books/top-rated/
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """
        Возвращает книги со средним рейтингом выше 4.0
        """
        books = Book.objects.all()
        rated_books = []

        for book in books:
            avg_rating = book.get_avg_rating()  # метод из модели
            if avg_rating >= 3:
                rated_books.append(book)

        serializer = self.get_serializer(rated_books, many=True)
        return Response(serializer.data)

# @action(detail=False, methods=['get'])
# def top_rated(self, request):
#     return Response({'status': 'Эндпоинт работает!'})


from .serializers import FeedbackSerializer



class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    http_method_names = ['post']  # только POST для формы обратной связи

    @action(methods=['POST'], detail=False)
    def submit(self, request):
        """
        Обработка отправки формы обратной связи
        URL: /api/feedback/submit/
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            feedback = serializer.save(status_feed='Новый')  # статус по умолчанию
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)