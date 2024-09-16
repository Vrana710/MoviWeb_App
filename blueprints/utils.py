import requests

OMDB_API_KEY = "fd6cbe7a"


def _fetch_movie_data(title):
    try:
        response = requests.get(
            f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}")
        if response.status_code == 200:
            data = response.json()
            if data['Response'] == 'True':
                print(data)
                return data
            else:
                print(f"Error: {data['Error']}")
        else:
            print("Error: Could not retrieve data from OMDb API.")
    except requests.RequestException as e:
        print(f"Error: {e}")
    return None
