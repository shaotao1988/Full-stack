from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

# Create your views here.

from .models import Author, Book, BookInstance, Genre
from .form import RenewBookForm


def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()
    num_authors = Author.objects.all().count()

    num_visits = request.session.get('num_visit', 0)
    request.session['num_visit'] = num_visits+1

    return render(request, 'index.html',
                  context={'num_books': num_books,
                           'num_instances': num_instances,
                           'num_instances_available': num_instances_available,
                           'num_authors': num_authors,
                           'num_visits': num_visits})

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
    paginate_by = 5
    template_name = 'book_list.html'

class BookDetailView(generic.DetailView):
    model = Book

def author_list_view(request):
    author_list = Author.objects.all()
    return render(request, 'author_list.html', context = {'author_list': author_list})

def author_detail_view(request, id):
    author = get_object_or_404(Author, id = id)
    return render(request, 'author_detail.html', context = {'author': author})

class LoanBooksByUserListView(LoginRequiredMixin, generic.ListView):

    model = BookInstance
    template_name = 'bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower = self.request.user)\
                                   .filter(status__exact = 'o')\
                                   .order_by('due_back')

class LoanBooksListView(generic.ListView):
    model = BookInstance
    template_name = 'bookinstance_list_borrowed.html'

    def get_queryset(self):
        return BookInstance.objects.filter(status__in = ['o', 'a']).order_by('due_back')

def renew_book_librarian(request, pk):
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('borrowed-list') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'book_renew_librarian.html', {'form': form, 'bookinst': book_inst})
