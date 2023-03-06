from math import sqrt
from django.shortcuts import render
from django.http import HttpResponse
import requests
from django import forms
import json
from colorthief import ColorThief
import urllib.request
import os
from PIL import Image


# Forms
class NewSearchForm(forms.Form):
    search = forms.CharField(label='', widget=forms.TextInput(
        attrs={'class': 'my-field-class', 'placeholder': 'Search'}))


# API key
API = '0fd7a8764e6522629a3b7e78c452c348'

# Views


def homepage(request):
    response = requests.get(
        f'https://api.themoviedb.org/3/search/movie?api_key={API}&language=en-US&query=Halloween&page=1&include_adult=false')


def index(request):
    response = requests.get(
        'https://api.themoviedb.org/3/trending/all/week?api_key=0fd7a8764e6522629a3b7e78c452c348'
    )

    trending = response.json()['results']

    context = {
        'trending': trending,
        'search_bar': NewSearchForm(),
    }
    return render(request, 'index.html', context)


def movies(request):
    # Pull data from third party rest api
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/popular?api_key=0fd7a8764e6522629a3b7e78c452c348&language=en-US&page=1')

    # Convert response data into json
    movies = response.json()['results']

    context = {
        'movies': movies,
        'search_bar': NewSearchForm(),
    }

    return render(request, 'movies.html', context)


def movie(request, movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=0fd7a8764e6522629a3b7e78c452c348&language=en-US&append_to_response=credits,watch/providers')

    # Convert response data into json
    movie = response.json()

    # Get movie backdrop
    # response = requests.get(
    #     f'https://api.themoviedb.org/3/movie/{movie_id}/images?api_key={API}'
    # )
    # backdrop = response.json()['backdrops'][0]

    # Get movie videos
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API}'
    )

    videos = response.json()['results']

    # Filter videos for trailers
    trailers = [video for video in videos if video['type'] == 'Trailer']

    # TODO: fix bug for no trailer
    key = trailers[0]['key']
    t = 'https://www.youtube.com/watch?v=' + key

    # URL of the image you want to get the dominant color of
    image_url = movie['poster_path']
    image_url = f'http://image.tmdb.org/t/p/w500{image_url}'

    # Download the image and save it locally
    urllib.request.urlretrieve(image_url, "temp_image.jpg")

    # Get the dominant color of the image using ColorThief
    color_thief = ColorThief("temp_image.jpg")
    average_color = color_thief.get_color(quality=1)

    # Unpack the average color tuple into separate red, green, and blue values

    # Get streaming services movie is available on
    if 'US' in movie['watch/providers']['results'] and \
            movie['watch/providers']['results']['US'].get('flatrate'):
        streaming_services = movie['watch/providers']['results']['US']['flatrate']
    else:
        streaming_services = None  # or some other default value

    red, green, blue = average_color
    # Calculate the luminance value of the color
    luminance = sqrt(0.299 * red**2 + 0.587 * green**2 + 0.114 * blue**2)
    print(f'red:{red}  green:{green}  blue{blue}')
    print(f'lum: {luminance}')

    # Set the luminosity threshold based on the luminance value
    # Set a minimum luminance threshold dynamically based on the actual luminance value
    min_luminance = 60
    max_luminance = 120

    # Darken the image if its luminance is below the threshold
    if luminance > max_luminance:
        # Calculate the amount to darken the image by (adjust as needed)
        darkness = max_luminance / luminance
        red = max(0, int(red * darkness))
        green = max(0, int(green * darkness))
        blue = max(0, int(blue * darkness))

    if luminance < min_luminance:
        # Calculate the amount to darken the image by (adjust as needed)
        darkness = min_luminance / luminance
        red = max(0, int(red * darkness))
        green = max(0, int(green * darkness))
        blue = max(0, int(blue * darkness))

    # Delete the temporary image file
    os.remove("temp_image.jpg")

    # Get review score
    review = round(float(movie['vote_average']), 1)

    print(f'red:{red}  green:{green}  blue{blue}')
    luminance = sqrt(0.299 * red**2 + 0.587 * green**2 + 0.114 * blue**2)
    print(f'lum: {luminance}')
    # Pass elements to view

    #TODO get highest r g b from avg color and increase!!

    context = {
        'movie': movie,
        'key': key,
        "r": str(red*.7),
        "g": str(green*.7),
        "b": str(blue*.7),
        'streaming_services': streaming_services,
        'review': review,
    }

    return render(request, 'movie.html', context)


def shows(request):

    response = requests.get(
        f'https://api.themoviedb.org/3/trending/tv/week?api_key=0fd7a8764e6522629a3b7e78c452c348'
    )

    # Convert response data into json
    shows = response.json()['results']

    context = {
        'shows': shows,
    }

    return render(request, 'shows.html', context)


def show(request, show_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}?api_key=0fd7a8764e6522629a3b7e78c452c348&language=en-US&append_to_response=seasons&append_to_response=episodes')

    # Convert response data into json
    show = response.json()

    # URL of the image you want to get the dominant color of
    image_url = show['poster_path']
    image_url = f'http://image.tmdb.org/t/p/w500{image_url}'

    # Download the image and save it locally
    urllib.request.urlretrieve(image_url, "temp_image.jpg")

    # Get the dominant color of the image using ColorThief
    color_thief = ColorThief("temp_image.jpg")
    average_color = color_thief.get_color(quality=1)

    # Unpack the average color tuple into separate red, green, and blue values
    red, green, blue = average_color

    # Delete the temporary image file
    os.remove("temp_image.jpg")

    # Print the dominant color

    context = {
        'show': show,
        "r": str(red),
        "g": str(green),
        "b": str(blue),
    }

    return render(request, 'show.html', context)


def season(request, show_id, season_number):
    response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}/season/{season_number}?api_key={API}&language=en-US')

    season = response.json()

    context = {
        'season': season,
        'show_id': show_id,
        'season_number': season_number
    }

    return render(request, 'season.html', context)


def episode(request, show_id, season_number, episode_number):
    response = requests.get(
        f'https://api.themoviedb.org/3/tv/{show_id}/season/{season_number}/episode/{episode_number}?api_key={API}&language=en-US'
    )
    episode = response.json()

    # TODO get show name using append
    context = {
        'episode': episode,
    }

    return render(request, 'episode.html', context)


def search(request):
    if request.method == 'POST':
        form = NewSearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']

            response = requests.get(
                f'https://api.themoviedb.org/3/search/multi?api_key={API}&language=en-US&query={search}&page=1&include_adult=false')

            search_results = response.json()['results']

            # Loop through movies and extract release year
            # release_years = []
            # for movie in movies:
            #     release_date = movie['release_date']
            #     release_year = release_date[:4]
            #     release_years.append(release_year)

            context = {
                'search_results': search_results,
                'search_bar': NewSearchForm(),
                # 'release_years': release_years
            }
            return render(request, 'search.html', context)


def actors(request):

    response = requests.get(
        f'https://api.themoviedb.org/3/trending/person/week?api_key={API}'
    )

    # Convert response data into json
    actors = response.json()['results']

    context = {
        'actors': actors
    }

    return render(request, 'actors.html', context)


def actor(request, actor_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/person/{actor_id}?api_key={API}&language=en-US')

    # Convert response data into json
    actor = response.json()

    context = {
        'actor': actor,
    }

    return render(request, 'actor.html', context)
