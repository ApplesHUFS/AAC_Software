from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import traceback
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from aac_interpreter_service import AACInterpreterService

app = Flask(__name__)

# React 개발/배포 환경 모두 지원하는 CORS 설정
CORS(app,
     origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=True
)

# AAC 서비스 인스턴스 생성
aac_service = AACInterpreterService()

# ===== React 친화적 응답 형식 =====

def api_response(success: bool = True, data: Any = None, message: str = "",
                error: str = "", status_code: int = 200) -> tuple:
    """React 친화적 API 응답 형식"""
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat(),
    }

    if success:
        response["data"] = data if data is not None else {}
        response["message"] = message
    else:
        response["error"] = error or message
        response["data"] = None

    return jsonify(response), status_code

def validate_json_request() -> Optional[Dict[str, Any]]:
    """JSON 요청 데이터 검증"""
    if not request.is_json:
        return None
    return request.get_json()

# ===== 에러 핸들러 =====

@app.errorhandler(Exception)
def handle_error(error):
    """전역 에러 핸들러"""
    print(f"서버 오류 발생: {str(error)}")
    traceback.print_exc()
    return api_response(
        success=False,
        error="서버 내부 오류가 발생했습니다",
        status_code=500
    )

# ===== 기본 엔드포인트 =====

@app.route('/', methods=['GET'])
def home():
    """API 정보 및 엔드포인트 가이드"""
    return api_response(
        data={
            "service": "AAC Interpreter Service API",
            "version": "1.0.0",
            "status": "running",
            "description": "개인화된 AAC 카드 해석 시스템",
            "endpoints": {
                "auth": {
                    "register": "POST /api/auth/register",
                    "login": "POST /api/auth/login",
                    "profile": "GET /api/auth/profile/{userId}",
                    "updateProfile": "PUT /api/auth/profile/{userId}"
                },
                "context": {
                    "create": "POST /api/context",
                    "get": "GET /api/context/{contextId}"
                },
                "cards": {
                    "recommend": "POST /api/cards/recommend",
                    "validate": "POST /api/cards/validate",
                    "interpret": "POST /api/cards/interpret",
                    "history": "GET /api/cards/history/{contextId}",
                    "historyPage": "GET /api/cards/history/{contextId}/page/{pageNumber}"
                },
                "feedback": {
                    "request": "POST /api/feedback/request",
                    "submit": "POST /api/feedback/submit",
                    "pending": "GET /api/feedback/pending"
                },
                "memory": {
                    "update": "POST /api/memory/update",
                    "summary": "GET /api/memory/{userId}/summary",
                    "patterns": "GET /api/memory/{userId}/patterns"
                }
            }
        },
        message="AAC Interpreter Service에 오신 것을 환영합니다"
    )

@app.route('/health', methods=['GET'])
def health_check():
    """헬스체크"""
    return api_response(
        data={
            "status": "healthy",
            "service": "AAC Interpreter Service",
            "version": "1.0.0"
        },
        message="서비스가 정상 작동 중입니다"
    )

@app.route('/api/images/<filename>')
def serve_image(filename):
    """AAC 카드 이미지 서빙 (React에서 직접 접근 가능)"""
    try:
        return send_from_directory('dataset/images', filename)
    except FileNotFoundError:
        return api_response(
            success=False,
            error=f"이미지를 찾을 수 없습니다: {filename}",
            status_code=404
        )

# ===== 1. 인증 관련 엔드포인트 (React 친화적 경로) =====

