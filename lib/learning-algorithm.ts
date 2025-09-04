// 学習アルゴリズム（SM-2アルゴリズムベース）
import { FlashCard } from './types';

export class LearningAlgorithm {
  // 次回復習日を計算
  static calculateNextReview(
    card: FlashCard,
    quality: number // 0-5: 0=完全に忘れた, 5=完璧
  ): { nextReview: Date; confidence: number } {
    const now = new Date();
    let interval = 1; // デフォルト1日後
    let confidence = card.confidence || 50;

    // 品質に基づいて信頼度を更新
    if (quality >= 3) {
      confidence = Math.min(100, confidence + (quality - 3) * 15);
    } else {
      confidence = Math.max(0, confidence - (3 - quality) * 20);
    }

    // 信頼度に基づいて次回復習間隔を計算
    if (confidence >= 90) {
      interval = 7; // 1週間後
    } else if (confidence >= 70) {
      interval = 3; // 3日後
    } else if (confidence >= 50) {
      interval = 1; // 1日後
    } else if (confidence >= 30) {
      interval = 0.25; // 6時間後
    } else {
      interval = 0.042; // 1時間後
    }

    // 連続正解回数を考慮
    if (card.reviewCount > 0) {
      const successRate = card.correctCount / card.reviewCount;
      if (successRate > 0.8) {
        interval *= 1.5;
      } else if (successRate < 0.5) {
        interval *= 0.5;
      }
    }

    const nextReview = new Date(now.getTime() + interval * 24 * 60 * 60 * 1000);

    return { nextReview, confidence };
  }

  // カードの優先度を計算（低いほど優先）
  static getCardPriority(card: FlashCard): number {
    const now = new Date();
    let priority = 0;

    // 新規カードは最優先
    if (card.reviewCount === 0) {
      return 0;
    }

    // 復習期限を過ぎている場合
    if (card.nextReview && card.nextReview < now) {
      const overdueDays = (now.getTime() - card.nextReview.getTime()) / (24 * 60 * 60 * 1000);
      priority = -overdueDays; // 期限切れが長いほど優先
    } else if (card.nextReview) {
      const daysUntilReview = (card.nextReview.getTime() - now.getTime()) / (24 * 60 * 60 * 1000);
      priority = daysUntilReview;
    }

    // 信頼度が低いカードを優先
    priority -= (100 - card.confidence) / 50;

    // 難易度が高いカードを優先
    priority -= card.difficulty * 2;

    return priority;
  }

  // 学習セッション用のカードデッキを生成
  static generateStudyDeck(
    cards: FlashCard[],
    deckSize: number = 20,
    focusOnWeak: boolean = true
  ): FlashCard[] {
    const now = new Date();
    const deck: FlashCard[] = [];

    // カードを優先度でソート
    const sortedCards = [...cards].sort((a, b) => {
      return this.getCardPriority(a) - this.getCardPriority(b);
    });

    // 新規カード、復習カード、苦手カードのバランスを取る
    const newCards = sortedCards.filter(c => c.reviewCount === 0);
    const dueCards = sortedCards.filter(c => 
      c.nextReview && c.nextReview <= now && c.reviewCount > 0
    );
    const weakCards = sortedCards.filter(c => 
      c.confidence < 50 && c.reviewCount > 0
    );

    // デッキ構成
    const newCardLimit = Math.floor(deckSize * 0.3); // 30%は新規
    const weakCardLimit = Math.floor(deckSize * 0.4); // 40%は苦手
    const dueCardLimit = deckSize - newCardLimit - weakCardLimit; // 残りは復習期限

    // デッキに追加
    deck.push(...newCards.slice(0, newCardLimit));
    deck.push(...weakCards.slice(0, weakCardLimit));
    deck.push(...dueCards.slice(0, dueCardLimit));

    // 不足分を他のカードで補充
    if (deck.length < deckSize) {
      const remaining = sortedCards.filter(c => !deck.includes(c));
      deck.push(...remaining.slice(0, deckSize - deck.length));
    }

    // シャッフル（最初の数枚は優先度高いものを維持）
    const fixedCount = 3;
    const toShuffle = deck.slice(fixedCount);
    for (let i = toShuffle.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [toShuffle[i], toShuffle[j]] = [toShuffle[j], toShuffle[i]];
    }

    return [...deck.slice(0, fixedCount), ...toShuffle];
  }

  // 学習統計を計算
  static calculateStats(cards: FlashCard[]): {
    mastered: number;
    learning: number;
    new: number;
    averageConfidence: number;
    weakestTopics: string[];
  } {
    const mastered = cards.filter(c => c.confidence >= 80).length;
    const learning = cards.filter(c => c.confidence >= 30 && c.confidence < 80).length;
    const newCards = cards.filter(c => c.reviewCount === 0).length;
    
    const totalConfidence = cards.reduce((sum, c) => sum + c.confidence, 0);
    const averageConfidence = cards.length > 0 ? totalConfidence / cards.length : 0;

    // タグ別の弱点を特定
    const tagStats: { [key: string]: { total: number; weak: number } } = {};
    cards.forEach(card => {
      card.tags?.forEach(tag => {
        if (!tagStats[tag]) {
          tagStats[tag] = { total: 0, weak: 0 };
        }
        tagStats[tag].total++;
        if (card.confidence < 50) {
          tagStats[tag].weak++;
        }
      });
    });

    const weakestTopics = Object.entries(tagStats)
      .filter(([_, stats]) => stats.weak / stats.total > 0.5)
      .sort((a, b) => (b[1].weak / b[1].total) - (a[1].weak / a[1].total))
      .slice(0, 3)
      .map(([tag]) => tag);

    return {
      mastered,
      learning,
      new: newCards,
      averageConfidence,
      weakestTopics
    };
  }
}