#!/usr/bin/env python3
"""
クレンジング済みカードのレビュー用HTMLを生成
モバイル対応・No-JSで確実に動作
"""

import json
from html import escape
from datetime import datetime

def generate_review_html(input_file: str, output_file: str):
    """レビュー用HTMLの生成"""
    
    # データ読み込み
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cards = data.get('cards', [])
    
    # HTML生成
    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>化学カードレビュー - {len(cards)}枚</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Sans', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px 10px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .header h1 {{
            font-size: 24px;
            color: #2d3748;
            margin-bottom: 10px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }}
        
        .stat {{
            background: #f7fafc;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #4a5568;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #718096;
            margin-top: 2px;
        }}
        
        .filters {{
            background: white;
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .filter-row {{
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }}
        
        .filter-button {{
            padding: 8px 16px;
            border-radius: 20px;
            border: 2px solid #e2e8f0;
            background: white;
            color: #4a5568;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .filter-button:hover {{
            border-color: #667eea;
            color: #667eea;
            background: #f0f4ff;
        }}
        
        .filter-button.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
        
        .card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            position: relative;
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }}
        
        .card-id {{
            font-size: 12px;
            color: #a0aec0;
            font-family: monospace;
        }}
        
        .card-type {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .type-quick {{
            background: #e6fffa;
            color: #065666;
        }}
        
        .type-decision {{
            background: #fef5e7;
            color: #7d4004;
        }}
        
        .type-process {{
            background: #f0f4ff;
            color: #434190;
        }}
        
        .question {{
            font-size: 18px;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 12px;
            line-height: 1.5;
        }}
        
        .answer {{
            font-size: 16px;
            color: #4a5568;
            line-height: 1.6;
            padding: 12px;
            background: #f7fafc;
            border-radius: 10px;
            margin-bottom: 15px;
        }}
        
        .formula {{
            font-family: 'Courier New', monospace;
            background: #fef8e7;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        .metadata {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e2e8f0;
        }}
        
        .meta-item {{
            font-size: 12px;
            color: #718096;
        }}
        
        .meta-label {{
            font-weight: bold;
            color: #4a5568;
        }}
        
        .tags {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            margin-top: 10px;
        }}
        
        .tag {{
            display: inline-block;
            padding: 4px 10px;
            background: #edf2f7;
            color: #4a5568;
            border-radius: 10px;
            font-size: 12px;
        }}
        
        .conditions {{
            background: #e6fffa;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
        }}
        
        .conditions-title {{
            font-size: 12px;
            font-weight: bold;
            color: #065666;
            margin-bottom: 5px;
        }}
        
        .conditions-list {{
            font-size: 14px;
            color: #047857;
        }}
        
        .misconceptions {{
            background: #fee2e2;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
        }}
        
        .misconceptions-title {{
            font-size: 12px;
            font-weight: bold;
            color: #991b1b;
            margin-bottom: 5px;
        }}
        
        .misconceptions-list {{
            font-size: 14px;
            color: #dc2626;
        }}
        
        .actions {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e2e8f0;
        }}
        
        .action-button {{
            flex: 1;
            padding: 10px;
            border-radius: 10px;
            border: none;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .btn-approve {{
            background: #10b981;
            color: white;
        }}
        
        .btn-approve:hover {{
            background: #059669;
        }}
        
        .btn-edit {{
            background: #f59e0b;
            color: white;
        }}
        
        .btn-edit:hover {{
            background: #d97706;
        }}
        
        .btn-reject {{
            background: #ef4444;
            color: white;
        }}
        
        .btn-reject:hover {{
            background: #dc2626;
        }}
        
        .duplicate-badge {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: #f59e0b;
            color: white;
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: bold;
        }}
        
        .chapter-group {{
            margin-bottom: 30px;
        }}
        
        .chapter-title {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 15px;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        
        @media (max-width: 640px) {{
            .header h1 {{
                font-size: 20px;
            }}
            
            .question {{
                font-size: 16px;
            }}
            
            .answer {{
                font-size: 14px;
            }}
            
            .actions {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 化学カードレビュー</h1>
            <p style="color: #718096;">生成日: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{len(cards)}</div>
                    <div class="stat-label">総カード数</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{len([c for c in cards if c.get('type') == 'quick'])}</div>
                    <div class="stat-label">Quickカード</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{len([c for c in cards if c.get('type') == 'decision'])}</div>
                    <div class="stat-label">Decisionカード</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{len([c for c in cards if c.get('type') == 'process'])}</div>
                    <div class="stat-label">Processカード</div>
                </div>
            </div>
        </div>
"""

    # 章ごとにカードをグループ化
    chapters = {}
    for card in cards:
        chapter = card.get('chapter', '未分類')
        if chapter not in chapters:
            chapters[chapter] = []
        chapters[chapter].append(card)
    
    # 章ごとにカードを表示
    for chapter, chapter_cards in sorted(chapters.items()):
        html_content += f"""
        <div class="chapter-group">
            <div class="chapter-title">
                📚 {escape(chapter)} ({len(chapter_cards)}枚)
            </div>
"""
        
        for i, card in enumerate(chapter_cards):
            card_id = escape(card.get('id', f'unknown_{i}'))
            question = escape(card.get('question', ''))
            answer = escape(card.get('answer', ''))
            card_type = card.get('type', 'quick')
            difficulty = card.get('difficulty', 1)
            tags = card.get('tags', [])
            conditions = card.get('conditions', [])
            misconceptions = card.get('misconceptions', [])
            duplicate_count = card.get('duplicate_count', 0)
            
            html_content += f"""
            <div class="card" data-id="{card_id}">
                {'<span class="duplicate-badge">重複 ' + str(duplicate_count) + '件</span>' if duplicate_count > 1 else ''}
                
                <div class="card-header">
                    <span class="card-id">{card_id}</span>
                    <span class="card-type type-{card_type}">{card_type}</span>
                </div>
                
                <div class="question">{question}</div>
                <div class="answer">{answer}</div>
                
                {f'''<div class="conditions">
                    <div class="conditions-title">⚠️ 適用条件</div>
                    <div class="conditions-list">
                        {'<br>'.join('• ' + escape(c) for c in conditions)}
                    </div>
                </div>''' if conditions else ''}
                
                {f'''<div class="misconceptions">
                    <div class="misconceptions-title">❌ よくあるミス</div>
                    <div class="misconceptions-list">
                        {'<br>'.join('• ' + escape(m) for m in misconceptions)}
                    </div>
                </div>''' if misconceptions else ''}
                
                <div class="metadata">
                    <div class="meta-item">
                        <span class="meta-label">難易度:</span> {'★' * difficulty}
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">ページ:</span> {card.get('page', 'N/A')}
                    </div>
                </div>
                
                {f'''<div class="tags">
                    {''.join(f'<span class="tag">{escape(tag)}</span>' for tag in tags)}
                </div>''' if tags else ''}
                
                <div class="actions">
                    <button class="action-button btn-approve" onclick="markCard('{card_id}', 'approved')">
                        ✅ 承認
                    </button>
                    <button class="action-button btn-edit" onclick="markCard('{card_id}', 'edit')">
                        ✏️ 要修正
                    </button>
                    <button class="action-button btn-reject" onclick="markCard('{card_id}', 'rejected')">
                        🗑️ 削除
                    </button>
                </div>
            </div>
"""
        
        html_content += """
        </div>
"""
    
    html_content += """
    </div>
    
    <script>
        function markCard(cardId, action) {
            const card = document.querySelector(`[data-id="${cardId}"]`);
            if (card) {
                card.style.opacity = '0.5';
                card.style.pointerEvents = 'none';
                
                // ローカルストレージに保存
                const reviews = JSON.parse(localStorage.getItem('cardReviews') || '{}');
                reviews[cardId] = {
                    action: action,
                    timestamp: new Date().toISOString()
                };
                localStorage.setItem('cardReviews', JSON.stringify(reviews));
                
                // フィードバック表示
                const message = action === 'approved' ? '✅ 承認済み' :
                              action === 'edit' ? '✏️ 要修正' : '🗑️ 削除済み';
                
                const feedback = document.createElement('div');
                feedback.style.cssText = `
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: ${action === 'approved' ? '#10b981' : 
                                action === 'edit' ? '#f59e0b' : '#ef4444'};
                    color: white;
                    padding: 15px 25px;
                    border-radius: 10px;
                    font-weight: bold;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    animation: slideIn 0.3s ease;
                `;
                feedback.textContent = message;
                document.body.appendChild(feedback);
                
                setTimeout(() => feedback.remove(), 2000);
            }
        }
        
        // レビュー結果をエクスポート
        function exportReviews() {
            const reviews = localStorage.getItem('cardReviews');
            if (reviews) {
                const blob = new Blob([reviews], {type: 'application/json'});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'card-reviews.json';
                a.click();
            }
        }
    </script>
    
    <style>
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    </style>
</body>
</html>"""
    
    # HTMLファイル保存
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Review HTML generated: {output_file}")
    print(f"Total cards: {len(cards)}")
    print(f"Chapters: {len(chapters)}")

if __name__ == '__main__':
    generate_review_html(
        'public/learning-data-v2.json',
        'public/card-review.html'
    )