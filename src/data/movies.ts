import { Movie } from '../types/movie';

// Popular movies for initial onboarding when backend is not available
export const mockOnboardingMovies: Movie[] = [
  {
    movieId: 550,
    title: "Fight Club",
    poster_path: "https://image.tmdb.org/t/p/w185/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
    overview: "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy.",
    genres: "Drama",
    release_date: "1999-10-15"
  },
  {
    movieId: 13,
    title: "Forrest Gump",
    poster_path: "https://image.tmdb.org/t/p/w185/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",
    overview: "A man with a low IQ has accomplished great things in his life and been present during significant historic events.",
    genres: "Drama, Romance",
    release_date: "1994-06-23"
  },
  {
    movieId: 278,
    title: "The Shawshank Redemption",
    poster_path: "https://image.tmdb.org/t/p/w185/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
    overview: "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
    genres: "Drama",
    release_date: "1994-09-23"
  },
  {
    movieId: 238,
    title: "The Godfather",
    poster_path: "https://image.tmdb.org/t/p/w185/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
    overview: "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
    genres: "Drama, Crime",
    release_date: "1972-03-14"
  },
  {
    movieId: 424,
    title: "Schindler's List",
    poster_path: "https://image.tmdb.org/t/p/w185/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg",
    overview: "In German-occupied Poland during World War II, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce.",
    genres: "Drama, History, War",
    release_date: "1993-11-30"
  }
];

// Helper function to convert API movie to internal format
export function normalizeMovie(apiMovie: any): Movie {
  return {
    movieId: apiMovie.movieId,
    title: apiMovie.title,
    poster_path: apiMovie.poster_path,
    overview: apiMovie.overview,
    genres: apiMovie.genres,
    release_date: apiMovie.release_date
  };
}
