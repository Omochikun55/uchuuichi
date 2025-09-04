'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { BookOpen, Trophy, Zap, TrendingUp, Clock, Target, Star, ChevronRight } from 'lucide-react';
import { FlashCard } from '@/lib/types';
import { LearningAlgorithm } from '@/lib/learning-algorithm';

export default function HomePage() {
  const [stats, setStats] = useState({
    totalCards: 0,
    masteredCards: 0,
    learningCards: 0,
    newCards: 0,
    todayStudied: 0,
    streakDays: 0,
    chemistryProgress: 0,
    physicsProgress: 0,
  });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      // カードデータを読み込み
      const response = await fetch('/learning-data.json');
      const data = await response.json();
      const cards: FlashCard[] = data.cards;

      // 保存された進捗を読み込み
      const saved = localStorage.getItem('uchuichi-progress');
      let updatedCards = cards;
      
      if (saved) {
        const progress = JSON.parse(saved);
        updatedCards = cards.map(card => {
          const savedCard = progress.find((p: { id: string }) => p.id === card.id);
          if (savedCard) {
            return { ...card, ...savedCard };
          }
          return card;
        });
      }

      // 統計を計算
      const algorithmStats = LearningAlgorithm.calculateStats(updatedCards);
      const chemCards = updatedCards.filter(c => c.subject === 'chemistry');
      const physCards = updatedCards.filter(c => c.subject === 'physics');
      
      const chemStats = LearningAlgorithm.calculateStats(chemCards);
      const physStats = LearningAlgorithm.calculateStats(physCards);

      // 今日の学習数を計算
      const today = new Date().toDateString();
      const todayCards = updatedCards.filter(c => 
        c.lastReviewed && new Date(c.lastReviewed).toDateString() === today
      );

      setStats({
        totalCards: cards.length,
        masteredCards: algorithmStats.mastered,
        learningCards: algorithmStats.learning,
        newCards: algorithmStats.new,
        todayStudied: todayCards.length,
        streakDays: calculateStreak(updatedCards),
        chemistryProgress: chemCards.length > 0 
          ? Math.round((chemStats.mastered / chemCards.length) * 100) 
          : 0,
        physicsProgress: physCards.length > 0 
          ? Math.round((physStats.mastered / physCards.length) * 100) 
          : 0,
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const calculateStreak = (cards: FlashCard[]): number => {
    const dates = cards
      .filter(c => c.lastReviewed)
      .map(c => new Date(c.lastReviewed!).toDateString())
      .filter((date, index, self) => self.indexOf(date) === index)
      .sort((a, b) => new Date(b).getTime() - new Date(a).getTime());

    if (dates.length === 0) return 0;

    let streak = 0;
    const today = new Date();
    
    for (let i = 0; i < dates.length; i++) {
      const date = new Date(dates[i]);
      const expectedDate = new Date(today);
      expectedDate.setDate(expectedDate.getDate() - i);
      
      if (date.toDateString() === expectedDate.toDateString()) {
        streak++;
      } else {
        break;
      }
    }

    return streak;
  };

  const quickStartOptions = [
    {
      title: '弱点克服',
      description: '苦手な問題を集中学習',
      icon: Target,
      color: 'from-red-400 to-pink-400',
      link: '/study?mode=weak',
    },
    {
      title: 'クイック復習',
      description: '5分で10問チャレンジ',
      icon: Clock,
      color: 'from-blue-400 to-cyan-400',
      link: '/study?mode=quick',
    },
    {
      title: '新規学習',
      description: 'まだ学習していない問題',
      icon: Star,
      color: 'from-purple-400 to-indigo-400',
      link: '/study?mode=new',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* ヒーローセクション */}
      <div className="px-4 pt-8 pb-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">
              ケミカルマスター
            </h1>
            <p className="text-xl text-gray-600">宇宙一わかりやすい化学の高速学習アプリ</p>
          </div>

          {/* 統計カード */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-2">
                <BookOpen className="w-8 h-8 text-blue-500" />
                <span className="text-xs text-gray-500">総カード数</span>
              </div>
              <div className="text-2xl font-bold text-gray-800">{stats.totalCards.toLocaleString()}</div>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-2">
                <Trophy className="w-8 h-8 text-yellow-500" />
                <span className="text-xs text-gray-500">習得済み</span>
              </div>
              <div className="text-2xl font-bold text-gray-800">{stats.masteredCards.toLocaleString()}</div>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-2">
                <Zap className="w-8 h-8 text-green-500" />
                <span className="text-xs text-gray-500">連続学習</span>
              </div>
              <div className="text-2xl font-bold text-gray-800">{stats.streakDays}日</div>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-2">
                <TrendingUp className="w-8 h-8 text-purple-500" />
                <span className="text-xs text-gray-500">今日の学習</span>
              </div>
              <div className="text-2xl font-bold text-gray-800">{stats.todayStudied}</div>
            </div>
          </div>

          {/* 化学分野別進捗 */}
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">化学分野別進捗</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-600">理論化学</span>
                  <span className="text-sm font-medium">36カード</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div className="bg-gradient-to-r from-blue-400 to-blue-600 h-full rounded-full" style={{ width: '28%' }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-600">無機化学</span>
                  <span className="text-sm font-medium">21カード</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div className="bg-gradient-to-r from-green-400 to-green-600 h-full rounded-full" style={{ width: '16%' }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-600">有機化学</span>
                  <span className="text-sm font-medium">28カード</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div className="bg-gradient-to-r from-purple-400 to-purple-600 h-full rounded-full" style={{ width: '22%' }} />
                </div>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t text-center">
              <span className="text-sm text-gray-500">総カード数: 128枚</span>
            </div>
          </div>

          {/* メイン学習ボタン */}
          <Link
            href="/study"
            className="block w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all transform hover:scale-105 mb-8"
          >
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold mb-2">学習を始める</h2>
                <p className="text-blue-100">
                  {stats.newCards > 0 
                    ? `${stats.newCards}枚の新規カードがあります`
                    : '復習カードで知識を定着させましょう'}
                </p>
              </div>
              <div className="bg-white/20 rounded-full p-4">
                <ChevronRight className="w-8 h-8" />
              </div>
            </div>
          </Link>

          {/* クイックスタートオプション */}
          <div className="grid md:grid-cols-3 gap-4 mb-6">
            {quickStartOptions.map((option, index) => (
              <Link
                key={index}
                href={option.link}
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all transform hover:scale-105"
              >
                <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${option.color} mb-4`}>
                  <option.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-800 mb-1">{option.title}</h3>
                <p className="text-sm text-gray-600">{option.description}</p>
              </Link>
            ))}
          </div>

          {/* カテゴリー選択ボタン */}
          <Link
            href="/categories"
            className="block w-full bg-white border-2 border-gray-200 hover:border-blue-400 text-gray-700 rounded-xl p-6 shadow-md hover:shadow-lg transition-all"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <BookOpen className="w-6 h-6 text-gray-500" />
                <div>
                  <h3 className="font-semibold text-gray-800">カテゴリー別学習</h3>
                  <p className="text-sm text-gray-500">教科・チャプター別に選んで学習</p>
                </div>
              </div>
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </div>
          </Link>

          {/* フッター */}
          <div className="mt-12 text-center text-sm text-gray-500">
            <p>PDFから自動生成された{stats.totalCards.toLocaleString()}枚の学習カード</p>
            <p className="mt-1">Mikan風の高速スワイプで効率的に学習</p>
          </div>
        </div>
      </div>
    </div>
  );
}
