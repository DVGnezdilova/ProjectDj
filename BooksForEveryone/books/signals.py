from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Account

# Сигнал для создания профиля Account при создании пользователя
@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        # Создаем связанный профиль Account
        Account.objects.create(user=instance)