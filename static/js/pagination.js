document.addEventListener('DOMContentLoaded', () => {

     // Handle pagination for Reports
    const paginationContainerReports = document.querySelector('#pagination-container-reports');
    if (paginationContainerReports) {
        paginationContainerReports.addEventListener('click', async (event) => {
            if (event.target.classList.contains('page-link')) {
                event.preventDefault();
                const href = event.target.getAttribute('href');
                const response = await fetch(href);
                if (response.ok) {
                    const data = await response.text();
                    document.querySelector('#main').innerHTML = data;
                } else {
                    console.error('Failed to load page');
                }
            }
        });
    }
    // Handle pagination for dashboard
    const paginationContainerDashboard = document.querySelector('#pagination-container-dashboard');
    if (paginationContainerDashboard) {
        paginationContainerDashboard.addEventListener('click', async (event) => {
            if (event.target.classList.contains('page-link')) {
                event.preventDefault();
                const href = event.target.getAttribute('href');
                const response = await fetch(href);
                if (response.ok) {
                    const data = await response.text();
                    document.querySelector('#main').innerHTML = data;
                } else {
                    console.error('Failed to load page');
                }
            }
        });
    }

    // Handle pagination for users
    const userPaginationContainer = document.querySelector('#pagination-container-users');
    if (userPaginationContainer) {
        userPaginationContainer.addEventListener('click', async (event) => {
            if (event.target.classList.contains('page-link')) {
                event.preventDefault();
                const href = event.target.getAttribute('href');
                const response = await fetch(href);
                if (response.ok) {
                    const data = await response.text();
                    document.querySelector('#main').innerHTML = data;
                } else {
                    console.error('Failed to load page');
                }
            }
        });
    }

      // Handle pagination for movies
    const moviePaginationContainer = document.querySelector('#pagination-container-movies');
    if (moviePaginationContainer) {
        moviePaginationContainer.addEventListener('click', async (event) => {
            if (event.target.classList.contains('page-link')) {
                event.preventDefault();
                const href = event.target.getAttribute('href');
                const response = await fetch(href);
                if (response.ok) {
                    const data = await response.text();
                    document.querySelector('#main').innerHTML = data;
                } else {
                    console.error('Failed to load page');
                }
            }
        });
    }

    // Handle pagination for my movies (users)
    const paginationContainerMymovies = document.querySelector('#pagination-container-my-movies');
    if (paginationContainerMymovies) {
        paginationContainerMymovies.addEventListener('click', async (event) => {
            if (event.target.classList.contains('page-link')) {
                event.preventDefault();
                const href = event.target.getAttribute('href');
                const response = await fetch(href);
                if (response.ok) {
                    const data = await response.text();
                    document.querySelector('#main').innerHTML = data;
                } else {
                    console.error('Failed to load page');
                }
            }
        });
    }

    // Handle pagination for user favorites movies
    const paginationContainerUserFavoritesMovies = document.querySelector('#pagination-container-user-favorites');
    if (paginationContainerUserFavoritesMovies) {
        paginationContainerUserFavoritesMovies.addEventListener('click', async (event) => {
            if (event.target.classList.contains('page-link')) {
                event.preventDefault();
                const href = event.target.getAttribute('href');
                const response = await fetch(href);
                if (response.ok) {
                    const data = await response.text();
                    document.querySelector('#main').innerHTML = data;
                } else {
                    console.error('Failed to load page');
                }
            }
        });
    }

    // Handle pagination for movie web app movies list
    const paginationContainerWebAppMovies = document.querySelector('#pagination-container-movies-web-app');
    if (paginationContainerWebAppMovies) {
        paginationContainerWebAppMovies.addEventListener('click', async (event) => {
            if (event.target.classList.contains('page-link')) {
                event.preventDefault();
                const href = event.target.getAttribute('href');
                const response = await fetch(href);
                if (response.ok) {
                    const data = await response.text();
                    document.querySelector('#main').innerHTML = data;
                } else {
                    console.error('Failed to load page');
                }
            }
        });
    }
});

