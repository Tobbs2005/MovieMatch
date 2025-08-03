'use client';

import { useState, useEffect, useCallback } from 'react';
import { MovieCard } from './MovieCard';
import { SwipeControls } from './SwipeControls';
import { MovieLists } from './MovieLists';
import { IntroScreen } from './IntroScreen';
import { Filters, FilterState } from './Filters';
import { ThemeToggle } from './ThemeToggle';
import { Button } from './ui/button';
import { Toaster } from './ui/sonner';
import { MovieAPI } from '../services/movieAPI';
import { mockOnboardingMovies } from '../data/movies';
import { Movie, UserMovieList } from '../types/movie';
import { Home, List, Shuffle, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

type View = 'intro' | 'swipe' | 'lists';

export default function MovieMatchApp() {
  const [currentView, setCurrentView] = useState<View>('intro');
  const [currentMovie, setCurrentMovie] = useState<Movie | null>(null);
  const [userLists, setUserLists] = useState<UserMovieList>({
    liked: [],
    saved: [],
    disliked: []
  });
  const [userVector, setUserVector] = useState<number[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);

  // Filter state
  const [filters, setFilters] = useState<FilterState>({
    genres: [],
    languages: [],
    yearRange: [1990, 2024]
  });

  // Available genres and languages (will be populated from backend or predefined)
  const availableGenres = [
    'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary',
    'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Mystery',
    'Romance', 'Science Fiction', 'TV Movie', 'Thriller', 'War', 'Western'
  ];

  const availableLanguages = [
    'en', 'es', 'fr', 'de', 'it', 'ja', 'ko', 'zh', 'hi', 'ar', 'pt', 'ru'
  ];

  const movieYearRange: [number, number] = [1900, 2024];

  // Get all movie IDs that have been seen
  const getAllSeenIds = useCallback(() => {
    const allMovies = [...userLists.liked, ...userLists.saved, ...userLists.disliked];
    return allMovies.map(movie => movie.movieId);
  }, [userLists]);

  // Get liked movie IDs
  const getLikedIds = useCallback(() => {
    return userLists.liked.map(movie => movie.movieId);
  }, [userLists.liked]);

  // Fetch next movie recommendation
  const fetchNextMovie = useCallback(async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    try {
      const seenIds = getAllSeenIds();
      const likedIds = getLikedIds();

      // Build filter object
      const filterObj: any = {};
      if (filters.genres.length > 0) {
        filterObj.genre = filters.genres[0]; // Use first selected genre
      }
      if (filters.languages.length > 0) {
        filterObj.language = filters.languages[0]; // Use first selected language
      }
      if (filters.yearRange[0] !== movieYearRange[0]) {
        filterObj.year_start = filters.yearRange[0];
      }
      if (filters.yearRange[1] !== movieYearRange[1]) {
        filterObj.year_end = filters.yearRange[1];
      }

      const response = await MovieAPI.getRecommendation({
        user_vector: userVector,
        seen_ids: seenIds,
        liked_ids: likedIds,
        ...filterObj
      });

      if (response.error) {
        toast.error(response.error);
        setCurrentMovie(null);
      } else if (response.movie) {
        const movie: Movie = {
          movieId: response.movie.movieId,
          title: response.movie.title,
          poster_path: response.movie.poster_path,
          overview: response.movie.overview,
          genres: response.movie.genres,
          release_date: response.movie.release_date
        };
        setCurrentMovie(movie);
        
        if (response.user_vector) {
          setUserVector(response.user_vector);
        }
      }
    } catch (error) {
      console.error('Error fetching recommendation:', error);
      toast.error('Failed to fetch movie recommendation. Using fallback.');
      
      // Fallback to mock data if API fails
      const seenIds = getAllSeenIds();
      const unseenMockMovies = mockOnboardingMovies.filter(
        movie => !seenIds.includes(movie.movieId)
      );
      
      if (unseenMockMovies.length > 0) {
        setCurrentMovie(unseenMockMovies[0]);
      } else {
        setCurrentMovie(null);
      }
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, getAllSeenIds, getLikedIds, filters, userVector]);

  // Fetch movie when filters change or when starting
  useEffect(() => {
    if (hasStarted && currentView === 'swipe') {
      fetchNextMovie();
    }
  }, [filters, hasStarted, currentView]);

  const handleStartSwiping = (preSelectedMovies: Movie[]) => {
    // Add pre-selected movies to liked list
    setUserLists(prev => ({
      ...prev,
      liked: [...prev.liked, ...preSelectedMovies]
    }));
    
    setCurrentView('swipe');
    setHasStarted(true);
  };

  const handleAction = async (action: 'like' | 'dislike' | 'skip' | 'save') => {
    if (!currentMovie) return;

    const newUserLists = { ...userLists };
    
    switch (action) {
      case 'like':
        newUserLists.liked = [...newUserLists.liked, currentMovie];
        break;
      case 'dislike':
        newUserLists.disliked = [...newUserLists.disliked, currentMovie];
        break;
      case 'save':
        newUserLists.saved = [...newUserLists.saved, currentMovie];
        break;
      case 'skip':
        // No action needed for skip
        break;
    }

    setUserLists(newUserLists);

    // Submit feedback to backend (except for skip and save)
    if (action === 'like' || action === 'dislike') {
      try {
        await MovieAPI.submitFeedback({
          user_vector: userVector,
          movie_id: currentMovie.movieId,
          feedback: action
        });
      } catch (error) {
        console.error('Error submitting feedback:', error);
      }
    }
    
    // Fetch next movie
    fetchNextMovie();
  };

  const handleMoveMovie = (movie: Movie, fromList: 'liked' | 'saved' | 'disliked', toList: 'liked' | 'saved' | 'disliked') => {
    setUserLists(prev => {
      const newLists = { ...prev };
      
      // Remove from source list
      newLists[fromList] = newLists[fromList].filter(m => m.movieId !== movie.movieId);
      
      // Add to target list (avoid duplicates)
      if (!newLists[toList].find(m => m.movieId === movie.movieId)) {
        newLists[toList] = [...newLists[toList], movie];
      }
      
      return newLists;
    });
  };

  const handleRemoveMovie = (movie: Movie, fromList: 'liked' | 'saved' | 'disliked') => {
    setUserLists(prev => ({
      ...prev,
      [fromList]: prev[fromList].filter(m => m.movieId !== movie.movieId)
    }));
  };

  const resetMovies = () => {
    setCurrentMovie(null);
    setUserVector(null);
    setFilters({
      genres: [],
      languages: [],
      yearRange: movieYearRange
    });
    fetchNextMovie();
  };

  // Don't show navigation on intro screen
  if (currentView === 'intro') {
    return <IntroScreen onStartSwiping={handleStartSwiping} />;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="sticky top-0 z-10 bg-background/80 backdrop-blur-sm border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                MovieMatch AI
              </h1>
            </div>
            
            <div className="flex items-center gap-4">
              <Button
                variant={currentView === 'swipe' ? 'default' : 'ghost'}
                onClick={() => setCurrentView('swipe')}
                className="flex items-center gap-2"
              >
                <Home className="w-4 h-4" />
                Discover
              </Button>
              
              <Button
                variant={currentView === 'lists' ? 'default' : 'ghost'}
                onClick={() => setCurrentView('lists')}
                className="flex items-center gap-2"
              >
                <List className="w-4 h-4" />
                My Lists ({userLists.liked.length + userLists.saved.length})
              </Button>

              <ThemeToggle />
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative">
        <AnimatePresence mode="wait">
          {currentView === 'swipe' && (
            <motion.div
              key="swipe"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
              className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] p-6"
            >
              {/* Filters */}
              <div className="w-full max-w-4xl mb-6">
                <Filters
                  filters={filters}
                  onFiltersChange={setFilters}
                  availableGenres={availableGenres}
                  availableLanguages={availableLanguages}
                  yearRange={movieYearRange}
                />
              </div>

              {isLoading ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin mb-4" />
                  <p className="text-muted-foreground">Finding your next favorite movie...</p>
                </div>
              ) : currentMovie ? (
                <>
                  <AnimatePresence mode="wait">
                    <MovieCard
                      key={currentMovie.movieId}
                      movie={currentMovie}
                      onAction={handleAction}
                    />
                  </AnimatePresence>
                  
                  <SwipeControls
                    onLike={() => handleAction('like')}
                    onDislike={() => handleAction('dislike')}
                    onSave={() => handleAction('save')}
                    onSkip={() => handleAction('skip')}
                  />
                  
                  <div className="mt-6 text-center">
                    <p className="text-muted-foreground">
                      AI-powered recommendations based on your taste
                    </p>
                    {userLists.liked.length >= 5 && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Learning from {userLists.liked.length} liked movies
                      </p>
                    )}
                  </div>
                </>
              ) : (
                <div className="text-center">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200, damping: 15 }}
                  >
                    <h3 className="text-3xl font-bold mb-4">No more movies available! 🎬</h3>
                    <p className="text-muted-foreground mb-6 text-lg">
                      Try adjusting your filters or explore different preferences.
                    </p>
                    <Button onClick={resetMovies} size="lg" className="flex items-center gap-2">
                      <Shuffle className="w-5 h-5" />
                      Reset & Discover More
                    </Button>
                  </motion.div>
                </div>
              )}
            </motion.div>
          )}

          {currentView === 'lists' && (
            <motion.div
              key="lists"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <MovieLists
                likedMovies={userLists.liked}
                savedMovies={userLists.saved}
                dislikedMovies={userLists.disliked}
                onMoveMovie={handleMoveMovie}
                onRemoveMovie={handleRemoveMovie}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
      
      <Toaster />
    </div>
  );
}
