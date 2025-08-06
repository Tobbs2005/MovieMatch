import { Movie } from '../types/movie';
import { MovieCard } from './MovieCard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Button } from './ui/button';
import { Heart, Bookmark, X, Trash2, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

interface MovieListsProps {
  likedMovies: Movie[];
  savedMovies: Movie[];
  dislikedMovies: Movie[];
  onMoveMovie: (movie: Movie, fromList: 'liked' | 'saved' | 'disliked', toList: 'liked' | 'saved' | 'disliked') => void;
  onRemoveMovie: (movie: Movie, fromList: 'liked' | 'saved' | 'disliked') => void;
}

interface MovieCardWithActionsProps {
  movie: Movie;
  currentList: 'liked' | 'saved' | 'disliked';
  onMoveMovie: (movie: Movie, fromList: 'liked' | 'saved' | 'disliked', toList: 'liked' | 'saved' | 'disliked') => void;
  onRemoveMovie: (movie: Movie, fromList: 'liked' | 'saved' | 'disliked') => void;
}

function MovieCardWithActions({ movie, currentList, onMoveMovie, onRemoveMovie }: MovieCardWithActionsProps) {
  const handleMoveToLiked = () => {
    if (currentList !== 'liked') {
      onMoveMovie(movie, currentList, 'liked');
      toast.success(`Moved "${movie.title}" to Liked`);
    }
  };

  const handleMoveToSaved = () => {
    if (currentList !== 'saved') {
      onMoveMovie(movie, currentList, 'saved');
      toast.success(`Moved "${movie.title}" to Saved`);
    }
  };

  const handleMoveToDisliked = () => {
    if (currentList !== 'disliked') {
      onMoveMovie(movie, currentList, 'disliked');
      toast.success(`Moved "${movie.title}" to Disliked`);
    }
  };

  const handleRemove = () => {
    onRemoveMovie(movie, currentList);
    toast.success(`Removed "${movie.title}" from your ${currentList} list`);
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="relative group"
    >
      <MovieCard movie={movie} isSwipeable={false} />
      
      {/* Quick Action Buttons - Always Visible */}
      <div className="absolute bottom-4 left-4 right-4">
        <div className="bg-background/90 backdrop-blur-sm border border-border/50 rounded-lg p-3 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
          <div className="flex items-center justify-between gap-2">
            <div className="flex gap-2">
              {currentList !== 'liked' && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleMoveToLiked}
                  className="flex items-center gap-1 hover:bg-green-50 hover:border-green-300 dark:hover:bg-green-900/20 dark:hover:border-green-700"
                >
                  <Heart className="w-3 h-3 text-green-600" />
                  Like
                </Button>
              )}
              
              {currentList !== 'saved' && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleMoveToSaved}
                  className="flex items-center gap-1 hover:bg-blue-50 hover:border-blue-300 dark:hover:bg-blue-900/20 dark:hover:border-blue-700"
                >
                  <Bookmark className="w-3 h-3 text-blue-600" />
                  Save
                </Button>
              )}
              
              {currentList !== 'disliked' && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleMoveToDisliked}
                  className="flex items-center gap-1 hover:bg-red-50 hover:border-red-300 dark:hover:bg-red-900/20 dark:hover:border-red-700"
                >
                  <X className="w-3 h-3 text-red-600" />
                  Dislike
                </Button>
              )}
            </div>
            
            <Button
              size="sm"
              variant="outline"
              onClick={handleRemove}
              className="flex items-center gap-1 hover:bg-destructive hover:text-destructive-foreground"
            >
              <Trash2 className="w-3 h-3" />
              Remove
            </Button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export function MovieLists({ likedMovies, savedMovies, dislikedMovies, onMoveMovie, onRemoveMovie }: MovieListsProps) {
  const renderMovieGrid = (movies: Movie[], emptyMessage: string, listType: 'liked' | 'saved' | 'disliked') => {
    if (movies.length === 0) {
      return (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
              {listType === 'liked' && <Heart className="w-8 h-8 text-muted-foreground" />}
              {listType === 'saved' && <Bookmark className="w-8 h-8 text-muted-foreground" />}
              {listType === 'disliked' && <X className="w-8 h-8 text-muted-foreground" />}
            </div>
            <h3 className="text-lg font-semibold mb-2">No {listType} movies yet</h3>
            <p className="text-muted-foreground text-sm">{emptyMessage}</p>
          </div>
        </div>
      );
    }

    return (
      <motion.div 
        layout
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {movies.map((movie) => (
          <MovieCardWithActions
            key={`${listType}-${movie.movieId}`}
            movie={movie}
            currentList={listType}
            onMoveMovie={onMoveMovie}
            onRemoveMovie={onRemoveMovie}
          />
        ))}
      </motion.div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Your Movie Collection</h2>
        <div className="text-right">
          <p className="text-sm text-muted-foreground">
            Total: {likedMovies.length + savedMovies.length + dislikedMovies.length} movies
          </p>
          <p className="text-xs text-muted-foreground">
            Hover over movies to manage them
          </p>
        </div>
      </div>
      
      <Tabs defaultValue="liked" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="liked" className="flex items-center gap-2">
            <Heart className="w-4 h-4 text-green-600" />
            Liked ({likedMovies.length})
          </TabsTrigger>
          <TabsTrigger value="saved" className="flex items-center gap-2">
            <Bookmark className="w-4 h-4 text-blue-600" />
            Saved ({savedMovies.length})
          </TabsTrigger>
          <TabsTrigger value="disliked" className="flex items-center gap-2">
            <X className="w-4 h-4 text-red-600" />
            Disliked ({dislikedMovies.length})
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="liked" className="mt-6">
          {renderMovieGrid(likedMovies, "Start swiping to build your collection of favorite movies!", 'liked')}
        </TabsContent>
        
        <TabsContent value="saved" className="mt-6">
          {renderMovieGrid(savedMovies, "Save movies you want to watch later while browsing!", 'saved')}
        </TabsContent>
        
        <TabsContent value="disliked" className="mt-6">
          {renderMovieGrid(dislikedMovies, "Movies you've disliked will appear here.", 'disliked')}
        </TabsContent>
      </Tabs>
    </div>
  );
}