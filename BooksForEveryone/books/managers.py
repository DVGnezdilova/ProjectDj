from django.db import models
from itertools import chain

class ReviewManager(models.Manager):
    def get_queryset(self):
        # Сначала "Обрабатывается" — старые сверху
        processing = super().get_queryset().filter(status_rev='Обрабатывается').order_by('created_at')

        # Затем "Опубликован" — новые сверху
        published = super().get_queryset().filter(status_rev='Опубликован').order_by('-created_at')

        # В конце — "Отказ в публикации"
        rejected = super().get_queryset().filter(status_rev='Отказ в публикации').order_by('-created_at')

        # Объединяем результаты
        return list(chain(processing, published, rejected))