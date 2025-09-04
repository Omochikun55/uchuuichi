#!/usr/bin/env python3
"""
宇宙一わかりやすい化学（無機）PDFから高品質カード抽出
"""

import sys
sys.path.append('/home/mochi/uchuichi-app/pdf-extractor')
from extract_uchuichi_pdf import UchuichiExtractor
from pathlib import Path

def main():
    """無機化学PDF処理"""
    pdf_path = Path("/home/mochi/uchuichi-app/PDF/宇宙一わかりやすい化学（無機）/【無機・化学】宇宙一わかりやすい化学.pdf")
    output_dir = Path("/home/mochi/uchuichi-app/pdf-extractor/output_muki")
    
    # 抽出実行（最初の50ページ）
    extractor = UchuichiExtractor(pdf_path, output_dir, max_pages=50)
    cards = extractor.process_pdf(batch_size=10)
    
    # 結果保存
    output_file = extractor.save_results()
    
    print(f"\n✅ 無機化学処理完了！")
    print(f"出力: {output_file}")

if __name__ == "__main__":
    main()