'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FlashCard } from '@/lib/types';
import { ChevronLeft, ChevronRight, Star } from 'lucide-react';

interface SwipeCardProps {
  card: FlashCard;
  onSwipe: (direction: 'left' | 'right' | 'up', quality: number) => void;
  isTop: boolean;
  totalCards: number;
  currentIndex: number;
}

export default function SwipeCard({
  card,
  onSwipe,
  isTop,
  totalCards,
  currentIndex,
}: SwipeCardProps) {
  const [showAnswer, setShowAnswer] = useState(false);
  const [isExiting, setIsExiting] = useState(false);
  const [exitDirection, setExitDirection] = useState<'left' | 'right' | 'up' | null>(null);
  const [isClient, setIsClient] = useState(false);

  // クライアントサイドでのみ実行
  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleAnswer = (direction: 'left' | 'right' | 'up', quality: number) => {
    setIsExiting(true);
    setExitDirection(direction);
    setTimeout(() => {
      onSwipe(direction, quality);
      setShowAnswer(false);
      setIsExiting(false);
      setExitDirection(null);
    }, 300);
  };

  const getDifficultyColor = (difficulty: number) => {
    const colors = ['bg-green-500', 'bg-blue-500', 'bg-yellow-500', 'bg-orange-500', 'bg-red-500'];
    return colors[difficulty - 1] || colors[0];
  };

  const getTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      definition: '定義',
      formula: '公式',
      separation: '分離法',
      state_change: '状態変化',
      application: '応用'
    };
    return labels[type] || type;
  };

  // サーバーサイドレンダリング中は何も表示しない
  if (!isClient) {
    return null;
  }

  if (!isTop) {
    return (
      <div className="absolute inset-0 w-full h-full">
        <div className="w-full h-full bg-white rounded-2xl shadow-xl border border-gray-100 opacity-50 scale-95" />
      </div>
    );
  }

  const exitVariants = {
    initial: { x: 0, y: 0, opacity: 1, scale: 1 },
    exitLeft: { x: -300, opacity: 0, transition: { duration: 0.3 } },
    exitRight: { x: 300, opacity: 0, transition: { duration: 0.3 } },
    exitUp: { y: -300, opacity: 0, transition: { duration: 0.3 } }
  };

  const getExitAnimation = () => {
    if (!isExiting) return 'initial';
    switch (exitDirection) {
      case 'left': return 'exitLeft';
      case 'right': return 'exitRight';
      case 'up': return 'exitUp';
      default: return 'initial';
    }
  };

  return (
    <motion.div
      className="absolute inset-0 w-full h-full"
      variants={exitVariants}
      initial="initial"
      animate={getExitAnimation()}
    >
      <div className="w-full h-full bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden flex flex-col">
        {/* ヘッダー */}
        <div className="px-6 py-4 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className={`px-2 py-1 rounded text-xs text-white ${getDifficultyColor(card.difficulty)}`}>
                Lv.{card.difficulty}
              </span>
              <span className="px-2 py-1 bg-gray-100 rounded text-xs text-gray-600">
                {getTypeLabel(card.type)}
              </span>
            </div>
            <div className="text-sm text-gray-500">
              {currentIndex + 1} / {totalCards}
            </div>
          </div>
        </div>

        {/* コンテンツエリア */}
        <div className="flex-1 relative flex items-center justify-center p-6">
          <div className="text-center max-w-md">
            {!showAnswer ? (
              <>
                <div className="text-2xl font-bold mb-8 text-gray-800">
                  {card.question}
                </div>
                <button
                  onClick={() => setShowAnswer(true)}
                  className="relative z-50 px-8 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium shadow-md hover:shadow-lg transition-all transform hover:scale-105"
                >
                  答えを表示
                </button>
              </>
            ) : (
              <AnimatePresence mode="wait">
                <motion.div
                  key="answer"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="text-lg font-medium mb-4 text-gray-600">
                    {card.question}
                  </div>
                  <div className="text-2xl text-blue-600 font-bold mb-6">
                    {card.answer}
                  </div>
                  {card.page && (
                    <div className="text-sm text-gray-400 mb-6">
                      {card.subject === 'chemistry' ? '化学' : '物理'} {card.chapter} - P.{card.page}
                    </div>
                  )}
                  
                  {/* アクションボタン */}
                  <div className="relative z-50 flex items-center gap-2">
                    <button
                      onClick={() => handleAnswer('left', 1)}
                      className="flex-1 bg-red-100 hover:bg-red-200 text-red-700 py-3 px-4 rounded-lg font-medium transition-all transform hover:scale-105 flex items-center justify-center gap-2"
                    >
                      <ChevronLeft className="w-5 h-5" />
                      <span>わからない</span>
                    </button>
                    
                    <button
                      onClick={() => handleAnswer('up', 5)}
                      className="bg-yellow-100 hover:bg-yellow-200 text-yellow-700 p-3 rounded-lg transition-all transform hover:scale-105"
                    >
                      <Star className="w-5 h-5" />
                    </button>
                    
                    <button
                      onClick={() => handleAnswer('right', 4)}
                      className="flex-1 bg-green-100 hover:bg-green-200 text-green-700 py-3 px-4 rounded-lg font-medium transition-all transform hover:scale-105 flex items-center justify-center gap-2"
                    >
                      <span>わかる</span>
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  </div>
                </motion.div>
              </AnimatePresence>
            )}
          </div>
        </div>

        {/* フッター（スワイプガイド） */}
        {!showAnswer && (
          <div className="px-6 py-3 border-t border-gray-100">
            <div className="flex items-center justify-around text-xs text-gray-400">
              <div>タップして答えを表示</div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}