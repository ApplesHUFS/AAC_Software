import os
import re
from pathlib import Path
from typing import List, Set, Dict
from collections import defaultdict
import shutil

class AACImageFilter:
    def __init__(self, images_folder: str):
        self.images_folder = Path(images_folder)
        self.backup_folder = Path(images_folder).parent / "filtered_images_backup"
        
        # 선정적인 키워드 리스트
        self.inappropriate_keywords = {
            '강간', '성매매', '섹스', '성관계', '성행위', '포르노', '야동', 
            '성기', '생식기', '유방', '가슴', '엉덩이', '성적', '야한', 
            '에로', '음란', '변태', '자위', '오르가슴', '섹시', '벗은', 
            '나체', '누드', '속옷', '브라', '팬티', '콘돔', '피임',
            'sex', 'porn', 'nude', 'naked', 'breast', 'penis', 'vagina',
            'erotic', 'sexy', 'masturbation', 'orgasm', 'condom'
        }
        
        # 나라/도시 이름 리스트 (사용자가 제공한 예시 + 추가)
        self.location_keywords = {
            # 스페인 지역들
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
            
            # 추가 나라/도시들
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
        """파일명에서 키워드 추출"""
        stem = Path(filename).stem  # 확장자 제거
        if '_' in stem:
            parts = stem.split('_', 1)
            if len(parts) == 2:
                return parts[1].strip()
        return ""
    
    def is_inappropriate_content(self, keyword: str) -> bool:
        """선정적인 내용인지 확인"""
        keyword_lower = keyword.lower()
        return any(inappropriate in keyword_lower for inappropriate in self.inappropriate_keywords)
    
    def is_location_name(self, keyword: str) -> bool:
        """지역명인지 확인"""
        keyword_lower = keyword.lower()
        return any(location in keyword_lower for location in self.location_keywords)
    
    def is_empty_keyword(self, keyword: str) -> bool:
        """키워드가 공백인지 확인"""
        return keyword.strip() == ""
    
    def find_duplicate_keywords(self, filenames: List[str]) -> Dict[str, List[str]]:
        """중복 키워드 찾기"""
        keyword_to_files = defaultdict(list)
        
        for filename in filenames:
            keyword = self.extract_keyword_from_filename(filename)
            if keyword:  # 공백이 아닌 경우만
                keyword_to_files[keyword].append(filename)
        
        # 중복된 키워드만 반환
        duplicates = {k: v for k, v in keyword_to_files.items() if len(v) > 1}
        return duplicates
    
    def analyze_images(self) -> Dict[str, List[str]]:
        """이미지 분석하여 필터링 대상 찾기"""
        if not self.images_folder.exists():
            print(f"이미지 폴더가 존재하지 않습니다: {self.images_folder}")
            return {}
        
        # PNG 파일만 찾기
        png_files = [f.name for f in self.images_folder.glob("*.png")]
        print(f"총 {len(png_files)}개의 PNG 파일을 찾았습니다.")
        
        filtered_files = {
            "inappropriate": [],
            "locations": [],
            "empty_keyword": [],
            "duplicates": []
        }
        
        # 1. 선정적인 내용
        for filename in png_files:
            keyword = self.extract_keyword_from_filename(filename)
            if self.is_inappropriate_content(keyword):
                filtered_files["inappropriate"].append(filename)
        
        # 2. 지역명
        for filename in png_files:
            keyword = self.extract_keyword_from_filename(filename)
            if self.is_location_name(keyword):
                filtered_files["locations"].append(filename)
        
        # 3. 공백 키워드
        for filename in png_files:
            keyword = self.extract_keyword_from_filename(filename)
            if self.is_empty_keyword(keyword):
                filtered_files["empty_keyword"].append(filename)
        
        # 4. 중복 키워드 (중복된 키워드의 두 번째 파일부터 제거)
        duplicates = self.find_duplicate_keywords(png_files)
        for keyword, files in duplicates.items():
            # 첫 번째 파일은 유지하고 나머지는 제거 대상
            filtered_files["duplicates"].extend(files[1:])
        
        return filtered_files
    
    def print_analysis_report(self, filtered_files: Dict[str, List[str]]):
        """분석 결과 출력"""
        print("\n" + "="*60)
        print("AAC 이미지 필터링 분석 결과")
        print("="*60)
        
        total_filtered = sum(len(files) for files in filtered_files.values())
        
        print(f"\n📊 전체 필터링 대상: {total_filtered}개")
        
        print(f"\n🚫 선정적인 내용: {len(filtered_files['inappropriate'])}개")
        if filtered_files['inappropriate']:
            for filename in filtered_files['inappropriate'][:10]:  # 최대 10개만 표시
                keyword = self.extract_keyword_from_filename(filename)
                print(f"   - {filename} (키워드: {keyword})")
            if len(filtered_files['inappropriate']) > 10:
                print(f"   ... 및 {len(filtered_files['inappropriate']) - 10}개 더")
        
        print(f"\n🌍 지역명: {len(filtered_files['locations'])}개")
        if filtered_files['locations']:
            for filename in filtered_files['locations'][:10]:
                keyword = self.extract_keyword_from_filename(filename)
                print(f"   - {filename} (키워드: {keyword})")
            if len(filtered_files['locations']) > 10:
                print(f"   ... 및 {len(filtered_files['locations']) - 10}개 더")
        
        print(f"\n📝 공백 키워드: {len(filtered_files['empty_keyword'])}개")
        if filtered_files['empty_keyword']:
            for filename in filtered_files['empty_keyword'][:10]:
                print(f"   - {filename}")
            if len(filtered_files['empty_keyword']) > 10:
                print(f"   ... 및 {len(filtered_files['empty_keyword']) - 10}개 더")
        
        print(f"\n🔄 중복 키워드: {len(filtered_files['duplicates'])}개")
        if filtered_files['duplicates']:
            for filename in filtered_files['duplicates'][:10]:
                keyword = self.extract_keyword_from_filename(filename)
                print(f"   - {filename} (키워드: {keyword})")
            if len(filtered_files['duplicates']) > 10:
                print(f"   ... 및 {len(filtered_files['duplicates']) - 10}개 더")
        
        print("\n" + "="*60)
    
    def create_backup(self, files_to_delete: List[str]):
        """삭제할 파일들을 백업 폴더로 이동"""
        if not files_to_delete:
            return
        
        self.backup_folder.mkdir(exist_ok=True)
        print(f"\n💾 백업 폴더 생성: {self.backup_folder}")
        
        for filename in files_to_delete:
            src = self.images_folder / filename
            dst = self.backup_folder / filename
            
            if src.exists():
                try:
                    shutil.move(str(src), str(dst))
                    print(f"   백업 완료: {filename}")
                except Exception as e:
                    print(f"   백업 실패: {filename} - {e}")
    
    def delete_filtered_images(self, filtered_files: Dict[str, List[str]], 
                             create_backup: bool = True, 
                             confirm: bool = True) -> int:
        """필터링된 이미지들 삭제"""
        # 모든 삭제 대상 파일 수집
        all_files_to_delete = []
        for category, files in filtered_files.items():
            all_files_to_delete.extend(files)
        
        # 중복 제거
        all_files_to_delete = list(set(all_files_to_delete))
        
        if not all_files_to_delete:
            print("삭제할 파일이 없습니다.")
            return 0
        
        print(f"\n총 {len(all_files_to_delete)}개 파일을 삭제할 예정입니다.")
        
        if confirm:
            response = input("정말 삭제하시겠습니까? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("삭제가 취소되었습니다.")
                return 0
        
        # 백업 생성
        if create_backup:
            self.create_backup(all_files_to_delete)
        
        # 실제 삭제 (백업을 했다면 이미 이동되어 있음)
        deleted_count = 0
        if not create_backup:  # 백업을 안 했다면 직접 삭제
            for filename in all_files_to_delete:
                file_path = self.images_folder / filename
                if file_path.exists():
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        print(f"   삭제 완료: {filename}")
                    except Exception as e:
                        print(f"   삭제 실패: {filename} - {e}")
        else:
            deleted_count = len(all_files_to_delete)
        
        print(f"\n✅ 총 {deleted_count}개 파일이 처리되었습니다.")
        if create_backup:
            print(f"백업 위치: {self.backup_folder}")
        
        return deleted_count
    
    def run_filter(self, delete_files: bool = False, 
                   create_backup: bool = True, 
                   confirm: bool = True):
        """필터링 실행"""
        print("AAC 이미지 필터링을 시작합니다...")
        
        # 분석 실행
        filtered_files = self.analyze_images()
        
        # 결과 출력
        self.print_analysis_report(filtered_files)
        
        # 삭제 실행
        if delete_files:
            deleted_count = self.delete_filtered_images(
                filtered_files, 
                create_backup=create_backup, 
                confirm=confirm
            )
            return deleted_count
        else:
            print("\n💡 분석만 수행되었습니다. 실제 삭제를 원한다면 delete_files=True로 설정하세요.")
            return 0


def main():
    # 사용 예시
    images_folder = "data/images"
    
    filter_tool = AACImageFilter(images_folder)
    
    # 1단계: 분석만 수행 (삭제하지 않음)
    print("🔍 1단계: 파일 분석 중...")
    filter_tool.run_filter(delete_files=False)
    
    # 2단계: 실제 삭제 수행 (확인 후)
    print("\n" + "="*60)
    response = input("분석 결과를 확인했습니다. 실제 삭제를 진행하시겠습니까? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("🗑️  2단계: 파일 삭제 중...")
        deleted_count = filter_tool.run_filter(
            delete_files=True, 
            create_backup=True,  # 백업 생성
            confirm=True  # 최종 확인
        )
        print(f"\n🎉 필터링 완료! {deleted_count}개 파일이 처리되었습니다.")
    else:
        print("삭제가 취소되었습니다.")


if __name__ == "__main__":
    main()