@app.route('/api/auth/register', methods=['POST'])
def register():
    """회원가입"""
    try:
        data = validate_json_request()
        if not data:
            return api_response(
                success=False,
                error="유효한 JSON 데이터가 필요합니다",
                status_code=400
            )

        # React에서 보내는 필드명 (camelCase) 처리
        required_fields = ['userId', 'name', 'age', 'gender', 'disabilityType',
                          'communicationCharacteristics', 'interestingTopics', 'password']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]

        if missing_fields:
            return api_response(
                success=False,
                error=f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}",
                status_code=400
            )

        # 성별 옵션 제공
        gender_mapping = {
            '남성': 'male', '여성': 'female'
        }

        mapped_gender = gender_mapping.get(data.get('gender', ''), '')
        if mapped_gender not in ['male', 'female']:
            return api_response(
                success=False,
                error="성별은 '남성', '여성' 중 하나여야 합니다",
                status_code=400
            )

        # 장애 유형 검증
        valid_disability_types = ['의사소통장애', '자폐스펙트럼장애', '지적장애']
        if data.get('disabilityType') not in valid_disability_types:
            return api_response(
                success=False,
                error=f"장애유형은 다음 중 하나여야 합니다: {', '.join(valid_disability_types)}",
                status_code=400
            )

        # snake_case로 변환하여 서비스에 전달
        persona_data = {
            'name': data.get('name'),
            'age': int(data.get('age')),
            'gender': mapped_gender,
            'disability_type': data.get('disabilityType'),
            'communication_characteristics': data.get('communicationCharacteristics', ''),
            'interesting_topics': data.get('interestingTopics', []),
            'password': data.get('password')
        }

        result = aac_service.register_user(data.get('userId'), persona_data)

        if result['status'] == 'success':
            return api_response(
                data={
                    "userId": result.get('user_id'),
                    "name": data.get('name'),
                    "status": "created"
                },
                message="회원가입이 완료되었습니다",
                status_code=201
            )
        else:
            return api_response(
                success=False,
                error=result['message'],
                status_code=400
            )

    except Exception as e:
        print(f"회원가입 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"회원가입 처리 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

@app.route('/api/auth/login', methods=['POST'])
def login():
    """로그인"""
    try:
        data = validate_json_request()
        if not data:
            return api_response(
                success=False,
                error="유효한 JSON 데이터가 필요합니다",
                status_code=400
            )

        user_id = data.get('userId')
        password = data.get('password')

        if not user_id or not password:
            return api_response(
                success=False,
                error="사용자 ID와 비밀번호가 필요합니다",
                status_code=400
            )

        result = aac_service.authenticate_user(user_id, password)

        if result['authenticated']:
            user_info = result.get('user_info', {})
            return api_response(
                data={
                    "userId": user_id,
                    "authenticated": True,
                    "user": {
                        "name": user_info.get('name'),
                        "age": user_info.get('age'),
                        "gender": user_info.get('gender'),
                        "disabilityType": user_info.get('disability_type'),
                        "communicationCharacteristics": user_info.get('communication_characteristics'),
                        "interestingTopics": user_info.get('interesting_topics', []),
                        "preferredCategoryTypes": user_info.get('preferred_category_types', []),
                        "createdAt": user_info.get('created_at'),
                        "updatedAt": user_info.get('updated_at')
                    }
                },
                message="로그인 성공"
            )
        else:
            return api_response(
                success=False,
                error=result['message'],
                status_code=401
            )

    except Exception as e:
        print(f"로그인 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"로그인 처리 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

@app.route('/api/auth/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    """사용자 프로필 조회"""
    try:
        result = aac_service.get_user_info(user_id)

        if result['status'] == 'success':
            user_data = result['user']
            return api_response(
                data={
                    "userId": user_id,
                    "name": user_data.get('name'),
                    "age": user_data.get('age'),
                    "gender": user_data.get('gender'),
                    "disabilityType": user_data.get('disability_type'),
                    "communicationCharacteristics": user_data.get('communication_characteristics'),
                    "interestingTopics": user_data.get('interesting_topics', []),
                    "preferredCategoryTypes": user_data.get('preferred_category_types', []),
                    "createdAt": user_data.get('created_at'),
                    "updatedAt": user_data.get('updated_at')
                },
                message="사용자 정보를 조회했습니다"
            )
        else:
            return api_response(
                success=False,
                error=result['message'],
                status_code=404
            )

    except Exception as e:
        print(f"프로필 조회 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"프로필 조회 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

@app.route('/api/auth/profile/<user_id>', methods=['PUT'])
def update_profile(user_id):
    """사용자 프로필 업데이트"""
    try:
        data = validate_json_request()
        if not data:
            return api_response(
                success=False,
                error="유효한 JSON 데이터가 필요합니다",
                status_code=400
            )

        # camelCase를 snake_case로 변환
        update_data = {}
        field_mapping = {
            'name': 'name',
            'age': 'age',
            'gender': 'gender',
            'disabilityType': 'disability_type',
            'communicationCharacteristics': 'communication_characteristics',
            'interestingTopics': 'interesting_topics'
        }

        for camel_key, snake_key in field_mapping.items():
            if camel_key in data:
                update_data[snake_key] = data[camel_key]

        # 성별 매핑
        if 'gender' in update_data:
            gender_mapping = {'남성': 'male', '여성': 'female', 'male': 'male', 'female': 'female'}
            update_data['gender'] = gender_mapping.get(update_data['gender'], update_data['gender'])

        result = aac_service.update_user_persona(user_id, update_data)

        if result['status'] == 'success':
            return api_response(
                data={
                    "updatedFields": result['updated_fields'],
                    "categoryRecalculated": result.get('category_recalculated', False)
                },
                message=result['message']
            )
        else:
            return api_response(
                success=False,
                error=result['message'],
                status_code=400
            )

    except Exception as e:
        print(f"프로필 업데이트 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"프로필 업데이트 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

# ===== 2. 컨텍스트 관리 =====

@app.route('/api/context', methods=['POST'])
def create_context():
    """대화 상황 컨텍스트 생성"""
    try:
        data = validate_json_request()
        if not data:
            return api_response(
                success=False,
                error="유효한 JSON 데이터가 필요합니다",
                status_code=400
            )

        user_id = data.get('userId')
        place = data.get('place', '').strip()
        interaction_partner = data.get('interactionPartner', '').strip()
        current_activity = data.get('currentActivity', '').strip()

        # 필수 필드 검증
        if not user_id:
            return api_response(success=False, error="userId가 필요합니다", status_code=400)
        if not place:
            return api_response(success=False, error="place는 필수 입력사항입니다", status_code=400)
        if not interaction_partner:
            return api_response(success=False, error="interactionPartner는 필수 입력사항입니다", status_code=400)

        result = aac_service.update_user_context(
            user_id, place, interaction_partner,
            current_activity if current_activity else None
        )

        if result['status'] == 'success':
            return api_response(
                data={
                    "contextId": result['context_id'],
                    "userId": user_id,
                    "place": place,
                    "interactionPartner": interaction_partner,
                    "currentActivity": current_activity,
                    "time": datetime.now().strftime("%H시 %M분")
                },
                message="컨텍스트가 생성되었습니다",
                status_code=201
            )
        else:
            return api_response(
                success=False,
                error=result['message'],
                status_code=400
            )

    except Exception as e:
        print(f"컨텍스트 생성 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"컨텍스트 생성 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

@app.route('/api/context/<context_id>', methods=['GET'])
def get_context(context_id):
    """컨텍스트 조회"""
    try:
        result = aac_service.context_manager.get_context(context_id)

        if result['status'] == 'success':
            context = result['context']
            return api_response(
                data={
                    "contextId": context_id,
                    "time": context.get('time'),
                    "place": context.get('place'),
                    "interactionPartner": context.get('interaction_partner'),
                    "currentActivity": context.get('current_activity'),
                    "createdAt": context.get('created_at')
                },
                message="컨텍스트 정보를 조회했습니다"
            )
        else:
            return api_response(
                success=False,
                error=result['message'],
                status_code=404
            )

    except Exception as e:
        print(f"컨텍스트 조회 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"컨텍스트 조회 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

# ===== 3. 카드 관련 엔드포인트 =====

@app.route('/api/cards/recommend', methods=['POST'])
def recommend_cards():
    """페르소나 기반 카드 추천"""
    try:
        data = validate_json_request()
        if not data:
            return api_response(
                success=False,
                error="유효한 JSON 데이터가 필요합니다",
                status_code=400
            )

        user_id = data.get('userId')
        context_id = data.get('contextId')

        if not user_id or not context_id:
            return api_response(
                success=False,
                error="userId와 contextId가 필요합니다",
                status_code=400
            )

        # 컨텍스트 정보 조회
        context_result = aac_service.context_manager.get_context(context_id)
        if context_result['status'] != 'success':
            return api_response(
                success=False,
                error=f"컨텍스트를 찾을 수 없습니다: {context_id}",
                status_code=404
            )

        context_data = {
            'time': context_result['context']['time'],
            'place': context_result['context']['place'],
            'interaction_partner': context_result['context']['interaction_partner'],
            'current_activity': context_result['context']['current_activity']
        }

        # 카드 추천 시스템 확인
        if not hasattr(aac_service, 'card_recommender') or aac_service.card_recommender is None:
            return api_response(
                success=False,
                error="카드 추천 시스템이 사용할 수 없습니다",
                status_code=503
            )

        result = aac_service.get_card_selection_interface(user_id, context_data, context_id)

        if result['status'] == 'success':
            interface_data = result['interface_data']
            cards = interface_data['selection_options']

            # React 친화적 카드 데이터 포맷
            formatted_cards = []
            for i, card_filename in enumerate(cards):
                card_id = card_filename.split('_')[0] if '_' in card_filename else card_filename.replace('.png', '')
                card_name = card_filename.replace('.png', '').replace('_', ' ')

                formatted_cards.append({
                    "id": card_id,
                    "name": card_name,
                    "filename": card_filename,
                    "imagePath": f"/api/images/{card_filename}",
                    "index": i,
                    "selected": False  # React 상태 관리용
                })

            return api_response(
                data={
                    "cards": formatted_cards,
                    "totalCards": len(formatted_cards),
                    "contextInfo": {
                        "time": interface_data.get('context_info', {}).get('time'),
                        "place": interface_data.get('context_info', {}).get('place'),
                        "interactionPartner": interface_data.get('context_info', {}).get('interaction_partner'),
                        "currentActivity": interface_data.get('context_info', {}).get('current_activity')
                    },
                    "selectionRules": {
                        "minCards": interface_data.get('selection_rules', {}).get('min_cards', 1),
                        "maxCards": interface_data.get('selection_rules', {}).get('max_cards', 4),
                        "totalOptions": len(formatted_cards)
                    },
                    "pagination": {
                        "currentPage": 1,
                        "totalPages": interface_data.get('total_pages', 1)
                    }
                },
                message="카드 추천이 완료되었습니다"
            )
        else:
            return api_response(
                success=False,
                error="카드 추천 생성에 실패했습니다",
                status_code=500
            )

    except Exception as e:
        print(f"카드 추천 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"카드 추천 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

@app.route('/api/cards/history/<context_id>', methods=['GET'])
def get_card_history_summary(context_id):
    """카드 추천 히스토리 요약"""
    try:
        result = aac_service.get_card_recommendation_history_summary(context_id)

        if result['status'] == 'success':
            return api_response(
                data={
                    "contextId": context_id,
                    "totalPages": result['total_pages'],
                    "latestPage": result['latest_page'],
                    "historySummary": [
                        {
                            "pageNumber": item['page_number'],
                            "cardCount": item['card_count'],
                            "timestamp": item['timestamp']
                        }
                        for item in result['history_summary']
                    ]
                },
                message="추천 히스토리를 조회했습니다"
            )
        else:
            return api_response(
                success=False,
                error=result['message'],
                status_code=404
            )

    except Exception as e:
        print(f"히스토리 조회 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"히스토리 조회 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

@app.route('/api/cards/history/<context_id>/page/<int:page_number>', methods=['GET'])
def get_card_history_page(context_id, page_number):
    """특정 페이지의 카드 히스토리"""
    try:
        result = aac_service.get_card_recommendation_history_page(context_id, page_number)

        if result['status'] == 'success':
            cards = result['cards']

            formatted_cards = []
            for i, card_filename in enumerate(cards):
                card_id = card_filename.split('_')[0] if '_' in card_filename else card_filename.replace('.png', '')
                card_name = card_filename.replace('.png', '').replace('_', ' ')

                formatted_cards.append({
                    "id": card_id,
                    "name": card_name,
                    "filename": card_filename,
                    "imagePath": f"/api/images/{card_filename}",
                    "index": i,
                    "selected": False
                })

            return api_response(
                data={
                    "cards": formatted_cards,
                    "pagination": {
                        "currentPage": result['page_number'],
                        "totalPages": result['total_pages']
                    },
                    "timestamp": result['timestamp'],
                    "contextId": context_id
                },
                message=f"페이지 {page_number}를 조회했습니다"
            )
        else:
            return api_response(
                success=False,
                error=result['message'],
                status_code=404
            )

    except Exception as e:
        print(f"히스토리 페이지 조회 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"히스토리 페이지 조회 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

@app.route('/api/cards/validate', methods=['POST'])
def validate_cards():
    """카드 선택 유효성 검증"""
    try:
        data = validate_json_request()
        if not data:
            return api_response(
                success=False,
                error="유효한 JSON 데이터가 필요합니다",
                status_code=400
            )

        selected_cards = data.get('selectedCards', [])
        available_options = data.get('availableOptions', [])

        if not selected_cards:
            return api_response(
                success=False,
                error="선택된 카드가 없습니다",
                status_code=400
            )

        result = aac_service.validate_card_selection(selected_cards, available_options)

        return api_response(
            data={
                "valid": result['valid'],
                "selectedCount": len(selected_cards)
            },
            message=result['message'],
            status_code=200 if result['valid'] else 422
        )

    except Exception as e:
        print(f"카드 검증 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"카드 검증 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

@app.route('/api/cards/interpret', methods=['POST'])
def interpret_cards():
    """선택된 카드 해석"""
    try:
        data = validate_json_request()
        if not data:
            return api_response(
                success=False,
                error="유효한 JSON 데이터가 필요합니다",
                status_code=400
            )

        selected_cards = data.get('selectedCards', [])
        user_id = data.get('userId')
        context_id = data.get('contextId')

        if not user_id or not selected_cards:
            return api_response(
                success=False,
                error="userId와 selectedCards가 필요합니다",
                status_code=400
            )

        # 카드 파일명 추출 (React에서 보낸 카드 객체 처리)
        card_filenames = []
        for card in selected_cards:
            if isinstance(card, dict):
                if 'filename' in card:
                    card_filenames.append(card['filename'])
                elif 'name' in card:
                    name = card['name'].replace(' ', '_') + '.png'
                    card_filenames.append(name)
            else:
                card_filenames.append(str(card))

        # 컨텍스트 정보 조회
        context = None
        if context_id:
            context_result = aac_service.context_manager.get_context(context_id)
            if context_result['status'] == 'success':
                context = {
                    'time': context_result['context']['time'],
                    'place': context_result['context']['place'],
                    'interaction_partner': context_result['context']['interaction_partner'],
                    'current_activity': context_result['context']['current_activity']
                }

        # 카드 해석기 확인
        if not hasattr(aac_service, 'card_interpreter') or aac_service.card_interpreter is None:
            return api_response(
                success=False,
                error="카드 해석 시스템이 사용할 수 없습니다",
                status_code=503
            )

        result = aac_service.interpret_cards(user_id, card_filenames, context)

        if result['status'] == 'success':
            return api_response(
                data={
                    "interpretations": [
                        {
                            "index": i,
                            "text": interpretation,
                            "selected": False  # React 상태 관리용
                        }
                        for i, interpretation in enumerate(result['interpretations'])
                    ],
                    "feedbackId": result['feedback_id'],
                    "method": result['method'],
                    "selectedCards": [
                        {
                            "filename": filename,
                            "name": filename.replace('.png', '').replace('_', ' '),
                            "imagePath": f"/api/images/{filename}"
                        }
                        for filename in card_filenames
                    ]
                },
                message="카드 해석이 완료되었습니다"
            )
        else:
            return api_response(
                success=False,
                error="카드 해석에 실패했습니다",
                status_code=500
            )

    except Exception as e:
        print(f"카드 해석 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"카드 해석 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

# ===== 4. 피드백 관리 =====

@app.route('/api/feedback/request', methods=['POST'])
def request_feedback():
    """Partner 피드백 확인 요청"""
    try:
        data = validate_json_request()
        if not data:
            return api_response(
                success=False,
                error="유효한 JSON 데이터가 필요합니다",
                status_code=400
            )

        user_id = data.get('userId')
        cards = data.get('cards', [])
        context = data.get('context', {})
        interpretations = data.get('interpretations', [])
        partner_info = data.get('partnerInfo', {})

        if not all([user_id, cards, interpretations]):
            return api_response(
                success=False,
                error="userId, cards, interpretations가 필요합니다",
                status_code=400
            )

        result = aac_service.request_partner_confirmation(
            user_id=user_id,
            cards=cards,
            context=context,
            interpretations=interpretations,
            partner_info=partner_info
        )

        if result['status'] == 'success':
            return api_response(
                data={
                    "confirmationId": result['confirmation_id'],
                    "confirmationRequest": result['confirmation_request']
                },
                message=result['message'],
                status_code=201
            )
        else:
            return api_response(
                success=False,
                error=result['message'],
                status_code=400
            )

    except Exception as e:
        print(f"피드백 요청 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"피드백 요청 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

@app.route('/api/feedback/submit', methods=['POST'])
def submit_feedback():
    """Partner 피드백 제출"""
    try:
        data = validate_json_request()
        if not data:
            return api_response(
                success=False,
                error="유효한 JSON 데이터가 필요합니다",
                status_code=400
            )

        confirmation_id = data.get('confirmationId')
        selected_interpretation_index = data.get('selectedInterpretationIndex')
        direct_feedback = data.get('directFeedback')

        if not confirmation_id:
            return api_response(
                success=False,
                error="confirmationId가 필요합니다",
                status_code=400
            )

        result = aac_service.submit_partner_feedback(
            confirmation_id=confirmation_id,
            selected_interpretation_index=selected_interpretation_index,
            direct_feedback=direct_feedback
        )

        if result['status'] == 'success':
            return api_response(
                data={
                    "feedbackResult": result['feedback_result']
                },
                message=result['message']
            )
        else:
            return api_response(
                success=False,
                error=result['message'],
                status_code=400
            )

    except Exception as e:
        print(f"피드백 제출 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"피드백 제출 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

@app.route('/api/feedback/pending', methods=['GET'])
def get_pending_feedback():
    """대기 중인 피드백 조회"""
    try:
        partner_filter = request.args.get('partner')

        try:
            result = aac_service.get_pending_partner_confirmations(partner_filter)
        except AttributeError:
            result = {'pending_requests': [], 'total_count': 0}

        return api_response(
            data={
                "pendingRequests": result['pending_requests'],
                "totalCount": result['total_count']
            },
            message="대기 중인 피드백을 조회했습니다"
        )

    except Exception as e:
        print(f"대기 피드백 조회 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"대기 피드백 조회 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

# ===== 5. 메모리 관리 =====

@app.route('/api/memory/update', methods=['POST'])
def update_memory():
    """대화 메모리 업데이트"""
    try:
        data = validate_json_request()
        if not data:
            return api_response(
                success=False,
                error="유효한 JSON 데이터가 필요합니다",
                status_code=400
            )

        user_id = data.get('userId')
        cards = data.get('cards', [])
        context = data.get('context', {})
        interpretations = data.get('interpretations', [])
        final_interpretation = data.get('finalInterpretation')

        if not user_id:
            return api_response(
                success=False,
                error="userId가 필요합니다",
                status_code=400
            )

        # 메모리 시스템 확인
        if not hasattr(aac_service, 'conversation_memory') or aac_service.conversation_memory is None:
            print(f"메모리 업데이트 (기본 모드) - 사용자: {user_id}")
            return api_response(
                data={"memoryUpdated": True},
                message="메모리 업데이트 완료 (기본 모드)"
            )

        if final_interpretation and cards:
            result = aac_service.conversation_memory.add_conversation_memory(
                user_id=user_id,
                cards=cards,
                context=context,
                interpretations=interpretations,
                selected_interpretation=final_interpretation if final_interpretation in interpretations else None,
                user_correction=final_interpretation if final_interpretation not in interpretations else None
            )

            if result['status'] == 'success':
                return api_response(
                    data={
                        "summary": result['summary'],
                        "memoryUpdated": result['memory_updated']
                    },
                    message=result['message']
                )
            else:
                return api_response(
                    success=False,
                    error=result['message'],
                    status_code=500
                )
        else:
            return api_response(
                data={"memoryUpdated": True},
                message="메모리 업데이트 완료"
            )

    except Exception as e:
        print(f"메모리 업데이트 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"메모리 업데이트 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

@app.route('/api/memory/<user_id>/summary', methods=['GET'])
def get_memory_summary(user_id):
    """사용자 메모리 요약 조회"""
    try:
        if not hasattr(aac_service, 'conversation_memory') or aac_service.conversation_memory is None:
            return api_response(
                data={
                    "summary": "",
                    "conversationCount": 0,
                    "available": False
                },
                message="메모리 시스템이 사용할 수 없습니다"
            )

        result = aac_service.conversation_memory.get_user_memory_summary(user_id)

        return api_response(
            data={
                "userId": user_id,
                "summary": result['summary'],
                "conversationCount": result['conversation_count'],
                "available": True
            },
            message="메모리 요약을 조회했습니다"
        )

    except Exception as e:
        print(f"메모리 요약 조회 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"메모리 요약 조회 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

@app.route('/api/memory/<user_id>/patterns', methods=['GET'])
def get_memory_patterns(user_id):
    """사용자 사용 패턴 조회"""
    try:
        limit = request.args.get('limit', 5, type=int)

        if not hasattr(aac_service, 'conversation_memory') or aac_service.conversation_memory is None:
            return api_response(
                data={
                    "recentPatterns": [],
                    "suggestions": [],
                    "available": False
                },
                message="메모리 시스템이 사용할 수 없습니다"
            )

        result = aac_service.conversation_memory.get_recent_patterns(user_id, limit)

        return api_response(
            data={
                "userId": user_id,
                "recentPatterns": result['recent_patterns'],
                "suggestions": result['suggestions'],
                "limit": limit,
                "available": True
            },
            message="사용 패턴을 조회했습니다"
        )

    except Exception as e:
        print(f"사용 패턴 조회 오류: {str(e)}")
        return api_response(
            success=False,
            error=f"사용 패턴 조회 중 오류가 발생했습니다: {str(e)}",
            status_code=500
        )

# ===== 서버 시작 =====

if __name__ == '__main__':
    print("🚀 AAC Interpreter API Server (React 최적화) 시작 중...")
    print("📍 서버 주소: http://localhost:8000")
    print("🔍 헬스체크: http://localhost:8000/health")
    print("🌐 CORS 설정: React 개발 서버 (3000, 5173) 허용")
    print("📱 React 친화적 API 엔드포인트:")
    print("   🔐 인증: /api/auth/*")
    print("   🔄 컨텍스트: /api/context/*")
    print("   🎴 카드: /api/cards/*")
    print("   💬 피드백: /api/feedback/*")
    print("   🧠 메모리: /api/memory/*")
    print("   🖼️  이미지: /api/images/*")

    app.run(host='0.0.0.0', port=8000, debug=True)
