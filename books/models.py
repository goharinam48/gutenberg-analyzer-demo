from django.db import models
from django.contrib.auth.models import User
import json

class Book(models.Model):
    book_id = models.CharField(max_length=20, unique=True)
    text = models.TextField()
    metadata = models.JSONField()  # Store metadata as JSON
    accessed_by = models.ManyToManyField(User, related_name='accessed_books')

    def __str__(self):
        return f"Book {self.book_id}"