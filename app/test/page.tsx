'use client';

import { useState } from 'react';
import SimpleCard from '@/components/SimpleCard';

export default function TestPage() {
  const [currentIndex, setCurrentIndex] = useState(0);
  
  const testCards = [
    {
      id: 'test1',
      question: 'テスト問題1: 水の化学式は？',
      answer: 'H₂O',
      type: 'definition' as const,
      difficulty: 1,
      subject: 'chemistry' as const,
      chapter: 'test',
      page: 1,
      reviewCount: 0,
      correctCount: 0,
      confidence: 0,
      tags: []
    },
    {
      id: 'test2',
      question: 'テスト問題2: 光の速さは？',
      answer: '約30万km/秒',
      type: 'definition' as const,
      difficulty: 2,
      subject: 'physics' as const,
      chapter: 'test',
      page: 1,
      reviewCount: 0,
      correctCount: 0,
      confidence: 0,
      tags: []
    }
  ];

  const handleNext = () => {
    setCurrentIndex((prev) => (prev + 1) % testCards.length);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-2xl font-bold text-center mb-8">テストページ</h1>
      <SimpleCard 
        card={testCards[currentIndex]} 
        onNext={handleNext}
      />
      <p className="text-center mt-4">
        カード {currentIndex + 1} / {testCards.length}
      </p>
    </div>
  );
}