import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Filter, ChevronDown, Calendar, Tag, X, Globe } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Checkbox } from './ui/checkbox';
import { Slider } from './ui/slider';

export interface FilterState {
  genres: string[];
  languages: string[];
  yearRange: [number, number];
}

interface FiltersProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  availableGenres: string[];
  availableLanguages: string[];
  yearRange: [number, number];
}

export function Filters({ filters, onFiltersChange, availableGenres, availableLanguages, yearRange }: FiltersProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleGenreToggle = (genre: string) => {
    const newGenres = filters.genres.includes(genre)
      ? filters.genres.filter(g => g !== genre)
      : [...filters.genres, genre];
    
    onFiltersChange({
      ...filters,
      genres: newGenres
    });
  };

  const handleLanguageToggle = (language: string) => {
    const newLanguages = filters.languages.includes(language)
      ? filters.languages.filter(l => l !== language)
      : [...filters.languages, language];
    
    onFiltersChange({
      ...filters,
      languages: newLanguages
    });
  };

  const handleYearRangeChange = (newRange: number[]) => {
    onFiltersChange({
      ...filters,
      yearRange: [newRange[0], newRange[1]]
    });
  };

  const clearFilters = () => {
    onFiltersChange({
      genres: [],
      languages: [],
      yearRange: yearRange
    });
  };

  const hasActiveFilters = filters.genres.length > 0 || 
    filters.languages.length > 0 ||
    (filters.yearRange[0] !== yearRange[0] || filters.yearRange[1] !== yearRange[1]);

  const activeFilterCount = filters.genres.length + filters.languages.length + 
    (filters.yearRange[0] !== yearRange[0] || filters.yearRange[1] !== yearRange[1] ? 1 : 0);

  return (
    <div className="flex items-center gap-3 flex-wrap">
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className="flex items-center gap-2 relative"
          >
            <Filter className="w-4 h-4" />
            Filters
            <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            {hasActiveFilters && (
              <Badge variant="destructive" className="absolute -top-2 -right-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs">
                {activeFilterCount}
              </Badge>
            )}
          </Button>
        </PopoverTrigger>
        
        <PopoverContent className="w-80 bg-gray-800/70 backdrop-blur-sm border-border text-white" align="start" sideOffset={8}>
          <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
              <h4 className="font-semibold text-sm text-white">Filter Movies</h4>
              {hasActiveFilters && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearFilters}
                  className="h-auto p-1 text-xs text-gray-300 hover:text-white hover:bg-white/10"
                >
                  Clear all
                </Button>
              )}
            </div>

            {/* Genre Filter */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Tag className="w-4 h-4 text-purple-400" />
                <span className="text-sm font-medium text-white">Genres</span>
                {filters.genres.length > 0 && (
                  <Badge variant="secondary" className="text-xs h-4 px-1">
                    {filters.genres.length}
                  </Badge>
                )}
              </div>
              <div className="max-h-32 overflow-y-auto">
                <div className="grid grid-cols-2 gap-1 text-sm">
                  {availableGenres.map(genre => (
                    <label key={genre} className="flex items-center space-x-2 cursor-pointer hover:bg-white/10 rounded p-1">
                      <Checkbox
                        id={`genre-${genre}`}
                        checked={filters.genres.includes(genre)}
                        onCheckedChange={() => handleGenreToggle(genre)}
                        className="h-3 w-3"
                      />
                      <span className="text-xs text-white">{genre}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            {/* Language Filter */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-medium text-white">Languages</span>
                {filters.languages.length > 0 && (
                  <Badge variant="secondary" className="text-xs h-4 px-1">
                    {filters.languages.length}
                  </Badge>
                )}
              </div>
              <div className="grid grid-cols-2 gap-1 text-sm">
                {availableLanguages.map(language => (
                  <label key={language} className="flex items-center space-x-2 cursor-pointer hover:bg-white/10 rounded p-1">
                    <Checkbox
                      id={`language-${language}`}
                      checked={filters.languages.includes(language)}
                      onCheckedChange={() => handleLanguageToggle(language)}
                      className="h-3 w-3"
                    />
                    <span className="text-xs text-white">{language}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Year Range Filter */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-green-400" />
                <span className="text-sm font-medium text-white">Release Year</span>
              </div>
              <div className="px-2">
                <Slider
                  value={filters.yearRange}
                  onValueChange={handleYearRangeChange}
                  max={yearRange[1]}
                  min={yearRange[0]}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-300 mt-2">
                  <span>{filters.yearRange[0]}</span>
                  <span>{filters.yearRange[1]}</span>
                </div>
              </div>
            </div>
          </div>
        </PopoverContent>
      </Popover>

      {/* Active Filters Display */}
      <div className="flex flex-wrap gap-2">
        <AnimatePresence>
          {filters.genres.map(genre => (
            <motion.div
              key={`genre-${genre}`}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
            >
              <Badge
                variant="secondary"
                className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground transition-colors text-xs"
                onClick={() => handleGenreToggle(genre)}
              >
                <Tag className="w-3 h-3 mr-1" />
                {genre}
                <X className="w-3 h-3 ml-1" />
              </Badge>
            </motion.div>
          ))}
        </AnimatePresence>

        <AnimatePresence>
          {filters.languages.map(language => (
            <motion.div
              key={`language-${language}`}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
            >
              <Badge
                variant="secondary"
                className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground transition-colors text-xs"
                onClick={() => handleLanguageToggle(language)}
              >
                <Globe className="w-3 h-3 mr-1" />
                {language}
                <X className="w-3 h-3 ml-1" />
              </Badge>
            </motion.div>
          ))}
        </AnimatePresence>

        <AnimatePresence>
          {(filters.yearRange[0] !== yearRange[0] || filters.yearRange[1] !== yearRange[1]) && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
            >
              <Badge
                variant="secondary"
                className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground transition-colors text-xs"
                onClick={() => onFiltersChange({ ...filters, yearRange: yearRange })}
              >
                <Calendar className="w-3 h-3 mr-1" />
                {filters.yearRange[0]} - {filters.yearRange[1]}
                <X className="w-3 h-3 ml-1" />
              </Badge>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}