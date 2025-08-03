'use client';

import { useRef, useState, ReactNode } from 'react';

interface SwipeCardProps {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  children: ReactNode;
  disabled?: boolean;
}

export function SwipeCard({ 
  onSwipeLeft, 
  onSwipeRight, 
  onSwipeUp, 
  children, 
  disabled = false 
}: SwipeCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [startY, setStartY] = useState(0);
  const [translateX, setTranslateX] = useState(0);
  const [translateY, setTranslateY] = useState(0);

  const handleStart = (e: React.MouseEvent | React.TouchEvent) => {
    if (disabled) return;
    
    setIsDragging(true);
    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
    const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY;
    setStartX(clientX);
    setStartY(clientY);
  };

  const handleMove = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDragging || disabled) return;
  
    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
    const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY;
    
    const deltaX = clientX - startX;
    const deltaY = clientY - startY;
    
    setTranslateX(deltaX);
    setTranslateY(deltaY);
  };

  const handleEnd = () => {
    if (!isDragging || disabled) return;
    
    setIsDragging(false);

    const threshold = 120;
    const verticalThreshold = 100;

    // Check for swipe up first (save action)
    if (translateY < -verticalThreshold && Math.abs(translateX) < threshold) {
      onSwipeUp?.();
    }
    // Check for horizontal swipes
    else if (translateX > threshold) {
      onSwipeRight?.(); // Like
    } else if (translateX < -threshold) {
      onSwipeLeft?.(); // Dislike
    }

    // Reset position
    setTranslateX(0);
    setTranslateY(0);
  };

  const getRotation = () => {
    return translateX / 10; // Reduced rotation for smoother feel
  };

  const getOpacity = () => {
    const maxDistance = 200;
    const distance = Math.sqrt(translateX * translateX + translateY * translateY);
    return Math.max(0.7, 1 - distance / maxDistance);
  };

  const getSwipeIndicator = () => {
    const threshold = 60;
    
    if (translateY < -threshold && Math.abs(translateX) < threshold) {
      return 'SAVE';
    } else if (translateX > threshold) {
      return 'LIKE';
    } else if (translateX < -threshold) {
      return 'PASS';
    }
    return null;
  };

  const swipeIndicator = getSwipeIndicator();

  return (
    <div className="relative touch-none select-none">
      <div
        ref={cardRef}
        onMouseDown={handleStart}
        onMouseMove={handleMove}
        onMouseUp={handleEnd}
        onMouseLeave={handleEnd}
        onTouchStart={handleStart}
        onTouchMove={handleMove}
        onTouchEnd={handleEnd}
        style={{
          transform: `translateX(${translateX}px) translateY(${translateY}px) rotate(${getRotation()}deg)`,
          opacity: getOpacity(),
          transition: isDragging ? 'none' : 'transform 0.3s ease, opacity 0.3s ease',
          cursor: disabled ? 'default' : isDragging ? 'grabbing' : 'grab',
        }}
        className="relative"
      >
        {children}
        
        {/* Swipe Indicators */}
        {swipeIndicator && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className={`
              px-6 py-3 rounded-full text-2xl font-bold border-4 backdrop-blur-sm
              ${swipeIndicator === 'LIKE' 
                ? 'bg-green-500/20 text-green-400 border-green-400' 
                : swipeIndicator === 'PASS'
                ? 'bg-red-500/20 text-red-400 border-red-400'
                : 'bg-blue-500/20 text-blue-400 border-blue-400'
              }
            `}>
              {swipeIndicator === 'LIKE' && '❤️ LIKE'}
              {swipeIndicator === 'PASS' && '👎 PASS'}
              {swipeIndicator === 'SAVE' && '⭐ SAVE'}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
