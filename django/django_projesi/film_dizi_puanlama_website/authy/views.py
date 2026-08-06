from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.models import User
from authy.models import Profile
from movie.models import Movie, Review, Likes

from comment.models import Comment
from comment.forms import CommentForm

from authy.forms import SignupForm, ChangePasswordForm, EditProfileForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, logout
from django.template import loader
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.core.paginator import Paginator
# Create your views here.

# Kullanıcı kayıt işlemi
def Signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			email = form.cleaned_data.get('email')
			first_name = form.cleaned_data.get('first_name')
			last_name = form.cleaned_data.get('last_name')
			password = form.cleaned_data.get('password')
			User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
			return redirect('login')
	else:
		form = SignupForm()

	context = {
		'form': form,
	}

	return render(request, 'registration/signup.html', context)

# Oturumu kapatma işlemi
@login_required
def Logout(request):
	logout(request)
	return redirect('login')

# Şifre değiştirme işlemi
@login_required
def PasswordChange(request):
	user = request.user

	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			new_password = form.cleaned_data.get('new_password')
			user.set_password(new_password)
			user.save()
			update_session_auth_hash(request, user)
			return redirect('change-password-done')
	else:
		form = ChangePasswordForm(instance=user)

	context = {
		'form': form,
	}

	return render(request, 'registration/change_password.html', context)

# Şifre değiştirme işlemi tamamlandığında gösterilecek sayfa
@login_required
def PasswordChangeDone(request):
	return render(request, 'registration/change_password_done.html')

