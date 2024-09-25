"""
utils.py

This module contains utility functions for the application,
including helper functions for movie API.

Functions:
- _fetch_movie_data: Fetches movie data from the OMDb API
  using the provided movie title.
"""

import requests

OMDB_API_KEY = "fd6cbe7a"
TMDB_API_KEY = "133afb26e03c038b42568392feaad902"


def _fetch_movie_data(title):
    """
    Fetches movie data from the OMDb API using the provided movie title.
    Additionally, fetches the movie trailer from TMDb API.

    Parameters:
    title (str): The title of the movie to fetch data for.

    Returns:
    dict: A dictionary containing the movie data and trailer link.
    """
    try:
        # Fetch movie data from OMDb API
        response = requests.get(
            f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}", timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data['Response'] == 'True':
                imdb_id = data.get('imdbID')

                # Fetch trailer from TMDb API using the IMDb ID
                tmdb_response = requests.get(
                    f"https://api.themoviedb.org/3/movie/{imdb_id}/videos?api_key={TMDB_API_KEY}"
                )
                if tmdb_response.status_code == 200:
                    tmdb_data = tmdb_response.json()
                    trailers = tmdb_data.get('results', [])

                    # Find the YouTube trailer link
                    for trailer in trailers:
                        if trailer['site'] == 'YouTube' and trailer['type'] == 'Trailer':
                            trailer_link = f"https://www.youtube.com/watch?v={trailer['key']}"
                            data['Trailer'] = trailer_link
                            break
                return data
            print(f"Error: {data['Error']}")
        print("Error: Could not retrieve data from OMDb API.")
    except requests.RequestException as e:
        print(f"Error: {e}")
    return None

