'use client';

import { useState, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import SwipeCard from '@/components/SwipeCard';
import { FlashCard } from '@/lib/types';
import { LearningAlgorithm } from '@/lib/learning-algorithm';
import { ArrowLeft, RefreshCw, Trophy, Target, Zap } from 'lucide-react';
import Link from 'next/link';

export default function StudyPage() {
  const [cards, setCards] = useState<FlashCard[]>([]);
  const [currentDeck, setCurrentDeck] = useState<FlashCard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [sessionStats, setSessionStats] = useState({
    studied: 0,
    correct: 0,
    streak: 0,
    maxStreak: 0,
  });
  const [selectedChapter, setSelectedChapter] = useState<'all' | '理論化学' | '無機化学' | '有機化学'>('all');
  const [deckSize, setDeckSize] = useState(20);
  const [studyMode, setStudyMode] = useState<'normal' | 'weak' | 'quick' | 'new'>('normal');

  useEffect(() => {
    loadCards();
    // URLパラメータからモードを取得
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const mode = params.get('mode');
      if (mode === 'weak' || mode === 'quick' || mode === 'new') {
        setStudyMode(mode);
        if (mode === 'quick') {
          setDeckSize(10); // クイックモードは10枚
        }
      }
    }
  }, []);

  const loadCards = async () => {
    try {
      const response = await fetch('/learning-data.json');
      const data = await response.json();
      const loadedCards: FlashCard[] = data.cards.map((card: Partial<FlashCard> & { lastReviewed?: string; nextReview?: string }) => ({
        ...card,
        lastReviewed: card.lastReviewed ? new Date(card.lastReviewed) : undefined,
        nextReview: card.nextReview ? new Date(card.nextReview) : undefined,
      }));
      setCards(loadedCards);
      generateNewDeck(loadedCards);
    } catch (error) {
      console.error('Failed to load cards:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateNewDeck = (allCards?: FlashCard[]) => {
    const cardsToUse = allCards || cards;
    let filteredCards = cardsToUse;
    
    // 化学の章で絞り込み
    if (selectedChapter !== 'all') {
      filteredCards = cardsToUse.filter(card => card.chapter === selectedChapter);
    }

    // モードに応じてカードをフィルタリング
    switch (studyMode) {
      case 'weak':
        // 正答率が低いカード（50%未満）または未学習カード
        filteredCards = filteredCards.filter(card => 
          card.reviewCount === 0 || 
          (card.reviewCount > 0 && card.correctCount / card.reviewCount < 0.5)
        );
        break;
      case 'new':
        // まだ学習していないカード
        filteredCards = filteredCards.filter(card => card.reviewCount === 0);
        break;
      case 'quick':
        // ランダムに選択（復習が必要なカードを優先）
        filteredCards = filteredCards.sort((a, b) => {
          const aScore = a.confidence || 0;
          const bScore = b.confidence || 0;
          return aScore - bScore;
        });
        break;
    }

    const actualDeckSize = studyMode === 'quick' ? 10 : deckSize;
    const deck = LearningAlgorithm.generateStudyDeck(filteredCards, actualDeckSize);
    setCurrentDeck(deck);
    setCurrentIndex(0);
    setSessionStats(prev => ({ ...prev, studied: 0, correct: 0, streak: 0 }));
  };

  const handleSwipe = (direction: 'left' | 'right' | 'up', quality: number) => {
    if (currentIndex >= currentDeck.length) return;

    const currentCard = currentDeck[currentIndex];
    const { nextReview, confidence } = LearningAlgorithm.calculateNextReview(currentCard, quality);

    // カードの更新
    const updatedCard = {
      ...currentCard,
      lastReviewed: new Date(),
      nextReview,
      reviewCount: currentCard.reviewCount + 1,
      correctCount: quality >= 3 ? currentCard.correctCount + 1 : currentCard.correctCount,
      confidence,
    };

    // カード一覧を更新
    const updatedCards = cards.map(card =>
      card.id === updatedCard.id ? updatedCard : card
    );
    setCards(updatedCards);

    // localStorage に保存
    saveProgress(updatedCards);

    // セッション統計を更新
    const isCorrect = quality >= 3;
    setSessionStats(prev => ({
      studied: prev.studied + 1,
      correct: isCorrect ? prev.correct + 1 : prev.correct,
      streak: isCorrect ? prev.streak + 1 : 0,
      maxStreak: isCorrect ? Math.max(prev.maxStreak, prev.streak + 1) : prev.maxStreak,
    }));

    // 次のカードへ
    setTimeout(() => {
      setCurrentIndex(prev => prev + 1);
    }, 300);
  };

  const saveProgress = (updatedCards: FlashCard[]) => {
    const progress = updatedCards.map(card => ({
      id: card.id,
      reviewCount: card.reviewCount,
      correctCount: card.correctCount,
      confidence: card.confidence,
      lastReviewed: card.lastReviewed,
      nextReview: card.nextReview,
    }));
    localStorage.setItem('uchuichi-progress', JSON.stringify(progress));
  };

  const loadProgress = () => {
    const saved = localStorage.getItem('uchuichi-progress');
    if (saved) {
      const progress = JSON.parse(saved);
      const updatedCards = cards.map(card => {
        const savedCard = progress.find((p: { id: string }) => p.id === card.id);
        if (savedCard) {
          return {
            ...card,
            ...savedCard,
            lastReviewed: savedCard.lastReviewed ? new Date(savedCard.lastReviewed) : undefined,
            nextReview: savedCard.nextReview ? new Date(savedCard.nextReview) : undefined,
          };
        }
        return card;
      });
      setCards(updatedCards);
      return updatedCards;
    }
    return cards;
  };

  useEffect(() => {
    if (cards.length > 0) {
      const updatedCards = loadProgress();
      generateNewDeck(updatedCards);
    }
  }, [selectedChapter, deckSize]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">学習データを読み込み中...</p>
        </div>
      </div>
    );
  }

  const isDeckComplete = currentIndex >= currentDeck.length;
  const accuracy = sessionStats.studied > 0 
    ? Math.round((sessionStats.correct / sessionStats.studied) * 100) 
    : 0;

  if (isDeckComplete) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-xl p-8 max-w-md w-full text-center">
          <Trophy className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">セッション完了！</h2>
          <div className="space-y-4 my-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-3xl font-bold text-blue-600">{sessionStats.studied}</div>
              <div className="text-sm text-gray-600">学習カード数</div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-600">{accuracy}%</div>
                <div className="text-xs text-gray-600">正答率</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-600">{sessionStats.maxStreak}</div>
                <div className="text-xs text-gray-600">最大連続正解</div>
              </div>
            </div>
          </div>
          <button
            onClick={() => generateNewDeck()}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full py-3 font-medium hover:shadow-lg transition-all transform hover:scale-105"
          >
            次のセッションを始める
          </button>
          <Link
            href="/"
            className="block mt-4 text-gray-500 hover:text-gray-700 transition-colors"
          >
            ホームに戻る
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex flex-col">
      {/* ヘッダー */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-100 px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Link href="/" className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 bg-green-100 px-3 py-1 rounded-full">
              <Zap className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-green-700">
                {sessionStats.streak} 連続
              </span>
            </div>
            <div className="flex items-center gap-2 bg-blue-100 px-3 py-1 rounded-full">
              <Target className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-700">
                {accuracy}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* コントロールパネル */}
      <div className="bg-white/60 backdrop-blur-sm px-4 py-3 border-b border-gray-100">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center gap-4 mb-2">
            <select
              value={selectedChapter}
              onChange={(e) => setSelectedChapter(e.target.value as 'all' | '理論化学' | '無機化学' | '有機化学')}
              className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm"
            >
              <option value="all">全範囲</option>
              <option value="理論化学">理論化学</option>
              <option value="無機化学">無機化学</option>
              <option value="有機化学">有機化学</option>
            </select>
            <select
              value={deckSize}
              onChange={(e) => setDeckSize(Number(e.target.value))}
              className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm"
              disabled={studyMode === 'quick'}
            >
              <option value="10">10枚</option>
              <option value="20">20枚</option>
              <option value="30">30枚</option>
              <option value="50">50枚</option>
            </select>
            <button
              onClick={() => generateNewDeck()}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="デッキを再生成"
            >
              <RefreshCw className="w-5 h-5 text-gray-600" />
            </button>
          </div>
          
          {/* 学習モード表示 */}
          {studyMode !== 'normal' && (
            <div className="text-center">
              <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium
                ${studyMode === 'weak' ? 'bg-red-100 text-red-700' : ''}
                ${studyMode === 'quick' ? 'bg-blue-100 text-blue-700' : ''}
                ${studyMode === 'new' ? 'bg-purple-100 text-purple-700' : ''}
              `}>
                {studyMode === 'weak' && '🎯 弱点克服モード'}
                {studyMode === 'quick' && '⚡ クイック復習モード（10問）'}
                {studyMode === 'new' && '✨ 新規学習モード'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* メインエリア */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="relative w-full max-w-md h-[600px]">
          <AnimatePresence>
            {currentDeck.slice(currentIndex, currentIndex + 2).map((card, index) => (
              <SwipeCard
                key={card.id}
                card={card}
                onSwipe={handleSwipe}
                isTop={index === 0}
                totalCards={currentDeck.length}
                currentIndex={currentIndex}
              />
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* プログレスバー */}
      <div className="px-4 py-3 bg-white/80 backdrop-blur-sm border-t border-gray-100">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">進捗</span>
            <span className="text-sm font-medium text-gray-800">
              {currentIndex} / {currentDeck.length}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-500 to-purple-500 h-full rounded-full transition-all duration-300"
              style={{ width: `${(currentIndex / currentDeck.length) * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}