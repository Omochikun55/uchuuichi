'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, BookOpen, Brain, Atom, FlaskRound, Zap, Calculator, Waves } from 'lucide-react';

interface Category {
  id: string;
  name: string;
  subject: 'chemistry' | 'physics';
  icon: any;
  color: string;
  cardCount: number;
  chapters: string[];
}

export default function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await fetch('/learning-data.json');
      const data = await response.json();
      const cards = data.cards;

      // カテゴリーを集計
      const categoryMap = new Map<string, Category>();

      // 化学カテゴリー
      const chemChapters = [...new Set(cards.filter((c: any) => c.subject === 'chemistry').map((c: any) => c.chapter))];
      const chemCards = cards.filter((c: any) => c.subject === 'chemistry');
      
      if (chemChapters.length > 0) {
        categoryMap.set('chemistry-all', {
          id: 'chemistry-all',
          name: '化学（全体）',
          subject: 'chemistry',
          icon: FlaskRound,
          color: 'from-blue-400 to-cyan-400',
          cardCount: chemCards.length,
          chapters: chemChapters.filter(Boolean)
        });
      }

      // 物理カテゴリー
      const physChapters = [...new Set(cards.filter((c: any) => c.subject === 'physics').map((c: any) => c.chapter))];
      const physCards = cards.filter((c: any) => c.subject === 'physics');
      
      if (physChapters.length > 0) {
        categoryMap.set('physics-all', {
          id: 'physics-all',
          name: '物理（全体）',
          subject: 'physics',
          icon: Atom,
          color: 'from-purple-400 to-indigo-400',
          cardCount: physCards.length,
          chapters: physChapters.filter(Boolean)
        });
      }

      // チャプター別カテゴリー（化学）
      const chemistryChapterIcons: { [key: string]: any } = {
        '物質の成り立ち': Flask,
        '物質の分離': Zap,
        '原子の構造': Atom,
        '化学反応': Brain,
        '酸と塩基': Flask,
        '酸化還元': Zap,
        '物質量': Calculator,
        '気体の性質': Flask,
      };

      chemChapters.forEach(chapter => {
        if (chapter) {
          const chapterCards = cards.filter((c: any) => c.subject === 'chemistry' && c.chapter === chapter);
          categoryMap.set(`chem-${chapter}`, {
            id: `chem-${chapter}`,
            name: `化学: ${chapter}`,
            subject: 'chemistry',
            icon: chemistryChapterIcons[chapter] || BookOpen,
            color: 'from-blue-400 to-blue-600',
            cardCount: chapterCards.length,
            chapters: [chapter]
          });
        }
      });

      // チャプター別カテゴリー（物理）
      const physicsChapterIcons: { [key: string]: any } = {
        '力学': Calculator,
        'エネルギー': Zap,
        '波動': Waves,
        '電磁気': Zap,
        '原子': Atom,
      };

      physChapters.forEach(chapter => {
        if (chapter) {
          const chapterCards = cards.filter((c: any) => c.subject === 'physics' && c.chapter === chapter);
          categoryMap.set(`phys-${chapter}`, {
            id: `phys-${chapter}`,
            name: `物理: ${chapter}`,
            subject: 'physics',
            icon: physicsChapterIcons[chapter] || BookOpen,
            color: 'from-purple-400 to-purple-600',
            cardCount: chapterCards.length,
            chapters: [chapter]
          });
        }
      });

      setCategories(Array.from(categoryMap.values()));
    } catch (error) {
      console.error('Failed to load categories:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">カテゴリーを読み込み中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* ヘッダー */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-100 px-4 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <Link href="/" className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-xl font-bold text-gray-800">カテゴリー選択</h1>
          <div className="w-9" />
        </div>
      </div>

      {/* カテゴリーグリッド */}
      <div className="px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* 科目別セクション */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">科目別</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {categories.filter(c => c.id.includes('-all')).map(category => (
                <Link
                  key={category.id}
                  href={`/study?subject=${category.subject}`}
                  className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-all transform hover:scale-105"
                >
                  <div className={`inline-flex p-3 rounded-xl bg-gradient-to-r ${category.color} mb-4`}>
                    <category.icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-800 mb-2">{category.name}</h3>
                  <p className="text-sm text-gray-600 mb-3">{category.cardCount}枚のカード</p>
                  <div className="flex flex-wrap gap-2">
                    {category.chapters.slice(0, 3).map(chapter => (
                      <span key={chapter} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        {chapter}
                      </span>
                    ))}
                    {category.chapters.length > 3 && (
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        +{category.chapters.length - 3}
                      </span>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* チャプター別セクション（化学） */}
          {categories.some(c => c.id.startsWith('chem-') && !c.id.includes('-all')) && (
            <div className="mb-8">
              <h2 className="text-lg font-semibold text-gray-700 mb-4">化学 - チャプター別</h2>
              <div className="grid md:grid-cols-3 gap-4">
                {categories
                  .filter(c => c.id.startsWith('chem-') && !c.id.includes('-all'))
                  .map(category => (
                    <Link
                      key={category.id}
                      href={`/study?subject=chemistry&chapter=${encodeURIComponent(category.chapters[0])}`}
                      className="bg-white rounded-xl shadow-md p-4 hover:shadow-lg transition-all transform hover:scale-105"
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <div className={`p-2 rounded-lg bg-gradient-to-r ${category.color}`}>
                          <category.icon className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-800 text-sm">{category.chapters[0]}</h4>
                          <p className="text-xs text-gray-500">{category.cardCount}枚</p>
                        </div>
                      </div>
                    </Link>
                  ))}
              </div>
            </div>
          )}

          {/* チャプター別セクション（物理） */}
          {categories.some(c => c.id.startsWith('phys-') && !c.id.includes('-all')) && (
            <div className="mb-8">
              <h2 className="text-lg font-semibold text-gray-700 mb-4">物理 - チャプター別</h2>
              <div className="grid md:grid-cols-3 gap-4">
                {categories
                  .filter(c => c.id.startsWith('phys-') && !c.id.includes('-all'))
                  .map(category => (
                    <Link
                      key={category.id}
                      href={`/study?subject=physics&chapter=${encodeURIComponent(category.chapters[0])}`}
                      className="bg-white rounded-xl shadow-md p-4 hover:shadow-lg transition-all transform hover:scale-105"
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <div className={`p-2 rounded-lg bg-gradient-to-r ${category.color}`}>
                          <category.icon className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-800 text-sm">{category.chapters[0]}</h4>
                          <p className="text-xs text-gray-500">{category.cardCount}枚</p>
                        </div>
                      </div>
                    </Link>
                  ))}
              </div>
            </div>
          )}

          {/* 学習モード */}
          <div className="mt-12">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">特別学習モード</h2>
            <div className="grid md:grid-cols-3 gap-4">
              <Link
                href="/study?mode=weak"
                className="bg-gradient-to-r from-red-100 to-pink-100 rounded-xl p-6 hover:shadow-lg transition-all"
              >
                <div className="text-red-600 mb-2">🎯</div>
                <h3 className="font-bold text-gray-800 mb-1">弱点克服</h3>
                <p className="text-sm text-gray-600">苦手な問題を集中学習</p>
              </Link>

              <Link
                href="/study?mode=quick"
                className="bg-gradient-to-r from-blue-100 to-cyan-100 rounded-xl p-6 hover:shadow-lg transition-all"
              >
                <div className="text-blue-600 mb-2">⚡</div>
                <h3 className="font-bold text-gray-800 mb-1">クイック復習</h3>
                <p className="text-sm text-gray-600">10問を5分で高速復習</p>
              </Link>

              <Link
                href="/study?mode=new"
                className="bg-gradient-to-r from-purple-100 to-indigo-100 rounded-xl p-6 hover:shadow-lg transition-all"
              >
                <div className="text-purple-600 mb-2">✨</div>
                <h3 className="font-bold text-gray-800 mb-1">新規学習</h3>
                <p className="text-sm text-gray-600">まだ学習していない問題</p>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}