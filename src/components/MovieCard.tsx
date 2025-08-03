import { Movie } from '../types/movie';
import { Star, Clock } from 'lucide-react';
import { motion } from 'framer-motion';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { SwipeCard } from './SwipeCard';

interface MovieCardProps {
  movie: Movie;
  onAction?: (action: 'like' | 'dislike' | 'skip' | 'save') => void;
  isSwipeable?: boolean;
}

export function MovieCard({ movie, onAction, isSwipeable = true }: MovieCardProps) {
  const handleSwipeLeft = () => {
    onAction?.('dislike');
  };

  const handleSwipeRight = () => {
    onAction?.('like');
  };

  const handleSwipeUp = () => {
    onAction?.('save');
  };

  const cardContent = (
    <motion.div
      className="relative w-full max-w-md mx-auto bg-card rounded-2xl overflow-hidden shadow-2xl border border-border/50"
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.9, opacity: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={!isSwipeable ? { y: -5 } : undefined}
    >
      <div className="relative">
        <ImageWithFallback
          src={movie.poster_path}
          alt={movie.title}
          className="w-full h-[500px] object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
        
        {/* Movie Info Overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-2xl font-bold">{movie.title}</h3>
            <span className="text-lg opacity-90">
              {movie.release_date ? new Date(movie.release_date).getFullYear() : 'N/A'}
            </span>
          </div>
          
          <div className="flex flex-wrap gap-2 mb-4">
            {movie.genres.split(',').map((genre, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-white/20 backdrop-blur-sm text-white rounded-full text-sm border border-white/30"
              >
                {genre.trim()}
              </span>
            ))}
          </div>
        </div>
      </div>
      
      <div className="p-6">
        <p className="text-muted-foreground leading-relaxed">
          {movie.overview}
        </p>
      </div>
    </motion.div>
  );

  // Wrap with SwipeCard if swipeable
  if (isSwipeable && onAction) {
    return (
      <SwipeCard
        onSwipeLeft={handleSwipeLeft}
        onSwipeRight={handleSwipeRight}
        onSwipeUp={handleSwipeUp}
      >
        {cardContent}
      </SwipeCard>
    );
  }

  return cardContent;
}