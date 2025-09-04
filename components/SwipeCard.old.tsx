'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, PanInfo, useMotionValue, useTransform } from 'framer-motion';
import { FlashCard } from '@/lib/types';
import { ChevronLeft, ChevronRight, Star, RotateCcw } from 'lucide-react';

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
  const [exitX, setExitX] = useState(0);
  const [exitY, setExitY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-30, 30]);
  const opacity = 1; // 常に不透明にする

  // スワイプ方向のインジケーター
  const leftIndicatorOpacity = useTransform(x, [-100, 0], [1, 0]);
  const rightIndicatorOpacity = useTransform(x, [0, 100], [0, 1]);
  const upIndicatorOpacity = useTransform(y, [-100, 0], [1, 0]);

  const handleDragStart = () => {
    setIsDragging(true);
  };

  const handleDragEnd = (_: any, info: PanInfo) => {
    setIsDragging(false);
    const threshold = 100;
    
    if (Math.abs(info.offset.x) > threshold) {
      setExitX(info.offset.x > 0 ? 200 : -200);
      const quality = info.offset.x > 0 ? 4 : 1; // 右：わかる、左：わからない
      onSwipe(info.offset.x > 0 ? 'right' : 'left', quality);
    } else if (info.offset.y < -threshold) {
      setExitY(-200);
      onSwipe('up', 5); // 上：完璧
    }
  };

  const handleShowAnswer = () => {
    setShowAnswer(true);
  };

  const cardVariants = {
    initial: { scale: 0.95, opacity: 0 },
    animate: { 
      scale: isTop ? 1 : 0.9, 
      opacity: isTop ? 1 : 0,  // 後ろのカードは完全に透明に
      y: isTop ? 0 : 30,
      transition: { duration: 0.3 }
    },
    exit: { 
      x: exitX, 
      y: exitY,
      opacity: 0,
      transition: { duration: 0.2 }
    }
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

  if (!isTop) {
    return (
      <motion.div
        className="absolute inset-0 w-full h-full"
        variants={cardVariants}
        initial="initial"
        animate="animate"
      >
        <div className="w-full h-full bg-white rounded-2xl shadow-xl border border-gray-100" />
      </motion.div>
    );
  }

  return (
    <motion.div
      className={`absolute inset-0 w-full h-full ${showAnswer ? 'cursor-grab active:cursor-grabbing' : ''}`}
      style={{ x, y, rotate }}
      drag={showAnswer} // 答えを表示したらドラッグ可能にする
      dragElastic={0.2}
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      variants={cardVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      whileTap={showAnswer ? { scale: 1.02 } : {}}
      onAnimationComplete={() => setIsDragging(false)}
    >
      {/* スワイプインジケーター */}
      <motion.div
        className="absolute -left-20 top-1/2 -translate-y-1/2 bg-red-500 text-white px-4 py-2 rounded-full font-bold"
        style={{ opacity: leftIndicatorOpacity }}
      >
        わからない
      </motion.div>
      <motion.div
        className="absolute -right-20 top-1/2 -translate-y-1/2 bg-green-500 text-white px-4 py-2 rounded-full font-bold"
        style={{ opacity: rightIndicatorOpacity }}
      >
        わかる！
      </motion.div>
      <motion.div
        className="absolute left-1/2 -top-12 -translate-x-1/2 bg-yellow-500 text-white px-4 py-2 rounded-full font-bold"
        style={{ opacity: upIndicatorOpacity }}
      >
        完璧！⭐
      </motion.div>

      {/* カード本体 */}
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
                <div className="text-2xl font-bold mb-4 text-gray-800">
                  {card.question}
                </div>
                <button
                  onClick={handleShowAnswer}
                  className="mt-8 px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors font-medium shadow-md hover:shadow-lg transform hover:scale-105"
                >
                  答えを表示
                </button>
              </>
            ) : (
              <>
                <div className="text-lg font-medium mb-4 text-gray-600">
                  {card.question}
                </div>
                <div className="text-2xl text-blue-600 font-bold">
                  {card.answer}
                </div>
                {card.page && (
                  <div className="text-sm text-gray-400 mt-4">
                    {card.subject === 'chemistry' ? '化学' : '物理'} {card.chapter} - P.{card.page}
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* フッター（スワイプガイド + ボタン） */}
        <div className="px-6 py-4 border-t border-gray-100">
          {showAnswer ? (
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setExitX(-200);
                  setTimeout(() => onSwipe('left', 1), 100);
                }}
                className="flex-1 bg-red-100 hover:bg-red-200 text-red-700 py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <ChevronLeft className="w-5 h-5" />
                <span className="font-medium">わからない</span>
              </button>
              <button
                onClick={() => {
                  setExitY(-200);
                  setTimeout(() => onSwipe('up', 5), 100);
                }}
                className="bg-yellow-100 hover:bg-yellow-200 text-yellow-700 p-3 rounded-lg transition-colors"
              >
                <Star className="w-5 h-5" />
              </button>
              <button
                onClick={() => {
                  setExitX(200);
                  setTimeout(() => onSwipe('right', 4), 100);
                }}
                className="flex-1 bg-green-100 hover:bg-green-200 text-green-700 py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <span className="font-medium">わかる</span>
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center justify-around text-xs text-gray-400">
              <div className="flex items-center gap-1">
                <ChevronLeft className="w-4 h-4" />
                <span>わからない</span>
              </div>
              <div className="flex items-center gap-1">
                <Star className="w-4 h-4" />
                <span>上にスワイプで完璧</span>
              </div>
              <div className="flex items-center gap-1">
                <span>わかる</span>
                <ChevronRight className="w-4 h-4" />
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}