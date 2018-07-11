from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
   url('^$', views.index, name = 'index'),
   path('books/', views.BookListView.as_view(), name = 'books'),
   path('book/<int:id>/', views.book_detail_view, name = 'book-detail'), 
   path('authors/', views.author_list_view, name = 'author-list'),  
   path('author/<int:id>/', views.author_detail_view, name = 'author-detail'),  
   path('mybooks/', views.LoanBooksByUserListView.as_view(), name = 'my-borrowed'),
   path('borrowed/', views.LoanBooksListView.as_view(), name = 'borrowed-list'),
   path('book/<uuid:pk>/renew/', views.renew_book_librarian, name = 'renew-book-librarian'),
]