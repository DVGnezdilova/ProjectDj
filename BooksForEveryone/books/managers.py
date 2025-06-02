from django.db import models
from itertools import chain

class ReviewManager(models.Manager):
    def get_queryset(self):
        processing = super().get_queryset().filter(status_rev='Обрабатывается').order_by('created_at')

        published = super().get_queryset().filter(status_rev='Опубликован').order_by('-created_at')

        rejected = super().get_queryset().filter(status_rev='Отказ в публикации').order_by('-created_at')

        # Объединяем результаты
        return list(chain(processing, published, rejected))