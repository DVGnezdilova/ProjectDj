from rest_framework import serializers
from books.models import Book, Writer, PublishingHouse, Review, Order, ShoppingCart, Article

class WriterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Writer
        fields = ['id', 'nickname']

class PublishingHouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublishingHouse
        fields = ['id', 'name_publish']

class BookSerializer(serializers.ModelSerializer):
    writers = WriterSerializer(source='id_writer', many=True)
    avg_rating = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'genre', 'year', 'photo',
            'discount', 'sale', 'writers', 'avg_rating',
            'discounted_price'
        ]

    def get_avg_rating(self, obj):
        return obj.get_avg_rating() or 0

    def get_discounted_price(self, obj):
        if obj.sale:
            try:
                sale_percent = int(obj.sale)
                return round(obj.discount - (obj.discount * sale_percent / 100))
            except ValueError:
                return obj.discount
        else:
            return obj.discount

