import os
import re
from pathlib import Path
from typing import List, Set, Dict
from collections import defaultdict
import shutil

class AACImageFilter:
    def __init__(self, images_folder: str):
        self.images_folder = Path(images_folder)
        self.filtered_folder = Path(images_folder).parent / "filtered_images"
        
        self.inappropriate_keywords = {
            '강간', '성매매'
        }
        
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
        
    def extract_keyword_from_filename(self, filename: str) -> str:
        stem = Path(filename).stem
        if '_' not in stem:
            return ""
        parts = stem.split('_', 1)
        if len(parts) == 2:
            return parts[1].strip()
        return ""
    
    def is_inappropriate_content(self, keyword: str) -> bool:
        keyword_lower = keyword.lower()
        return any(inappropriate in keyword_lower for inappropriate in self.inappropriate_keywords)
    
    def is_location_name(self, keyword: str) -> bool:
        keyword_lower = keyword.lower()
        return any(location in keyword_lower for location in self.location_keywords)
    
    def is_empty_keyword(self, keyword: str) -> bool:
        return keyword.strip() == ""
    
    def is_single_english_letter(self, keyword: str) -> bool:
        keyword = keyword.strip()
        return len(keyword) == 1 and keyword.isalpha() and keyword.isascii()
    
    def find_duplicate_keywords(self, filenames: List[str]) -> Dict[str, List[str]]:
        keyword_to_files = defaultdict(list)
        
        for filename in filenames:
            keyword = self.extract_keyword_from_filename(filename)
            if keyword:
                keyword_to_files[keyword].append(filename)
        
        duplicates = {k: v for k, v in keyword_to_files.items() if len(v) > 1}
        return duplicates
    
    def analyze_images(self) -> Dict[str, List[str]]:
        if not self.images_folder.exists():
            print(f"Error: 이미지 폴더가 존재하지 않습니다: {self.images_folder}")
            return {}
        
        png_files = [f.name for f in self.images_folder.glob("*.png")]
        
        filtered_files = {
            "inappropriate": [],
            "locations": [],
            "empty_keyword": [],
            "single_english_letter": [],
            "duplicates": []
        }
        
        for filename in png_files:
            keyword = self.extract_keyword_from_filename(filename)
            if self.is_inappropriate_content(keyword):
                filtered_files["inappropriate"].append(filename)
        
        for filename in png_files:
            keyword = self.extract_keyword_from_filename(filename)
            if self.is_location_name(keyword):
                filtered_files["locations"].append(filename)
        
        for filename in png_files:
            keyword = self.extract_keyword_from_filename(filename)
            if self.is_empty_keyword(keyword):
                filtered_files["empty_keyword"].append(filename)
        
        for filename in png_files:
            keyword = self.extract_keyword_from_filename(filename)
            if self.is_single_english_letter(keyword):
                filtered_files["single_english_letter"].append(filename)
        
        duplicates = self.find_duplicate_keywords(png_files)
        for keyword, files in duplicates.items():
            filtered_files["duplicates"].extend(files[1:])
        
        return filtered_files
    
    def print_analysis_report(self, filtered_files: Dict[str, List[str]]):
        total_filtered = sum(len(files) for files in filtered_files.values())
        
        print(f"\n필터링 결과:")
        print(f"  부적절한 내용: {len(filtered_files['inappropriate'])}개")
        print(f"  지역명: {len(filtered_files['locations'])}개")
        print(f"  공백 키워드: {len(filtered_files['empty_keyword'])}개")
        print(f"  영어 한글자: {len(filtered_files['single_english_letter'])}개")
        print(f"  중복 키워드: {len(filtered_files['duplicates'])}개")
        print(f"  총 필터링 대상: {total_filtered}개")
    
    def move_filtered_images(self, filtered_files: Dict[str, List[str]], confirm: bool = True) -> int:
        all_files_to_move = []
        for category, files in filtered_files.items():
            all_files_to_move.extend(files)
        
        all_files_to_move = list(set(all_files_to_move))
        
        if not all_files_to_move:
            return 0
        
        if confirm:
            response = input(f"\n{len(all_files_to_move)}개 파일을 이동하시겠습니까? (y/N): ").strip().lower()
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
        
        print(f"{moved_count}개 파일이 {self.filtered_folder}로 이동되었습니다.")
        return moved_count
    
    def run_filter(self, move_files: bool = False, confirm: bool = True):
        filtered_files = self.analyze_images()
        self.print_analysis_report(filtered_files)
        
        if move_files:
            return self.move_filtered_images(filtered_files, confirm=confirm)
        return 0


def main():
    images_folder = "data/images"
    filter_tool = AACImageFilter(images_folder)
    
    filter_tool.run_filter(move_files=False)
    
    response = input("\n실제 이동을 진행하시겠습니까? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        moved_count = filter_tool.run_filter(move_files=True, confirm=False)
        print(f"완료: {moved_count}개 파일 처리됨")


if __name__ == "__main__":
    main()