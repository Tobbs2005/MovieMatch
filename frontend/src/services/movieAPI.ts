const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class MovieAPI {
  private static async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`API request failed: ${response.status} ${response.statusText}`, errorText);
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }

      return response.json();
    } catch (error) {
      console.error(`Network error for ${url}:`, error);
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error(`Cannot connect to backend at ${url}. Please ensure the backend is running.`);
      }
      throw error;
    }
  }

  static async getRecommendation(request: {
    user_vector?: number[] | null;
    seen_ids: number[];
    liked_ids: number[];
    genre?: string | null;
    language?: string | null;
    year_start?: number | null;
    year_end?: number | null;
    adult?: boolean | null;
  }) {
    return this.request<{
      movie?: {
        movieId: number;
        title: string;
        genres: string;
        overview: string;
        release_date: string;
        poster_path: string;
      };
      user_vector?: number[] | null;
      error?: string;
    }>('/recommend', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  static async submitFeedback(request: {
    user_vector?: number[] | null;
    movie_id: number;
    feedback: string;
  }) {
    return this.request<{
      user_vector?: number[] | null;
    }>('/feedback', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  static async searchMovies(request: {
    query: string;
    genre?: string | null;
    language?: string | null;
    year_start?: number | null;
    year_end?: number | null;
    adult?: boolean | null;
  }) {
    return this.request<{
      movies: {
        title: string;
        overview: string;
        genres: string;
        release_date: string;
        poster_path: string;
        movieId: number;
      }[];
      search_time_ms?: number; // Optional timing information for debugging
    }>('/search', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }
}
