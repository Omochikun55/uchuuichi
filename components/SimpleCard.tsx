'use client';

import { useState } from 'react';
import { FlashCard } from '@/lib/types';

interface SimpleCardProps {
  card: FlashCard;
  onNext: () => void;
}

export default function SimpleCard({ card, onNext }: SimpleCardProps) {
  const [showAnswer, setShowAnswer] = useState(false);

  return (
    <div className="w-full max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
      <div className="mb-4">
        <h3 className="text-xl font-bold">{card.question}</h3>
      </div>
      
      {!showAnswer ? (
        <button
          onClick={() => setShowAnswer(true)}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
        >
          答えを表示
        </button>
      ) : (
        <>
          <div className="mb-4 p-4 bg-gray-100 rounded">
            <p className="text-lg">{card.answer}</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={onNext}
              className="flex-1 bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600"
            >
              わからない
            </button>
            <button
              onClick={onNext}
              className="flex-1 bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600"
            >
              わかる
            </button>
          </div>
        </>
      )}
    </div>
  );
}