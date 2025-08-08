'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { MovieCard } from './MovieCard';
import { SwipeControls } from './SwipeControls';
import { MovieLists } from './MovieLists';
import { IntroScreen } from './IntroScreen';
import { Filters, FilterState } from './Filters';
import { ThemeToggle } from './ThemeToggle';
import { Button } from './ui/button';
import { Toaster } from './ui/sonner';
import { MovieAPI } from '../services/movieAPI';
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
  const [isMobile, setIsMobile] = useState(false);
  
  // Ref to track recently fetched movies to prevent duplicates
  const recentlyFetchedIds = useRef<Set<number>>(new Set());
  const fetchTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const fetchAttemptCount = useRef<number>(0);
  const maxFetchAttempts = 5;

  // Detect if device is mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Filter state
  const [filters, setFilters] = useState<FilterState>({
    genres: [],
    languages: [],
    yearRange: [1990, 2024]
  });

  // Available genres and languages (will be populated from backend or predefined)
  const availableGenres = [
    'Action', 'Adventure', 'Animation', 'Comedy', 'Crime',
    'Drama', 'Family', 'Fantasy', 'Horror', 
    'Romance', 'Thriller'
  ];

  const availableLanguages = [
    'en', 'es', 'fr', 'de', 'it', 'ja', 'ko', 'zh',
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
    
    // Clear any pending fetch timeout
    if (fetchTimeoutRef.current) {
      clearTimeout(fetchTimeoutRef.current);
    }
    
    // Check if we've exceeded max attempts
    if (fetchAttemptCount.current >= maxFetchAttempts) {
      console.log('Max fetch attempts reached, clearing recent cache and resetting');
      recentlyFetchedIds.current.clear();
      fetchAttemptCount.current = 0;
      setCurrentMovie(null);
      setIsLoading(false);
      return;
    }
    
    setIsLoading(true);
    try {
      const seenIds = getAllSeenIds();
      const likedIds = getLikedIds();
      
      // Include recently fetched IDs to prevent API from returning the same movies
      const recentIds = Array.from(recentlyFetchedIds.current);
      const allExcludedIds = [...seenIds, ...recentIds];

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
        seen_ids: allExcludedIds, // Send both seen and recently fetched IDs
        liked_ids: likedIds,
        ...filterObj
      });

      if (response.error) {
        toast.error(response.error);
        setCurrentMovie(null);
        fetchAttemptCount.current = 0; // Reset on error
      } else if (response.movie) {
        // Double-check for duplicates (should be rare now that we send excluded IDs to API)
        const movieExists = allExcludedIds.includes(response.movie.movieId);
        
        if (movieExists) {
          console.log(`Unexpected duplicate movie detected (ID: ${response.movie.movieId}), attempt ${fetchAttemptCount.current + 1}/${maxFetchAttempts}`);
          
          // Add to recently fetched to exclude it next time
          recentlyFetchedIds.current.add(response.movie.movieId);
          
          fetchAttemptCount.current++;
          setIsLoading(false);
          
          if (fetchAttemptCount.current >= maxFetchAttempts) {
            console.log('Max attempts reached, stopping fetch');
            setCurrentMovie(null);
            return;
          }
          
          // Use exponential backoff for retry
          const delay = Math.min(200 * Math.pow(2, fetchAttemptCount.current - 1), 2000);
          fetchTimeoutRef.current = setTimeout(() => fetchNextMovie(), delay);
          return;
        }

        // Success! Add to recently fetched and reset attempt counter
        recentlyFetchedIds.current.add(response.movie.movieId);
        
        // Limit cache size to prevent memory issues
        if (recentlyFetchedIds.current.size > 50) {
          const idsArray = Array.from(recentlyFetchedIds.current);
          recentlyFetchedIds.current = new Set(idsArray.slice(-50));
        }

        // Reset attempt counter on success
        fetchAttemptCount.current = 0;

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
      toast.error('Failed to fetch movie recommendation. Please check your connection and try again.');
      setCurrentMovie(null);
      fetchAttemptCount.current = 0; // Reset on error
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, getAllSeenIds, getLikedIds, filters, userVector, maxFetchAttempts]);

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

  const handleGoHome = () => {
    // Reset to intro screen
    setCurrentView('intro');
    setHasStarted(false);
    setCurrentMovie(null);
    setUserVector(null);
    // Optionally reset user lists - uncomment if you want to clear all data
    // setUserLists({ liked: [], saved: [], disliked: [] });
  };

  const handleAction = async (action: 'like' | 'dislike' | 'skip' | 'save') => {
    if (!currentMovie || isLoading) return; // Prevent action if already loading

    // Immediately clear current movie for instant feedback
    const movieToProcess = currentMovie;
    setCurrentMovie(null);

    const newUserLists = { ...userLists };
    
    switch (action) {
      case 'like':
        newUserLists.liked = [...newUserLists.liked, movieToProcess];
        break;
      case 'dislike':
        newUserLists.disliked = [...newUserLists.disliked, movieToProcess];
        break;
      case 'save':
        newUserLists.saved = [...newUserLists.saved, movieToProcess];
        break;
      case 'skip':
        // No action needed for skip
        break;
    }

    setUserLists(newUserLists);

    // Clear recently fetched cache periodically to avoid excluding too many movies
    if (recentlyFetchedIds.current.size > 30) {
      const idsArray = Array.from(recentlyFetchedIds.current);
      recentlyFetchedIds.current = new Set(idsArray.slice(-15)); // Keep only last 15
    }

    // Immediately fetch next movie for instant swipe experience
    fetchNextMovie();

    // Submit feedback to backend in background (except for skip and save)
    if (action === 'like' || action === 'dislike') {
      try {
        await MovieAPI.submitFeedback({
          user_vector: userVector,
          movie_id: movieToProcess.movieId,
          feedback: action
        });
      } catch (error) {
        console.error('Error submitting feedback:', error);
      }
    }
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
    recentlyFetchedIds.current.clear();
    fetchAttemptCount.current = 0;
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
              <h1 
                className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent cursor-pointer hover:opacity-80 transition-opacity"
                onClick={handleGoHome}
                title="Go back to intro screen"
              >
                MovieMatch
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
                <div className="flex flex-col items-center justify-center py-12 h-200">
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
                             {(userLists.liked.length >= 5) ? (
     
                      <p className="text-muted-foreground">
                      AI-powered recommendations based on your taste
                    </p>
                    ) : (
                      <p className="text-muted-foreground">
                        Algorithm is learning your tastes and preferences...
                      </p>
                    )
                      
                    }
                    
                    <div className="flex items-center justify-center gap-4 mt-2 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <span className="text-red-400">←</span> Swipe left to pass
                      </span>
                      {!isMobile && (
                        <span className="flex items-center gap-1">
                          <span className="text-blue-400">↑</span> Swipe up to save
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <span className="text-green-400">→</span> Swipe right to like
                      </span>
                    </div>
                            <p className="text-xs text-muted-foreground mt-1">
                        Learning from {userLists.liked.length} liked movies
                      </p>

                  </div>
                </>
              ) : (
                <div className="text-center h-160">
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