# Profil düzenleme işlemi
@login_required
def EditProfile(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            if 'picture' in request.FILES:
                new_picture = request.FILES['picture']
                # Eğer yeni bir resim yüklendiğinde
                if new_picture != profile.picture:
                    # Eski resmi sil
                    if profile.picture:
                        profile.picture.delete()
                    # Yeni resmi kaydet
                    profile.picture = new_picture
            profile.save()
            return redirect('index')
    else:
        form = EditProfileForm(instance=profile)

    context = {
        'form': form,
    }

    return render(request, 'edit_profile.html', context)

# Kullanıcı profil sayfası
@login_required
def UserProfile(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)

	#Filmlerin izlenen veya izlenecek olanların sayacı
	mWatched_count = profile.watched.filter(Type='movie').count()
	sWatched_count = profile.watched.filter(Type='series').count()
	watch_list_count = profile.to_watch.all().count()
	m_reviewd_count = Review.objects.filter(user=user).count()

	context = {
		'profile': profile,
		'mWatched_count': mWatched_count,
		'sWatched_count': sWatched_count,
		'watch_list_count': watch_list_count,
		'm_reviewd_count': m_reviewd_count,
	}

	template = loader.get_template('profile.html')

	return HttpResponse(template.render(context, request))

# Kullanıcının izlediği filmleri gösteren sayfa
def UserProfileMoviesWatched(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)

	#Filmlerin izlenen veya izlenecek olanların sayacı
	mWatched_count = profile.watched.filter(Type='movie').count()
	sWatched_count = profile.watched.filter(Type='series').count()
	watch_list_count = profile.to_watch.all().count()
	m_reviewd_count = Review.objects.filter(user=user).count()

	#Filmler listesi
	movies = profile.watched.filter(Type='movie')
	paginator = Paginator(movies, 9)
	page_number = request.GET.get('page')
	movie_data = paginator.get_page(page_number)

	context = {
		'profile': profile,
		'mWatched_count': mWatched_count,
		'sWatched_count': sWatched_count,
		'watch_list_count': watch_list_count,
		'm_reviewd_count': m_reviewd_count,
		'movie_data': movie_data,
		'list_title': 'Movies Watched',
	}

	template = loader.get_template('profile.html')

	return HttpResponse(template.render(context, request))

# Kullanıcının izlediği dizileri gösteren sayfa
def UserProfileSeriesWatched(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)

	#Filmlerin izlenen veya izlenecek olanların sayacı
	mWatched_count = profile.watched.filter(Type='movie').count()
	sWatched_count = profile.watched.filter(Type='series').count()
	watch_list_count = profile.to_watch.all().count()
	m_reviewd_count = Review.objects.filter(user=user).count()

	#Filmler listesi
	movies = profile.watched.filter(Type='series')
	paginator = Paginator(movies, 9)
	page_number = request.GET.get('page')
	movie_data = paginator.get_page(page_number)
	
	context = {
		'profile': profile,
		'mWatched_count': mWatched_count,
		'sWatched_count': sWatched_count,
		'watch_list_count': watch_list_count,
		'm_reviewd_count': m_reviewd_count,
		'movie_data': movie_data,
		'list_title': 'Series Watched',
	}

	template = loader.get_template('profile.html')

	return HttpResponse(template.render(context, request))

# Kullanıcının izleme listesini gösteren sayfa
def UserProfileWatchList(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)

	#Filmlerin izlenen veya izlenecek olanların sayacı
	mWatched_count = profile.watched.filter(Type='movie').count()
	sWatched_count = profile.watched.filter(Type='series').count()
	watch_list_count = profile.to_watch.all().count()
	m_reviewd_count = Review.objects.filter(user=user).count()

	#Filmler listesi
	movies = profile.to_watch.all()
	paginator = Paginator(movies, 9)
	page_number = request.GET.get('page')
	movie_data = paginator.get_page(page_number)
	
	context = {
		'profile': profile,
		'mWatched_count': mWatched_count,
		'sWatched_count': sWatched_count,
		'watch_list_count': watch_list_count,
		'm_reviewd_count': m_reviewd_count,
		'movie_data': movie_data,
		'list_title': 'Watchist',
	}

	template = loader.get_template('profile.html')

	return HttpResponse(template.render(context, request))

# Kullanıcının incelediği film ve dizileri gösteren sayfa
def UserProfileMoviesReviewed(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)

	#Filmlerin izlenen veya izlenecek olanların sayacı
	mWatched_count = profile.watched.filter(Type='movie').count()
	sWatched_count = profile.watched.filter(Type='series').count()
	watch_list_count = profile.to_watch.all().count()
	m_reviewd_count = Review.objects.filter(user=user).count()

	#Filmler listesi
	movies = Review.objects.filter(user=user)
	paginator = Paginator(movies, 9)
	page_number = request.GET.get('page')
	movie_data = paginator.get_page(page_number)
	
	context = {
		'profile': profile,
		'mWatched_count': mWatched_count,
		'sWatched_count': sWatched_count,
		'watch_list_count': watch_list_count,
		'm_reviewd_count': m_reviewd_count,
		'movie_data': movie_data,
		'list_title': 'Reviewed',
	}

	template = loader.get_template('profile.html')

	return HttpResponse(template.render(context, request))

# İnceleme detaylarını gösteren sayfa
def ReviewDetail(request, username, imdb_id):
	user_comment = request.user
	user = get_object_or_404(User, username=username)
	movie = Movie.objects.get(imdbID=imdb_id)
	review = Review.objects.get(user=user, movie=movie)

	#Yorum
	comments = Comment.objects.filter(review=review).order_by('date')

	#Yorum Formu
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.review = review
			comment.user = user_comment
			comment.save()
			return HttpResponseRedirect(reverse('user-review', args=[username, imdb_id]))
	else:
		form = CommentForm()

	context = {
		'review': review,
		'movie' : movie,
		'comments': comments,
		'form': form,
	}

	template = loader.get_template('movie_review.html')

	return HttpResponse(template.render(context, request))

# Yorumu silme işlemi
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    # Yorumu sadece sahibi silebilir
    if request.user == comment.user:
        comment.delete()

    return HttpResponseRedirect(reverse('user-review', args=[comment.review.user.username, comment.review.movie.imdbID]))

# Beğenme işlemi
def like(request, username, imdb_id):
    user_liking = request.user
    user_review = get_object_or_404(User, username=username)
    movie = Movie.objects.get(imdbID=imdb_id)
    review = Review.objects.get(user=user_review, movie=movie)
    current_likes = review.likes

    liked = Likes.objects.filter(user=user_liking, review=review, type_like=1).count()  # type_like 1 olanlar beğenme işlemi için

    if not liked:
        like = Likes.objects.create(user=user_liking, review=review, type_like=1)
        current_likes = current_likes + 1
    else:
        Likes.objects.filter(user=user_liking, review=review, type_like=1).delete()
        current_likes = current_likes - 1

    review.likes = current_likes
    review.save()

    return HttpResponseRedirect(reverse('user-review', args=[username, imdb_id]))

# Beğenmeme işlemi
def unlike(request, username, imdb_id):
    user_unliking = request.user
    user_review = get_object_or_404(User, username=username)
    movie = Movie.objects.get(imdbID=imdb_id)
    review = Review.objects.get(user=user_review, movie=movie)
    current_unlikes = review.unlikes

    unliked = Likes.objects.filter(user=user_unliking, review=review, type_like=2).count()  # type_like 2 olanlar beğenmeme işlemi için

    if not unliked:
        unlike = Likes.objects.create(user=user_unliking, review=review, type_like=2)
        current_unlikes = current_unlikes + 1
    else:
        Likes.objects.filter(user=user_unliking, review=review, type_like=2).delete()
        current_unlikes = current_unlikes - 1

    review.unlikes = current_unlikes
    review.save()

    return HttpResponseRedirect(reverse('user-review', args=[username, imdb_id]))






