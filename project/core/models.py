from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    def __str__(self):
        return self.username
    
class Book(models.Model):
    google_book_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=300)
    authors = models.CharField(max_length=300, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    published_date = models.CharField(max_length=50, blank=True)
    thumbnail = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

class UserBook(models.Model):
    STATUS_CHOICES = [
        ('plan', 'Planejo ler'),
        ('reading', 'Lendo'),
        ('completed', 'Completo'),
        ('dropped', 'Abandonado'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='userbooks')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='userbooks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='plan')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')  # um usuário não pode adicionar o mesmo livro duas vezes

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"