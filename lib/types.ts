// 型定義ファイル
export interface FlashCard {
  id: string;
  question: string;
  answer: string;
  type: 'definition' | 'formula' | 'separation' | 'state_change' | 'application';
  difficulty: 1 | 2 | 3 | 4 | 5;
  subject: 'chemistry' | 'physics';
  chapter: string;
  page?: number;
  imageUrl?: string;
  lastReviewed?: Date;
  reviewCount: number;
  correctCount: number;
  confidence: number; // 0-100
  nextReview?: Date;
  tags?: string[];
}

export interface StudySession {
  id: string;
  userId: string;
  startTime: Date;
  endTime?: Date;
  cardsStudied: number;
  correctAnswers: number;
  subject: string;
  chapter: string;
}

export interface UserProgress {
  userId: string;
  totalCards: number;
  masteredCards: number;
  learningCards: number;
  newCards: number;
  streakDays: number;
  lastStudyDate?: Date;
  weeklyGoal: number;
  weeklyProgress: number;
}

export interface ChapterData {
  id: string;
  subject: 'chemistry' | 'physics';
  chapterNumber: number;
  title: string;
  totalCards: number;
  progress: number;
  difficulty: number;
}

export type SwipeDirection = 'left' | 'right' | 'up' | 'down';

export interface SwipeAction {
  direction: SwipeDirection;
  action: 'know' | 'dont_know' | 'favorite' | 'skip';
  confidence?: number;
}