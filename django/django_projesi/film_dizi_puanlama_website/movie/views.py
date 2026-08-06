from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Avg
from django.conf import settings

from movie.models import Movie, Genre, Rating, Review
from actor.models import Actor
from authy.models import Profile
from django.contrib.auth.models import User

from movie.forms import RateForm

import requests


def fetch_omdb(**params):
    """Fetch OMDb data without exposing credentials in source code."""
    if not settings.OMDB_API_KEY:
        return {'Response': 'False', 'Error': 'OMDb API key is not configured.'}

    try:
        response = requests.get(
            'https://www.omdbapi.com/',
            params={'apikey': settings.OMDB_API_KEY, **params},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return {'Response': 'False', 'Error': 'Movie service is temporarily unavailable.'}


# Create your views here.
# Anasayfa ve arama işlemleri
def index(request):
    query = request.GET.get('q')

    if query:
        movie_data = fetch_omdb(s=query)

        context = {
            'query' : query,
            'movie_data' : movie_data,
            'page_number' : 1,
        }

        template = loader.get_template('search_results.html')

        return HttpResponse(template.render(context, request))
    
    return render(request, 'index.html')

# Sayfalama işlemleri
def pagination(request, query, page_number):
    movie_data = fetch_omdb(s=query, page=str(page_number))
    page_number = int(page_number) + 1

    context = {
        'query' : query,
        'movie_data' : movie_data,
        'page_number' : page_number,
    }

    template = loader.get_template('search_results.html')

    return HttpResponse(template.render(context, request))

# Film detayları ve veritabanına kaydetme işlemleri
def movieDetails(request, imdb_id):

    # Eğer film veritabanında varsa
    if Movie.objects.filter(imdbID=imdb_id).exists():
        movie_data = Movie.objects.get(imdbID=imdb_id) # Film veritabanından alınır
        reviews = Review.objects.filter(movie=movie_data)  # Film için kaydedilmiş incelemeler alınır
        reviews_avg = reviews.aggregate(Avg('rate')) # İncelemelerin ortalama puanı hesaplanır
        reviews_count = reviews.count() # Toplam inceleme sayısı hesaplanır
        other_users = User.objects.exclude(id=request.user.id) # Diğer kullanıcılar
        our_db = True # Veritabanında bulunduğu için bu film bizim veritabanımızda var

        # Context oluşturulur, burada şablonlara veri aktarılır
        context = {
            'movie_data': movie_data,
            'reviews': reviews,
            'reviews_avg': reviews_avg,
            'reviews_count': reviews_count,
            'other_users': other_users,
            'our_db': our_db,
        }
    
    else:
        # Eğer film veritabanında yoksa OMDB API den film verileri çekilir
        movie_data = fetch_omdb(i=imdb_id)
        if movie_data.get('Response') == 'False':
            return render(request, 'movie_details.html', {
                'movie_data': movie_data,
                'our_db': False,
            }, status=503 if 'temporarily' in movie_data.get('Error', '') else 404)

        # Veritabanına eklenecek veri nesneleri
        rating_objs = []
        genre_objs = []
        actor_objs = []

        # Actorler için
        actor_list = [x.strip() for x in movie_data['Actors'].split(',')]
        for actor in actor_list:
            a, created = Actor.objects.get_or_create(name=actor)
            actor_objs.append(a)
        
        # Genre ve türler için
        genre_list = list(movie_data['Genre'].replace(" ", "").split(','))
        for genre in genre_list:
            genre_slug = slugify(genre)
            g, created = Genre.objects.get_or_create(title=genre, slug=genre_slug)
            genre_objs.append(g)
        
        # Rate için
        for rate in movie_data['Ratings']:
            r, created = Rating.objects.get_or_create(source=rate['Source'], rating=rate['Value'])
            rating_objs.append(r)

        # Film detayları veritabanına ekleniyor
        if movie_data['Type'] == 'movie':
            m, created = Movie.objects.get_or_create(
                Title=movie_data['Title'],
                Year=movie_data['Year'],
                Rated=movie_data['Rated'],
                Released=movie_data['Released'],
                Runtime=movie_data['Runtime'],
                Director=movie_data['Director'],
                Writer=movie_data['Writer'],
                Plot=movie_data['Plot'],
                Language=movie_data['Language'],
                Country=movie_data['Country'],
                Awards=movie_data['Awards'],
                Poster_url=movie_data['Poster'],
                Metascore=movie_data['Metascore'],
                imdbRating=movie_data['imdbRating'],
                imdbVotes=movie_data['imdbVotes'],
                imdbID=movie_data['imdbID'],
                Type=movie_data['Type'],
                DVD=movie_data['DVD'],
                BoxOffice=movie_data['BoxOffice'],
                Production=movie_data['Production'],
                Website=movie_data['Website'],
                )
            m.Genre.set(genre_objs)
            m.Actors.set(actor_objs)
            m.Ratings.set(rating_objs)

        else:
            m, created = Movie.objects.get_or_create(
                Title=movie_data['Title'],
                Year=movie_data['Year'],
                Rated=movie_data['Rated'],
                Released=movie_data['Released'],
                Runtime=movie_data['Runtime'],
                Director=movie_data['Director'],
                Writer=movie_data['Writer'],
                Plot=movie_data['Plot'],
                Language=movie_data['Language'],
                Country=movie_data['Country'],
                Awards=movie_data['Awards'],
                Poster_url=movie_data['Poster'],
                Metascore=movie_data['Metascore'],
                imdbRating=movie_data['imdbRating'],
                imdbVotes=movie_data['imdbVotes'],
                imdbID=movie_data['imdbID'],
                Type=movie_data['Type'],
                totalSeasons=movie_data['totalSeasons'],
                )
            m.Genre.set(genre_objs)
            m.Actors.set(actor_objs)
            m.Ratings.set(rating_objs)

        
        for actor in actor_objs:
            actor.movies.add(m)
            actor.save()

        m.save()
        our_db = False

        context = {
            'movie_data': movie_data,
            'our_db': our_db,
        }

    template = loader.get_template('movie_details.html')

    return HttpResponse(template.render(context, request))


# Türlere göre film listeleme ve sayfalama
def genres(request, genre_slug):
    genre = get_object_or_404(Genre, slug=genre_slug)
    movies = Movie.objects.filter(Genre=genre)

    # Sayfalama
    paginator = Paginator(movies, 9)
    page_number = request.GET.get('page')
    movie_data = paginator.get_page(page_number)

    context = {
        'movie_data' : movie_data,
        'genre' : genre,
    }


    template = loader.get_template('genre.html')

    return HttpResponse(template.render(context, request))

# Kullanıcının izleme listesine film ekleme/çıkarma
def addMoviesToWatch(request, imdb_id):
    movie = Movie.objects.get(imdbID=imdb_id)
    user = request.user
    profile = Profile.objects.get(user=user)

    if profile.to_watch.filter(imdbID=imdb_id).exists():
        # Kullanıcı filmi izleme listesinden çıkarmak
        profile.to_watch.remove(movie)
    else:
        # Kullanıcı filmi izleme listesine eklemek
        profile.to_watch.add(movie)

    return HttpResponseRedirect(reverse('movie-details', args=[imdb_id]))


# Kullanıcının izlediği filmleri ekleme/çıkarma
def addMoviesWatched(request, imdb_id):
    movie = Movie.objects.get(imdbID=imdb_id)
    user = request.user
    profile = Profile.objects.get(user=user)

    if profile.watched.filter(imdbID=imdb_id).exists():
        # Kullanıcı filmi izlediği listeden çıkarmak
        profile.watched.remove(movie)
    else:
        # Kullanıcı filmi izlediği listeye eklemek
        if profile.to_watch.filter(imdbID=imdb_id).exists():
            profile.to_watch.remove(movie)
        profile.watched.add(movie)

    return HttpResponseRedirect(reverse('movie-details', args=[imdb_id]))


# Film puanlama ve inceleme yazma
def Rate(request, imdb_id):
    movie = Movie.objects.get(imdbID=imdb_id)
    user = request.user
    existing_review = Review.objects.filter(user=user, movie=movie).first()

    if request.method == 'POST':
        form = RateForm(request.POST, instance=existing_review)
        if form.is_valid():
            if existing_review:
                # Kullanıcı daha önce bir inceleme yazmışsa, bu incelemeyi güncelle
                existing_review.rate = form.cleaned_data['rate']
                existing_review.save()
            else:
                # Kullanıcı daha önce bir inceleme yazmamışsa, yeni bir inceleme oluştur
                rate = form.save(commit=False)
                rate.user = user
                rate.movie = movie
                rate.save()
            return HttpResponseRedirect(reverse('movie-details', args=[imdb_id]))
    else:
        form = RateForm(instance=existing_review)

    template = loader.get_template('rate.html')

    context = {
        'form': form,
        'movie': movie,
    }

    return HttpResponse(template.render(context, request))

