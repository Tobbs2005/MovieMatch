export interface Movie {
  movieId: number;
  title: string;
  poster_path: string;
  overview: string;
  genres: string;
  release_date: string;
}

export interface MovieWithDetails extends Movie {
  rating?: number;
  year?: number;
  genre?: string[];
  duration?: number;
  language?: string;
}

export interface UserMovieList {
  liked: Movie[];
  saved: Movie[];
  disliked: Movie[];
}

export interface RecommendationRequest {
  user_vector?: number[] | null;
  seen_ids: number[];
  liked_ids: number[];
  genre?: string | null;
  language?: string | null;
  year_start?: number | null;
  year_end?: number | null;
  adult?: boolean | null;
}

export interface RecommendationResponse {
  movie?: Movie;
  user_vector?: number[] | null;
  error?: string;
}

export interface SearchRequest {
  query: string;
  genre?: string | null;
  language?: string | null;
  year_start?: number | null;
  year_end?: number | null;
  adult?: boolean | null;
}

export interface SearchResponse {
  movies: Movie[];
}