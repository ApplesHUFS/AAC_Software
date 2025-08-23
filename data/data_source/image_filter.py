import shutil
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class ImageFilter:
    def __init__(self, images_folder: str):
        self.images_folder = Path(images_folder)
        self.filtered_folder = self.images_folder.parent / "filtered_images"

        self.inappropriate_keywords = {
            '강간', '성매매', '구강 성교', '사정', '발기', '자위', '성관계', '난소', '난자',
            '성폭행', '나체', '살인', '학대', '자살', '납치되다', '여자 생식기', '남자 생식기',
            '남자 성기', '생식기를 만지다', '클리토리스', '낙태', '자해', '속옷을 벗다', '베이비 파우더',
            '목을 조르다', '목 조르다', '마약', '공격하다', '쏘다', '불구',
            '소변줄', '탐폰을 끼우다', '사지', '탐폰을 빼다', '속옷을 벗다', '팬티를 입다', '팬티를 벗다',
            '범죄학자', '범죄 현장', '유언장', '무덤을 파다', '범죄', '공동 묘지', '수영복을 벗다', '더러운 기저귀'

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
            "항암화학요법", '수중 분만', '외과 전문의', '심리운동실', '심장 전문의', '간병인실', '작업치료사',
            '치료용 짐볼', '족질환치료사', '무용 치료', '환자 리프트', '작업치료',
            '가족치료 팀', '보조 마우스', '특별활동 전문가', '기억력훈련', '기억력 훈련',
            '장애인 스포츠', '보치아', '황달', '이경', '기립훈련기', '성 행태 학장', '성 행태 학자',
            '질식 방지 장치', '마취 마스크', '수 치료', '전염시키다', '마취 기계', '소생실',
            '의식을 되찾다', '심전도 초음파', '항암화학요법', '건강 검진', '혈액 분석', '투석',
            '수중 분만', '암점', '감각통합실', '청력검사', '씨티를 찍다', '알러지 검사', '시력검사',
            '중환자실', '방사선사', '코산소줄을 한 사람', '코산소줄을 한 소년', '코산소줄을 한 소녀',
            '외과용 테이프를 붙이다', '삽관하다', '반사신경검사', '경구투약', ' 엑스레이를 찍다',
            '하혈', '격리병동', '글루텐', '쌍둥이에게 수유하다', '검사실', '부상자 분류', '방사선 전문의', '임상 심리학자', '제세동기', '결혼 가족 상담치료',
            '마취과 의사', 'MRI', '언어 치료사', '특수학교', '웃음 치료',
            '외과제품 가게', '영안실', '상처를 봉합하다', '반사검사', 'teacch',
            '머리둘레', '장애진단서', '사망진단서', '건강검진센터', '낮병원',
            '정신건강센터', '여성의학센터'

        }

        self.academic_scientific_keywords = {
            '엽록소', '구석기시대', '신석기시대', '대수층', '수권', '암석권',
            '지협', '대기현상', '응결', '증발', '난생의', '단백질', 'DNA',
            '티라노사우루스 렉스 두개골', '달 위상', '박테리아', '입자', '힘줄', '노뼈', '광섬유',
            '공룡 다리', '티라노사우루스 렉스 두개골', '트리케라톱스 두개골', '공룡 척추 화석', '공룡 척추',
            '공룡 꼬리', '공룡 이빨', '공룡 목', '공룡 발톱', '공룡 골판', '공룡 팔',
            '원자력', '선사시대', '역사', '녹이다', '모양을 만들다', '발굴하다',
            '고등 교육', '치태'

        }

        self.cultural_specific_keywords = {
            'ñ', '알타미라', '세르반테스', '둘네시아', '프란시스코 고야', '산초 판사',
            '마고스토', '파네예스트', '까가네', '티오 데 나달', '트론카 데 나달',
            '성 조지', '사순절의 거인', '살바도르 달리', '헤미사이클', '카르멘 문',
            '탐 톰브', '사그라다 파밀리아 성당', '아토미움', '까혼 드럼', '클라베스',
            '이맘', '란셋', '아우구스투스', '스페인어', '스페인의', '크레마', '파예',
            "유대교의 예배당", "플라멩코", "알칼라 문", "투탕카멘", '율법', '둘시네아',
            '티오 델 나달', '성반', '미사', '성자', '페그보드게임', '야물커', '쿠아하다',
            '갈고리', '카넬로니', '성찬식', '세 명의 현자', '성주간', '돈키호테',
            '아라곤 과일', '잠봄바', '산 후안의 날', '쿠아하다', '둘시네아',
            '파네예스트', '티오 델 나달', '발렌타인데이', '알칼라 문', '브라덴부르크 문',
            '카르멘 문', '다윗의 별', '아담과 이브', '제단', '사도', '사도들',
            '노아의 방주', '은총', '성배', '촛대', '성령', '플라멩코', '성체의 빵',
            '야물커', '파티마의 손', '기적', '모세', '노아', '성반', '세례 요한',
            '성자', '유대교의 예배당', '부활초', '이슬람사원', '율법', '묵주 기도를 드리다',
            '묵주기도', '미국 국회 의사당', '브라질 예수상','숄', '이동식 예배소', '성찬의 전롄',
            '판초', '트랜스 젠더', '성적 지향', '성평등', '파네예트스', '카르멘문',
            'ARASAAC'


        }

        self.administrative_legal_keywords = {
            '출생증명서', '공민권', '가족관계증명서', '영수증', '이행', '명예 위원회',
            '노사협의회', '인구조사', '신청서', '명예위원회', '조약', '보조금',
            '수술동의서', '동의서', '평생교육', '정당', '야당',
            '이혼 판결', '이혼 신청', '항의', '보험', '자동차보험', '집보험',
            '건강보험', '생명보험', '유지 보수 관리자', '자문 상담', '오리엔테이션',
            '학생대표실', '파업', '불신임 발의', '공무원', '상인', '고용주 조합',
            '고용센터', '직업 소개소', '등기소', '유지 보수', '지역 자치회', '주소',
            '개인정보', '지역 회관', '공업단지', '회계 감사하다', '세금', '세무서', '공증기관',
            '공증인', '법률', '인가하다', '사생활 침해', '특별 고용 센터', '전화번호', '우편번호',
            '조기교실 센터', '교육부', '홍보 담당 부서', '지역', '신규 이민자 프로그램',
            '등록', '통역 센터', '경찰서', '접수처', '배심원', '비밀 투표', '투표소', '계획', '대변인', '안내책',
            '운전 학원'
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
            '인도', '이라크', '이란', '이스라엘', '뉴질랜드', '파키스탄', '태국', '스웨덴', '프랑스',
            '러시아', '영국', '그리스', '벨기에', '이탈리아', '독일', '포르투갈', '스페인', '부르키나 파소',
            '베트남', '시리아', '싱가포르', '카타르', '오만', '네팔', '카자흐스탄', '인도네시아',
            '필리핀', '캄보디아', '나토', '가나', '에티오피아', '콩고민주공화국', '앙골라', '알제리',
            '아르메니아', '아제르바이잔', '바하마 제도', '바베이도스', '벨로루시', '보츠와나', '부르키나파소',
            '부룬디', '카보베르데', "그란 카나리아", '테이데산', '라트비아', '폴란드', '사르비아', '아구아탑',
            '4D 영화관', '가족 모임 장소', '노인학교', '동물보호소', '오감정원', '동맹국'

        }

        self.tools_objects_keywords = {
            '페탕크', '콘크리트 칼블럭', '배수관 세정제', '전동캔따개', '자수틀',
            '배터리함', '손가락 심벌즈', '목공 클램프', '완장한 튜브', '도르래',
            '풀 누들', '전화 교환대', '교환실', '플랫 그네', '심리운동용 바퀴',
            '치료용 짐볼', '보조 마우스', '주택 자동화', '심판의 라커룸', '트랙볼',
            '파이프 오르간', '적외선 조사기', '치과 등', '소변줄', '타진기', '흡입약', '산소줄',
            '태블릿 스위치', '터치스크린', '기립기가 있는 휠체어', '데이터 센터',
            '인큐베이터', '유축기', '수실용 스테이플러', '산소마스크', '산소 마스크', '검안경',
            '경추보호대', '투관침', '전극' '핫팩', '공기탱크', '압력계', '스쿠버다이빙 장비',
            '아이 트래킹', '헤드마우스', '헤드 포인터', '참빛', '유해폐기물', '감각 물병', '도자기 가마',
            '계단 리프트', '스티커', '막사', '잔고소켓', '스카치 테이프 케이스', '파쇄기', '웨이트벨트', '부력조절기',
            '스쿠버다이빙 호흡기', '보안검색', 'X선 보안검색', '금속탐지기',
            '코르크', '코르크를 뽑다', '저울', '데오도런트', '기립기', '음성 합성'

        }

        self.concepts_keywords = {
            '동등한 기회', '접근하기 쉬운', '문화', '존엄성', '의무를 지우다',
            '계속하다', '시간을 가지다', '중요하다', '참여', '의심', '할 수 있다',
            '원인', '범용 디자인', '실행', '일치하다', '통합하다', '차별하다', '주말',
            '범주', '감각', '공간 개념', '개인의', '활동과 행사', '목격', '독립하다', '무게',
            '동사', '방학', '화재 시 엘리베이터 사용 금', '주', '독화', '미성년자', '생년월일',
            '성별이 뭐예요', '접근성', '설명'

        }

        self.miscellaneous_keywords = {
            '역 슬래시', '역 느낌표', '역 물음표', '하이픈', '세미콜론', 'ESPLAI', 'ois', 'ots',
            '심사의원', ' 삼촌', '숙모', '조카', '사촌', '주유소 직원',
            '교장', '상담사', '교장 선생님', '흰자를 젓다', '라디에이터', '벨크로', 'ㅂ',
            '벨보이', '덩굴식물', '개막 연설', '살코기', '바', '수위', '마카로니', '순대', '만두',
            '2유로', '그러나', '아무것도 아니다', '또는', '왜냐하면', '그', '그런데', '그리고',
            '에서', '에서 부터', '얼마나'


        }

    def _contains_word(self, text: str, keywords: Set[str]) -> bool:
        for keyword in keywords:
            keyword_lower=keyword.lower()
            
            # 1) 한글 키워드 처리
            if re.search(r'[ㄱ-ㅎ가-힣]', keyword_lower):
                pattern=r'(?<![가-힣])' + re.escape(keyword_lower) + r'(?![가-힣])'
            # 2) 영어 키워드 처리
            else:
                pattern = r'\b' + re.escape(keyword_lower) + r'\b'
            
            if re.search(pattern, text, re.IGNORECASE):
                return True
            
        return False
            
        '''
        or 단순 일치
        for keyword in keywords:
            if text==keyword.lower().strip():
                return True
        return False
        '''

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

        categories = [
            ("inappropriate", self.inappropriate_keywords),
            ("medical_technical", self.medical_technical_keywords),
            ("academic_scientific", self.academic_scientific_keywords),
            ("cultural_specific", self.cultural_specific_keywords),
            ("administrative_legal", self.administrative_legal_keywords),
            ("locations", self.location_keywords),
            ("tools_objects", self.tools_objects_keywords),
            ("concepts", self.concepts_keywords),
            ("miscellaneous", self.miscellaneous_keywords)
        ]

        for category_name, keywords in categories:
            if self._contains_word(keyword_lower, keywords):
                return category_name

        return ""

    def analyze_images(self) -> Dict[str, List[str]]:
        if not self.images_folder.exists():
            raise FileNotFoundError(f"Images folder not found: {self.images_folder}")

        png_files = [f.name for f in self.images_folder.glob("*.png")]
        filtered_files: Dict[str, List[str]] = defaultdict(list)
        keyword_to_files: Dict[str, List[str]] = defaultdict(list)

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
