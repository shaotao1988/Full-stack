from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
   url('^$', views.index, name = 'index'),
   path('books/', views.BookListView.as_view(), name = 'books'),
   path('book/<int:id>', views.book_detail_view, name = 'book-detail'), 
]