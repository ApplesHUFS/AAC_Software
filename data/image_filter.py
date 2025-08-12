import os
import shutil
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class ImageFilter:
    def __init__(self, images_folder: str):
        self.images_folder = Path(images_folder)
        self.filtered_folder = self.images_folder.parent / "filtered_images"
        
        self.inappropriate_keywords = {
            '강간', '성매매', '구강 성교', '사정', '발기', '자위', '성관계', 
            '성폭행', '나체', '살인', '학대', '자살', '납치되다', '여자 생식기', '남자 생식기',
            '남자 성기', '생식기를 만지다', '클리토리스', '낙태', '자해',
            '목을 조르다', '목 조르다', '마약', '공격하다', '쏘다', '불구',
            '소변줄', '황달'
        }

        self.medical_technical_keywords = {
            '포롭터', '이경검사', '요추 천자', '기관절개술', '동정맥루', '뇌전도검사',
            '폐활량 측정', '산소포화도 측정', '유발 전위', '파노라마 방사선 촬영',
            '대퇴사두근', '비복근', '소둔근', '승모근', '비골', '정강이뼈', 
            '지골', '위팔뼈', '자뼈', '대퇴골', '묘성증후군', '자폐스펙트럼장애', 
            '지체장애', '뇌전증', '난독증', '글루텐 불내증', '요로감염증',
            '압력 관리 기계', '작업 치료사', '언어치료사', '수치료', '시험관 시술',
            '피임약', '난관결찰', '정관수술', '외이도', '이소골', '소파수술', '하복부 방사선 보호 차폐',
            '양수 진단', '대장내시경', '요로결석', '위내시경', '심전도계', '좌약을 넣다', '관장튜브',
            '좌약', '관장', '뉴런', '버튼형 위조루', '다운증후군', '췌장', '당뇨', '정맥', '동맥',
            "항암화학요법"
        }

        self.academic_scientific_keywords = {
            '엽록소', '구석기시대', '신석기시대', '대수층', '수권', '암석권',
            '지협', '대기현상', '응결', '증발', '난생의', '단백질', 'DNA',
            '티라노사우루스 렉스 두개골'
        }
        

        self.cultural_specific_keywords = {
            'ñ', '알타미라', '세르반테스', '둘네시아', '프란시스코 고야', '산초 판사',
            '마고스토', '파네예스트', '까가네', '티오 데 나달', '트론카 데 나달', 
            '성 조지', '사순절의 거인', '살바도르 달리', '헤미사이클', '카르멘 문', 
            '탐 톰브', '사그라다 파밀리아 성당', '아토미움', '까혼 드럼', '클라베스', 
            '이맘', '란셋', '아우구스투스', '스페인어', '스페인의', '크레마', '파예',
            "유대교의 예배당", "플라멩코", "알칼라 문", "투탕카멘", '율법', '둘시네아',
            '티오 델 나달', '성반', '미사', '성자', '페그보드게임'
        }

        self.administrative_legal_keywords = {
            '출생증명서', '공민권', '가족관계증명서', '영수증', '이행', 
            '노사협의회', '인구조사', '신청서', '명예위원회', '조약', '보조금',
            '수술동의서', '동의서', '평생교육', '정당', '야당'
        }
        
        self.location_keywords = {
            '우에스카', '테루엘', '사라고사', '알메리아', '카디스', '코르도바', '소말리아',
            '그라나다', '우엘바', '하엔', '말라가', '세비야', '라코루냐', 
            '루고', '오렌세', '폰테베드라', '알라바', '기푸스코아', '비스카야',
            '알바세테', '시우다드레알', '쿠엔카', '과달라하라', '톨레도',
            '알리칸테', '카스텔론', '발렌시아', '아빌라', '부르고스', '레온',
            '팔렌시아', '살라망카', '세고비아', '소리아', '바야돌리드', '사모라',
            '아스투리아스', '바다호스', '카세레스', '바르셀로나', '지로나',
            '레이다', '타라고나', '칸타브리아', '세우타', '멜리야', '라 리오하',
            '마드리드', '무르시아', '나바라', '엘이에로', '라 고메라', '라 팔마',
            '란사로테', '포르멘테라', '테네리페', '이비자', '마요르카', '미노르카',
            '헝가리', '노르웨이', '불가리아', '쿠바', '파나마', '푸에르토리코', 
            '네덜란드', '에콰도르', '호주', '오스트리아', '보스니아 헤르체코비나', '체코',
            '사이프러스', '코스타리카', '크로아티아', '덴마크', '에스토니아', '스코틀랜드',
            '슬로바키아', '핀란드', '과테말라', '아일랜드', '아이슬란드', '리투아니아', 
            '룩셈부르크', '북마케도니아', '몰타', '니카라과', '남아프리카', '스위스', '터키',
            '그린 카나리아', '푸에르테벤투라', '아프가니스탄', '사우디아라비아', '북한', '대한민국',
            '인도', '이라크', '이란', '이스라엘', '뉴질랜드', '파키스탄', '태국',
            '러시아', '영국', '그리스', '벨기에', '이탈리아', '독일', '포르투갈', '스페인',
            '베트남', '시리아', '싱가포르', '카타르', '오만', '네팔', '카자흐스탄', '인도네시아',
            '필리핀', '캄보디아', '나토', '가나', '에티오피아', '콩고민주공화국', '앙골라', '알제리',
            '아르메니아', '아제르바이잔', '바하마 제도', '바베이도스', '벨로루시', '보츠와나', '부르키나파소',
            '부룬디', '카보베르데', "그란 카나리아"
        }

        self.miscellaneous_keywords = {
            '페탕크', '콘크리트 칼블럭', '배수관 세정제', '연습문제', 
            '동등한 기회', '접근하기 쉬운', 'ESPLAI', '기술 교사', 
            'IOS', 'OTS', '문화', '존엄성', '스폰서', '홍보하다', 
            '의무를 지우다', '도시 중심지', '정화 시설', '의사소통책을 사용하다',
            '계속하다', '시간을 가지다', '자수틀', '결항되다', '술탄', 
            '전동캔따개', '죽마로 걷다', '배터리함', '돼지껍데기 과자',
            '라벨을 붙이다', '용수로', '가족 모임 장소', '무덤을 파다', '자세', '개인의',
            '문장', '글루텐', '고용, 평등, 협력과 의사소'
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
        
        if any(word in keyword_lower for word in self.medical_technical_keywords):
            return "medical_technical"
        
        if any(word in keyword_lower for word in self.academic_scientific_keywords):
            return "academic_scientific"
        
        if any(word in keyword_lower for word in self.cultural_specific_keywords):
            return "cultural_specific"
        
        if any(word in keyword_lower for word in self.administrative_legal_keywords):
            return "administrative_legal"
        
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