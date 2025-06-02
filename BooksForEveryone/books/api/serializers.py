from rest_framework import serializers
from books.models import Book, Writer, PublishingHouse, Review, Order, ShoppingCart, Article

class WriterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Writer
        fields = '__all__'

class PublishingHouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublishingHouse
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    writers = WriterSerializer(source='id_writer', many=True, read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'genre', 'year', 'discount', 'sale', 'description', 'writers']

