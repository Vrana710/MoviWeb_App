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
// Handle pagination for dashboard -all-users-movies
    const paginationContainerDashboardAllUsersMovies = document.querySelector('#pagination-container-dashboard-all-users-movies');
    if (paginationContainerDashboardAllUsersMovies) {
        paginationContainerDashboardAllUsersMovies.addEventListener('click', async (event) => {
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

     // Handle pagination for movies-details-added-by-user-of-current-admin
    const paginationContainerMoviesAddedByUserOfCurrentAdmin = document.querySelector('#pagination-container-all-movies-added-by-user-of-current-admin-report');
    if (paginationContainerMoviesAddedByUserOfCurrentAdmin) {
        paginationContainerMoviesAddedByUserOfCurrentAdmin.addEventListener('click', async (event) => {
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

     // Handle pagination for movies-added-by-user-of-current-admin
    const paginationContainerMoviesAddedByAllUser = document.querySelector('#pagination-container-all-movies-added-by-all-user-of-report');
    if (paginationContainerMoviesAddedByAllUser) {
        paginationContainerMoviesAddedByAllUser.addEventListener('click', async (event) => {
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

    // Handle pagination for movies-details-added-by-user-of-current-admin
    const paginationContainerMoviesDetailsAddedByUserOfCurrentAdmin = document.querySelector('#pagination-container-movies-details-added-by-user-of-current-admin');
    if (paginationContainerMoviesDetailsAddedByUserOfCurrentAdmin) {
        paginationContainerMoviesDetailsAddedByUserOfCurrentAdmin.addEventListener('click', async (event) => {
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

     // Handle pagination for -manage-all-movies
    const paginationContainerManageAllMovies = document.querySelector('#pagination-container-manage-all-movies');
    if (paginationContainerManageAllMovies) {
        paginationContainerManageAllMovies.addEventListener('click', async (event) => {
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

    // Handle pagination for -manage-all-users
    const paginationContainerManageAllUsers = document.querySelector('#pagination-container-manage-all-users');
    if (paginationContainerManageAllUsers) {
        paginationContainerManageAllUsers.addEventListener('click', async (event) => {
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

