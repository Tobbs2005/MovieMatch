import { Heart, X, BookmarkPlus, SkipForward } from 'lucide-react';
import { Button } from './ui/button';
import { motion } from 'framer-motion';

interface SwipeControlsProps {
  onLike: () => void;
  onDislike: () => void;
  onSave: () => void;
  onSkip: () => void;
}

export function SwipeControls({ onLike, onDislike, onSave, onSkip }: SwipeControlsProps) {
  return (
    <motion.div
      className="flex items-center justify-center gap-6 mt-8"
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.2 }}
    >
      <Button
        variant="outline"
        size="lg"
        onClick={onDislike}
        className="rounded-full p-5 border-2 border-red-200 hover:bg-red-50 hover:border-red-300 dark:border-red-800 dark:hover:bg-red-900/20 dark:hover:border-red-700 transition-all duration-200 hover:scale-110"
      >
        <X className="w-7 h-7 text-red-500" />
      </Button>
      
      <Button
        variant="outline"
        size="lg"
        onClick={onSkip}
        className="rounded-full p-5 border-2 border-border hover:bg-accent transition-all duration-200 hover:scale-110"
      >
        <SkipForward className="w-7 h-7 text-muted-foreground" />
      </Button>
      
      <Button
        variant="outline"
        size="lg"
        onClick={onSave}
        className="rounded-full p-5 border-2 border-blue-200 hover:bg-blue-50 hover:border-blue-300 dark:border-blue-800 dark:hover:bg-blue-900/20 dark:hover:border-blue-700 transition-all duration-200 hover:scale-110"
      >
        <BookmarkPlus className="w-7 h-7 text-blue-500" />
      </Button>
      
      <Button
        variant="outline"
        size="lg"
        onClick={onLike}
        className="rounded-full p-5 border-2 border-green-200 hover:bg-green-50 hover:border-green-300 dark:border-green-800 dark:hover:bg-green-900/20 dark:hover:border-green-700 transition-all duration-200 hover:scale-110"
      >
        <Heart className="w-7 h-7 text-green-500" />
      </Button>
    </motion.div>
  );
}