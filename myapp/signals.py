from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserBook


@receiver(post_save, sender=UserBook)
def decrease_book_quantity(sender, instance, created, **kwargs):
    if created:  # Only run when a new UserBook is created
        book = instance.book
        if book.quantity > 0:
            book.quantity -= 1
            book.save()
                
