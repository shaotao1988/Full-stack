from django.shortcuts import render, get_object_or_404
from django.views import generic

# Create your views here.

from .models import Author, Book, BookInstance, Genre


def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()
    num_authors = Author.objects.all().count()
    print('index view')

    return render(request, 'index.html',
                  context={'num_books': num_books,
                           'num_instances': num_instances,
                           'num_instances_available': num_instances_available,
                           'num_authors': num_authors})

def book_detail_view(request, id):
    book = get_object_or_404(Book, id = id)
    return render(
        request,
        'book_detail.html',
        context={'book': book}
    )

class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list'
    # queryset = Book.objects.all()[:5]
    paginate_by = 2
    template_name = 'book_list.html'

class BookDetailView(generic.DetailView):
    model = Book

def author_list_view(request):
    author_list = Author.objects.all()
    return render(request, 'author_list.html', context = {'author_list': author_list})

def author_detail_view(request, id):
    author = get_object_or_404(Author, id = id)
    return render(request, 'author_detail.html', context = {'author': author})