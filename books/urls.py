from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/<str:book_id>/', views.book_detail, name='book_detail'),
    path('accessed/', views.accessed_books, name='accessed_books'),
    path('analyze/<str:book_id>/<str:analysis_type>/', views.analyze_book, name='analyze_book'),
]