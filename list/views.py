from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import BookDate, UserProfile, Book, Review, Invite
from django.views import generic
from .forms import BookDateForm, SignUpForm
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.core import serializers
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
import datetime
from collections import OrderedDict
from django.utils.http import is_safe_url


@login_required
def friends(request):
    context = {
        'friends': [profile.user for profile in request.user.profile.friends.all()],
        'invites':[invite.from_user.user for invite in request.user.profile.invites_to_me.all()],
        'current_tab': "friends",
    }
    return render(request, 'friends.html', context)

def allbooks(request):
    context = {
        'books': Book.objects.all(),
        'current_tab': "reviews"
    }
    return render(request, 'allbooks.html', context)

def reviews(request, pk):
    book = get_object_or_404(Book, pk=pk)
    context = {
        'book': book,
        'reviews': Review.objects.filter(book=book),
        'invites_from_me': [invite.to_user.user for invite in request.user.profile.invites_from_me.all()],
        'current_tab': "reviews"
    }
    return render(request, 'reviews.html', context)

def users(request):
    user_list = get_user_model().objects.all()
    context = {
        'users': user_list,
        'invites_from_me': [invite.to_user.user for invite in request.user.profile.invites_from_me.all()],
        'current_tab': "friends"
    }
    return render(request, 'userslist.html', context)

def create_bookdate(POST, user):
    form = BookDateForm(POST)
    print(form)
    valid = form.is_valid()
    print(valid)
    bookdate_pk = None
    if valid:
        title = form.cleaned_data.get('title').strip()
        notes = form.cleaned_data.get('notes')
        month = form.cleaned_data.get('month')
        year  = form.cleaned_data.get('year')
        date = datetime.date(month=month, year=year, day=1)
        try:
            book = Book.objects.get(title=title)
        except:
            book = Book(title=title)
            book.save()

        if notes: Review(book=book, text=notes, user=user).save()

        bookdate = BookDate(book=book, notes=notes, date=date, user=user)
        bookdate.save()
        bookdate_pk = bookdate.pk
    return valid, form, bookdate_pk

def get_list(user):
    bookdate_list = BookDate.objects.filter(user=user)
    dates = bookdate_list.dates('date', 'month')
    dct = OrderedDict()
    for date in dates:
        if not date.year in dct:
            dct[date.year] = OrderedDict()
        dct[date.year][date.month] = bookdate_list.filter(date=date)
    return dct

@never_cache
def readonly_list(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    context = {
            'list': get_list(user),
            'another_owner': user,
            'current_tab': 'list',
            'invites_from_me': [invite.to_user.user for invite in request.user.profile.invites_from_me.all()]
    }
    return render(request, 'list.html', context)

@login_required
@never_cache
def home(request):
    if request.method == 'POST':
        create_bookdate(request.POST, request.user)
        return redirect(request.GET.get('next', '/') + "#new")
    else:
        form = BookDateForm()
    context = {
        'list': get_list(request.user),
        'form': form,
        'all_books': [book.title for book in Book.objects.all()],
        'current_tab': 'list',
        'cannot_view': False,
    }
    return render(request, 'list.html', context)


@login_required
def post_bookdate_form(request):
    valid, form, bookdate_pk = create_bookdate(request)
    if valid:
        return JsonResponse({'error': False, 'bookdate_pk': bookdate_pk})
    else:
        return JsonResponse({'error': True})

@login_required
def delbookdate(request, pk=None):
    if pk == None:
        pk = request.GET.get('pk')
    bookdate = get_object_or_404(BookDate, pk=pk)
    if bookdate.user == request.user:
        bookdate.delete()
    return redirect('home')
@login_required
def delreview(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user == request.user:
        review.delete()
    return redirect(request.GET.get('next', 'home'))
@login_required
def setprivate(request, value):
    if value == 'true':
        request.user.profile.is_list_private = True
    elif value == 'false':
        request.user.profile.is_list_private = False
    request.user.save()
    return redirect(request.GET.get('next', 'home'))
@login_required
def send_invite(request, username):
    from_user = request.user.profile
    to_user = get_object_or_404(get_user_model(), username=username).profile
    if Invite.objects.filter(from_user=to_user, to_user=from_user).exists():
        Invite.objects.get(from_user=to_user, to_user=from_user).delete()
        to_user.friends.add(from_user)
    elif to_user != from_user:
        invite = Invite.objects.create(to_user=to_user, from_user=from_user)
    return redirect(request.GET.get('next', 'home'))
@login_required
def accept_invite(request, username):
    to_user = request.user.profile
    from_user = get_object_or_404(get_user_model(), username=username).profile
    get_object_or_404(Invite, to_user=to_user, from_user=from_user).delete()
    to_user.friends.add(from_user)
    return redirect(request.GET.get('next', 'home'))
@login_required
def decline_invite(request, username):
    to_user = request.user.profile
    from_user = get_object_or_404(get_user_model(), username=username).profile
    get_object_or_404(Invite, to_user=to_user, from_user=from_user).delete()
    return redirect(request.GET.get('next', 'home'))

@never_cache
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            # load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')

            # login user after signing up
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)

            # redirect user to home page
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
