# MoviWeb App

MoviWeb App is a Flask-based web application for managing user and admin accounts, movies, and user interactions. It features role-based access control, caching, and a contact form. The application uses SQLite for data storage.

## Features

- **User and Admin Registration**: Separate signup routes for users and admins.
- **Login and Logout**: Unified login route with role-based redirection and session management.
- **Cache Management**: Simple in-memory cache configuration for development.
- **Contact Form**: Allows users to send messages to support.
- **Movie Management**: Admins can add, edit, delete, and manage movies.
- **Favorites Management**: Users can manage their favorite movies.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Vrana710/MoviWeb_App.git
   cd MoviWeb_App
   ```

2. **Create a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database:**

   ```bash
   flask db upgrade
   ```

## Configuration

- **Database**: Uses SQLite. The database file is located in the `db` directory.
- **Secret Key**: Set in the Flask app configuration for session management.
- **Cache**: Configured with a simple in-memory cache for development.

## Running the Application

To start the Flask development server:

```bash
python3 app.py  
or
flask run
```

The application will be available at `http://127.0.0.1:5000`.

## Routes

### User Routes

- **Home (`/`)**: Displays the home page.
- **About (`/about`)**: Displays information about the application.
- **Favorites (`/favorites`)**: Shows a list of favorite movies.
- **Movies (`/movies`)**: Lists available movies.
- **Contact (`/contact`)**: Provides a form for users to send messages.
- **Signup User (`/signup_user`)**: User registration form.
- **Login (`/login`)**: Login page for both users and admins.
- **Logout (`/logout`)**: Logs out the current user or admin.
- **Dashboard (`/dashboard`)**: Displays the user dashboard with latest movies.
- **My Movies (`/my_movies`)**: Lists movies that are not in the user's favorites.
- **User Favorites (`/user_favorites`)**: Lists favorite movies of the user.
- **Add to Favorites (`/add_to_favorites/<int:movie_id>`)**: Adds a movie to the user's favorites.
- **Remove from Favorites (`/remove_from_favorites/<int:movie_id>`)**: Removes a movie from the user's favorites.
- **Add Movie (`/user_add_movie`)**: Form to add a new movie (for users).
- **User Profile (`/user_profile`)**: Displays user profile information.

### Admin Routes

- **Admin Dashboard (`/admin_dashboard`)**: Displays the admin dashboard.
- **Add User (`/add_user`)**: Form to register a new user.
- **Edit User (`/edit_user/<int:user_id>`)**: Form to edit user details.
- **Delete User (`/delete_user/<int:user_id>`)**: Deletes a user.
- **Manage Users (`/manage_users`)**: Lists all users.
- **Add Movie (`/add_movie`)**: Form to add a new movie.
- **Edit Movie (`/edit_movie/<int:movie_id>`)**: Form to edit movie details.
- **Delete Movie (`/delete_movie/<int:movie_id>`)**: Deletes a movie.
- **Manage Movies (`/manage_movies`)**: Lists all movies.
- **Reports (`/reports`)**: Displays user and movie count reports.

## API Endpoints

### Admin API

- **`/admin_dashboard`**: GET - View the admin dashboard.
- **`/add_user`**: POST - Register a new user.
- **`/edit_user/<int:user_id>`**: POST - Update user details.
- **`/delete_user/<int:user_id>`**: POST - Delete a user.
- **`/manage_users`**: GET - List all users.
- **`/add_movie`**: POST - Add a new movie to the database.
- **`/edit_movie/<int:movie_id>`**: POST - Update movie details.
- **`/delete_movie/<int:movie_id>`**: POST - Delete a movie.
- **`/manage_movies`**: GET - List all movies.
- **`/reports`**: GET - View user and movie count reports.

### User API

- **`/dashboard`**: GET - View the user dashboard with the latest movies.
- **`/my_movies`**: GET - List movies not in the user's favorites.
- **`/user_favorites`**: GET - List favorite movies of the user.
- **`/add_to_favorites/<int:movie_id>`**: POST - Add a movie to the user's favorites.
- **`/remove_from_favorites/<int:movie_id>`**: POST - Remove a movie from the user's favorites.
- **`/user_add_movie`**: GET, POST - Add a new movie (for users).
- **`/user_profile`**: GET - View the user's profile information.


## Development

- **Cache**: Configured with a simple in-memory cache for development purposes.
- **Logging**: Basic logging configuration is set up for debugging.

## Credits

The application uses the "Forty" template by HTML5 UP. 

- **Template**: Forty by HTML5 UP
- **Website**: [html5up.net](https://html5up.net)
- **License**: Free for personal and commercial use under the CCA 3.0 license ([html5up.net/license](https://html5up.net/license))
- **Author**: @ajlkn

## Demo

Watch the demo video of the MoviWeb App [here](https://github.com/Vrana710/MoviWeb_App/blob/main/assets/video/Demo.mp4).
Watch the demo video ![Demo](./assets/video/Demo.mp4)


Note: Due to file size limitations, the video may need to be downloaded to view it properly.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or suggestions, feel free to contact me at [ranavarsha710@gmail.com](mailto:ranavarsha710@gmail.com).
