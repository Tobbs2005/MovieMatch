import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Play, Sparkles, Film, Heart, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Movie } from '../types/movie';
import { MovieAPI } from '../services/movieAPI';
import { toast } from 'sonner';

interface IntroScreenProps {
  onStartSwiping: (likedMovies: Movie[]) => void;
}

export function IntroScreen({ onStartSwiping }: IntroScreenProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMovies, setSelectedMovies] = useState<Movie[]>([]);
  const [popularMovies, setPopularMovies] = useState<Movie[]>([]);
  const [isLoadingPopular, setIsLoadingPopular] = useState(true);
  const [searchResults, setSearchResults] = useState<Movie[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Fetch onboarding movies on component mount
  useEffect(() => {
    const fetchOnboardingMovies = async () => {
      try {
        setIsLoadingPopular(true);
        // Use recommend endpoint with empty liked list for onboarding
        const response = await MovieAPI.getRecommendation({
          seen_ids: [],
          liked_ids: [],
          user_vector: null
        });
        
        if (response.movie) {
          setPopularMovies([response.movie]);
        } else {
          setPopularMovies([]);
        }
      } catch (error) {
        console.error('Error fetching onboarding movies:', error);
        toast.error('Failed to load movies. Please check your connection and try again.');
        setPopularMovies([]);
      } finally {
        setIsLoadingPopular(false);
      }
    };

    fetchOnboardingMovies();
  }, []);

  // Search movies when user types
  useEffect(() => {
    const searchMovies = async () => {
      if (searchTerm.trim().length < 2) {
        setSearchResults([]);
        setIsSearching(false);
        return;
      }

      try {
        setIsSearching(true);
        const response = await MovieAPI.searchMovies({
          query: searchTerm,
        });
        const movies: Movie[] = response.movies.map(movie => ({
          movieId: movie.movieId,
          title: movie.title,
          poster_path: movie.poster_path,
          overview: movie.overview,
          genres: movie.genres,
          release_date: movie.release_date
        }));
        setSearchResults(movies);
      } catch (error) {
        console.error('Error searching movies:', error);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    };

    const debounceTimer = setTimeout(searchMovies, 300);
    return () => clearTimeout(debounceTimer);
  }, [searchTerm]);

  // Get movies to display (search results or popular movies)
  const moviesToShow = searchTerm.trim().length >= 2 ? searchResults : popularMovies;
  
  const filteredMovies = moviesToShow.filter(movie =>
    !selectedMovies.find(selected => selected.movieId === movie.movieId)
  );

  const handleMovieSelect = (movie: Movie) => {
    setSelectedMovies([...selectedMovies, movie]);
    setSearchTerm('');
  };

  const handleRemoveMovie = (movieId: number) => {
    setSelectedMovies(selectedMovies.filter(m => m.movieId !== movieId));
  };

  const handleStartSwiping = () => {
    onStartSwiping(selectedMovies);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-500/10 via-background to-blue-500/10 flex items-center justify-center p-6">
      {/* User Note about Backend Spin-up */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-50 max-w-xl w-full px-4">
        <div className="bg-yellow-100 border border-yellow-300 text-yellow-900 rounded-lg px-4 py-3 shadow-md text-sm flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin text-yellow-600" />
          <span>
            Note: The backend is hosted on Hugging Face Spaces, which uses containerized infrastructure. After periods of inactivity, the service may require a cold start, resulting in longer response times while the container is being reactivated. If no movie data appears, please wait a moment and try refreshing the page.
          </span>
        </div>
      </div>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="max-w-2xl w-full text-center space-y-8"
      >
        {/* Logo Animation */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ 
            delay: 0.2, 
            type: "spring", 
            stiffness: 200, 
            damping: 15 
          }}
          className="relative"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <motion.div
              animate={{ 
                rotate: [0, 10, -10, 0],
                scale: [1, 1.1, 1]
              }}
              transition={{ 
                duration: 2, 
                repeat: Infinity, 
                repeatDelay: 3 
              }}
            >
              <Film className="w-12 h-12 text-purple-500" />
            </motion.div>
            <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              MovieMatch
            </h1>
          </div>
          
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="flex items-center justify-center gap-2 text-muted-foreground"
          >
            <Sparkles className="w-4 h-4" />
            <span>Discover your next favorite movie</span>
            <Sparkles className="w-4 h-4" />
          </motion.div>
        </motion.div>

        {/* Search Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="space-y-6"
        >
          <div className="text-left">
            <h2 className="text-xl mb-2">Tell us what you already love</h2>
            <p className="text-muted-foreground text-sm">
              Search and select movies you've enjoyed to get better recommendations
            </p>
          </div>

          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              type="text"
              placeholder="Search for movies you like..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 py-3 text-base"
            />
            
            {/* Search Results */}
            {searchTerm && filteredMovies.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute top-full left-0 right-0 bg-gray-800/70 backdrop-blur-sm border border-border rounded-md mt-1 shadow-lg z-10 max-h-48 overflow-y-auto"
              >
                {filteredMovies.slice(0, 5).map((movie) => (
                  <button
                    key={movie.movieId}
                    onClick={() => handleMovieSelect(movie)}
                    className="w-full text-left px-4 py-3 hover:bg-white/10 transition-colors flex items-center gap-3 text-white"
                  >
                    <img
                      src={movie.poster_path}
                      alt={movie.title}
                      className="w-8 h-12 object-cover rounded"
                    />
                    <div>
                      <div className="font-medium text-white">{movie.title}</div>
                      <div className="text-sm text-gray-300">
                        {movie.release_date ? new Date(movie.release_date).getFullYear() : 'N/A'}
                      </div>
                    </div>
                  </button>
                ))}
              </motion.div>
            )}
          </div>

          {/* Selected Movies */}
          {selectedMovies.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="space-y-3"
            >
              <div className="flex items-center gap-2 text-sm font-medium">
                <Heart className="w-4 h-4 text-red-500" />
                Your liked movies ({selectedMovies.length})
              </div>
              <div className="flex flex-wrap gap-2">
                {selectedMovies.map((movie) => (
                  <Badge
                    key={movie.movieId}
                    variant="secondary"
                    className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground transition-colors"
                    onClick={() => handleRemoveMovie(movie.movieId)}
                  >
                    {movie.title} ×
                  </Badge>
                ))}
              </div>
            </motion.div>
          )}
        </motion.div>

        {/* Start Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
        >
          <Button
            onClick={handleStartSwiping}
            size="lg"
            className="px-8 py-4 text-lg font-semibold bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white border-0"
          >
            <Play className="w-5 h-5 mr-2" />
            Start Swiping
          </Button>
          
          <p className="text-sm text-muted-foreground mt-3">
            {selectedMovies.length > 0 
              ? `We'll use your ${selectedMovies.length} selected movies to personalize your experience`
              : "You can skip this step and start discovering movies right away"
            }
          </p>
        </motion.div>

        {/* Floating Animation Elements */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute"
              initial={{ 
                x: typeof window !== 'undefined' ? Math.random() * window.innerWidth : Math.random() * 1000,
                y: typeof window !== 'undefined' ? Math.random() * window.innerHeight : Math.random() * 1000,
                opacity: 0 
              }}
              animate={{
                y: [null, -20, 20],
                opacity: [0, 0.3, 0],
              }}
              transition={{
                duration: 4 + Math.random() * 2,
                repeat: Infinity,
                delay: Math.random() * 2,
              }}
            >
              <Film className="w-6 h-6 text-purple-400/30" />
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}