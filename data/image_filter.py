import os
import shutil
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class ImageFilter:
    def __init__(self, images_folder: str):
        self.images_folder = Path(images_folder)
        self.filtered_folder = self.images_folder.parent / "filtered_images"
        
        self.inappropriate_keywords = {'강간', '성매매'}
        
        self.location_keywords = {
            '우에스카', '테루엘', '사라고사', '알메리아', '카디스', '코르도바', 
            '그라나다', '우엘바', '하엔', '말라가', '세비야', '라코루냐', 
            '루고', '오렌세', '폰테베드라', '알라바', '기푸스코아', '비스카야',
            '알바세테', '시우다드레알', '쿠엔카', '과달라하라', '톨레도',
            '알리칸테', '카스텔론', '발렌시아', '아빌라', '부르고스', '레온',
            '팔렌시아', '살라망카', '세고비아', '소리아', '바야돌리드', '사모라',
            '아스투리아스', '바다호스', '카세레스', '바르셀로나', '지로나',
            '레이다', '타라고나', '칸타브리아', '세우타', '멜리야', '라 리오하',
            '마드리드', '무르시아', '나바라', '엘이에로', '라 고메라', '라 팔마',
            '란사로테', '포르멘테라', '테네리페', '이비자', '마요르카', '미노르카',
            '서울', '부산', '대구', '인천', '광주', '대전', '울산', '제주',
            '경기도', '강원도', '충청도', '전라도', '경상도', '평양', '개성',
            '도쿄', '오사카', '요코하마', '나고야', '베이징', '상하이', '홍콩',
            '런던', '파리', '베를린', '로마', '뉴욕', '로스앤젤레스', '시카고',
            '모스크바', '상트페테르부르크', '시드니', '멜버른', '토론토', '밴쿠버',
            'spain', 'korea', 'japan', 'china', 'america', 'france', 'germany',
            'italy', 'russia', 'australia', 'canada', 'london', 'paris',
            'berlin', 'rome', 'tokyo', 'seoul', 'busan', 'moscow', 'sydney'
        }
    
    def _extract_keyword(self, filename: str) -> str:
        stem = Path(filename).stem
        if '_' not in stem:
            return ""
        return stem.split('_', 1)[1].strip()
    
    def _should_filter(self, keyword: str) -> str:
        keyword_lower = keyword.lower()
        
        if not keyword.strip():
            return "empty_keyword"
        
        if len(keyword.strip()) == 1 and keyword.isalpha() and keyword.isascii():
            return "single_english_letter"
        
        if any(inappropriate in keyword_lower for inappropriate in self.inappropriate_keywords):
            return "inappropriate"
        
        if any(location in keyword_lower for location in self.location_keywords):
            return "locations"
        
        return ""
    
    def analyze_images(self) -> Dict[str, List[str]]:
        if not self.images_folder.exists():
            raise FileNotFoundError(f"Images folder not found: {self.images_folder}")
        
        png_files = [f.name for f in self.images_folder.glob("*.png")]
        filtered_files = defaultdict(list)
        keyword_to_files = defaultdict(list)
        
        for filename in png_files:
            keyword = self._extract_keyword(filename)
            filter_reason = self._should_filter(keyword)
            
            if filter_reason:
                filtered_files[filter_reason].append(filename)
            
            if keyword:
                keyword_to_files[keyword].append(filename)
        
        for keyword, files in keyword_to_files.items():
            if len(files) > 1:
                filtered_files["duplicates"].extend(files[1:])
        
        return dict(filtered_files)
    
    def filter_images(self, confirm: bool = True) -> int:
        filtered_files = self.analyze_images()
        all_files_to_move = list(set(
            file for files in filtered_files.values() for file in files
        ))
        
        if not all_files_to_move:
            return 0
        
        total_filtered = sum(len(files) for files in filtered_files.values())
        print(f"Filtering analysis:")
        for category, files in filtered_files.items():
            print(f"  {category}: {len(files)} files")
        print(f"  Total to filter: {total_filtered} files")
        
        if confirm:
            response = input(f"Move {len(all_files_to_move)} files? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                return 0
        
        self.filtered_folder.mkdir(exist_ok=True)
        moved_count = 0
        
        for filename in all_files_to_move:
            src = self.images_folder / filename
            dst = self.filtered_folder / filename
            
            if src.exists():
                try:
                    shutil.move(str(src), str(dst))
                    moved_count += 1
                except Exception as e:
                    print(f"Error moving {filename}: {e}")
        
        print(f"Moved {moved_count} files to {self.filtered_folder}")
        return moved_count