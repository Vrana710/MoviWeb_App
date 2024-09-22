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


def _fetch_movie_data(title):
    """
    Fetches movie data from the OMDb API using the provided movie title.

    Parameters:
    title (str): The title of the movie to fetch data for.

    Returns:
    dict: A dictionary containing the movie data
          if the request is successful and the movie exists.
          If the movie does not exist or
          an error occurs during the request, returns None.
          The dictionary will contain the following keys: 'Title',
          'Year', 'Rated', 'Released', 'Runtime', 'Genre',
          'Director', 'Writer', 'Actors', 'Plot', 'Language',
          'Country', 'Awards', 'Ratings', 'Metascore', 'imdbRating',
          'imdbVotes', 'imdbID', 'Type', 'DVD', 'BoxOffice',
          'Production', 'Website'.
    """
    try:
        response = requests.get(
            f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}", timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data['Response'] == 'True':
                print(data)
                return data
            print(f"Error: {data['Error']}")
        print("Error: Could not retrieve data from OMDb API.")
    except requests.RequestException as e:
        print(f"Error: {e}")
    return None
