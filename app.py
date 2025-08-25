from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import traceback
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from aac_interpreter_service import AACInterpreterService

app = Flask(__name__)
CORS(app)

# AAC 서비스 인스턴스 생성
aac_service = AACInterpreterService()

# ===== 에러 핸들러 =====

@app.errorhandler(Exception)
def handle_error(error):
    """전역 에러 핸들러"""
    print(f"서버 오류 발생: {str(error)}")
    traceback.print_exc()
    return jsonify({
        'error': str(error),
        'message': '서버 내부 오류가 발생했습니다'
    }), 500

def validate_json_request() -> Optional[Dict[str, Any]]:
    """JSON 요청 데이터 검증"""
    if not request.is_json:
        return None

    data = request.get_json()
    if not data:
        return None

    return data

def error_response(message: str, status_code: int = 400) -> tuple:
    """에러 응답 생성"""
    return jsonify({'error': message}), status_code

def success_response(data: Dict[str, Any], status_code: int = 200) -> tuple:
    """성공 응답 생성"""
    return jsonify(data), status_code

# ===== 기본 엔드포인트 =====

@app.route('/', methods=['GET'])
def home():
    """서비스 정보 제공"""
    return success_response({
        'message': 'AAC Interpreter Service API',
        'version': '1.0.0',
        'status': 'running',
        'description': '개인화된 AAC 카드 해석 시스템',
        'endpoints': {
            'health': 'GET /health',
            'users': {
                'register': 'POST /users',
                'login': 'POST /users/{user_id}/auth',
                'get_info': 'GET /users/{user_id}',
                'update_persona': 'PUT /users/{user_id}/persona'
            },
            'contexts': {
                'create': 'POST /contexts',
                'get': 'GET /contexts/{context_id}'
            },
            'cards': {
                'recommend': 'POST /cards/recommendations',
                'validate_selection': 'POST /cards/validate',
                'interpret': 'POST /cards/interpret',
                'history_summary': 'GET /cards/recommendations/history/{context_id}',
                'history_page': 'GET /cards/recommendations/history/{context_id}/page/{page_number}'
            },
            'feedback': {
                'submit': 'POST /feedback',
                'get_pending': 'GET /feedback/pending'
            },
            'memory': {
                'update': 'POST /memory/update',
                'get_summary': 'GET /memory/{user_id}/summary'
            }
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """헬스체크 엔드포인트"""
    return success_response({
        'status': 'healthy',
        'service': 'AAC Interpreter Service',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/dataset/images/<filename>')
def serve_image(filename):
    """AAC 카드 이미지 파일 서빙"""
    try:
        return send_from_directory('dataset/images', filename)
    except FileNotFoundError:
        return error_response(f'이미지 파일을 찾을 수 없습니다: {filename}', 404)

# ===== 1. 사용자 관리 엔드포인트 =====

@app.route('/users', methods=['POST'])
def register_user():
    """사용자 회원가입"""
    try:
        data = validate_json_request()
        if not data:
            return error_response('유효한 JSON 데이터가 필요합니다')

        # 필수 필드 검증
        required_fields = ['user_id', 'name', 'age', 'gender', 'disability_type',
                          'communication_characteristics', 'interesting_topics', 'password']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return error_response(f'필수 필드가 누락되었습니다: {", ".join(missing_fields)}')

        # 성별 매핑 (한국어 → 영어)
        gender_mapping = {
            '남성': 'male',
            '여성': 'female',
            'male': 'male',
            'female': 'female'
        }

        original_gender = data.get('gender', '')
        mapped_gender = gender_mapping.get(original_gender, original_gender)

        # 페르소나 데이터 구성
        persona_data = {
            'name': data.get('name'),
            'age': data.get('age'),
            'gender': mapped_gender,
            'disability_type': data.get('disability_type'),
            'communication_characteristics': data.get('communication_characteristics', ''),
            'interesting_topics': data.get('interesting_topics'),
            'password': data.get('password')
        }

        # 사용자 등록
        result = aac_service.register_user(data.get('user_id'), persona_data)

        if result['status'] == 'success':
            return success_response({
                'user_id': result.get('user_id'),
                'name': data.get('name', ''),
                'status': 'created',
                'message': '회원가입이 완료되었습니다'
            }, 201)
        else:
            return error_response(result['message'])

    except Exception as e:
        print(f"회원가입 오류: {str(e)}")
        return error_response(f'회원가입 처리 중 오류가 발생했습니다: {str(e)}', 500)

@app.route('/users/<user_id>/auth', methods=['POST'])
def login_user(user_id):
    """사용자 로그인"""
    try:
        data = validate_json_request()
        if not data:
            return error_response('유효한 JSON 데이터가 필요합니다')

        if 'password' not in data:
            return error_response('비밀번호가 필요합니다')

        # 사용자 인증
        result = aac_service.authenticate_user(user_id, data['password'])

        response_data = {
            'authenticated': result['authenticated'],
            'message': result['message']
        }

        if result['authenticated']:
            response_data['user_info'] = result.get('user_info')
            return success_response(response_data)
        else:
            return jsonify(response_data), 401

    except Exception as e:
        print(f"로그인 오류: {str(e)}")
        return error_response(f'로그인 처리 중 오류가 발생했습니다: {str(e)}', 500)

@app.route('/users/<user_id>', methods=['GET'])
def get_user_info(user_id):
    """사용자 정보 조회 (비밀번호 제외)"""
    try:
        result = aac_service.get_user_info(user_id)

        if result['status'] == 'success':
            user_data = result['user']
            return success_response({
                'user_id': user_id,
                'name': user_data.get('name', f'사용자{user_id}'),
                'age': user_data.get('age'),
                'gender': user_data.get('gender'),
                'disability_type': user_data.get('disability_type'),
                'communication_characteristics': user_data.get('communication_characteristics'),
                'interesting_topics': user_data.get('interesting_topics', []),
                'preferred_category_types': user_data.get('preferred_category_types', []),
                'created_at': user_data.get('created_at'),
                'updated_at': user_data.get('updated_at')
            })
        else:
            return error_response(result['message'], 404)

    except Exception as e:
        print(f"사용자 조회 오류: {str(e)}")
        return error_response(f'사용자 조회 중 오류가 발생했습니다: {str(e)}', 500)

@app.route('/users/<user_id>/persona', methods=['PUT'])
def update_user_persona(user_id):
    """사용자 페르소나 정보 업데이트"""
    try:
        data = validate_json_request()
        if not data:
            return error_response('유효한 JSON 데이터가 필요합니다')

        # 성별 매핑 처리
        if 'gender' in data:
            gender_mapping = {
                '남성': 'male',
                '여성': 'female',
                'male': 'male',
                'female': 'female'
            }
            data['gender'] = gender_mapping.get(data['gender'], data['gender'])

        # 페르소나 업데이트
        result = aac_service.update_user_persona(user_id, data)

        if result['status'] == 'success':
            return success_response({
                'updated_fields': result['updated_fields'],
                'category_recalculated': result.get('category_recalculated', False),
                'message': result['message']
            })
        else:
            return error_response(result['message'])

    except Exception as e:
        print(f"페르소나 업데이트 오류: {str(e)}")
        return error_response(f'페르소나 업데이트 중 오류가 발생했습니다: {str(e)}', 500)

# ===== 2. 컨텍스트 관리 엔드포인트 =====

@app.route('/contexts', methods=['POST'])
def create_context():
    """새로운 대화 상황 컨텍스트 생성"""
    try:
        data = validate_json_request()
        if not data:
            return error_response('유효한 JSON 데이터가 필요합니다')

        user_id = data.get('user_id') or data.get('userId')
        place = data.get('place', '').strip()
        interaction_partner = data.get('interaction_partner', '').strip()
        current_activity = data.get('current_activity', '').strip()

        # 필수 필드 검증
        if not user_id:
            return error_response('user_id가 필요합니다')
        if not place:
            return error_response('place는 필수 입력사항입니다')
        if not interaction_partner:
            return error_response('interaction_partner는 필수 입력사항입니다')

        # 컨텍스트 생성
        result = aac_service.update_user_context(
            user_id,
            place,
            interaction_partner,
            current_activity if current_activity else None
        )

        if result['status'] == 'success':
            return success_response({
                'context_id': result['context_id'],
                'user_id': user_id,
                'place': place,
                'interaction_partner': interaction_partner,
                'current_activity': current_activity,
                'time': datetime.now().strftime("%H시 %M분"),
                'status': 'created',
                'message': result['message']
            }, 201)
        else:
            return error_response(result['message'])

    except Exception as e:
        print(f"컨텍스트 생성 오류: {str(e)}")
        return error_response(f'컨텍스트 생성 중 오류가 발생했습니다: {str(e)}', 500)

@app.route('/contexts/<context_id>', methods=['GET'])
def get_context(context_id):
    """컨텍스트 정보 조회"""
    try:
        result = aac_service.context_manager.get_context(context_id)

        if result['status'] == 'success':
            return success_response(result['context'])
        else:
            return error_response(result['message'], 404)

    except Exception as e:
        print(f"컨텍스트 조회 오류: {str(e)}")
        return error_response(f'컨텍스트 조회 중 오류가 발생했습니다: {str(e)}', 500)

# ===== 3. 카드 추천 및 선택 엔드포인트 =====

@app.route('/cards/recommendations', methods=['POST'])
def get_card_recommendations():
    """페르소나 기반 개인화된 AAC 카드 추천"""
    try:
        data = validate_json_request()
        if not data:
            return error_response('유효한 JSON 데이터가 필요합니다')

        user_id = data.get('user_id') or data.get('userId')
        context_id = data.get('context_id') or data.get('contextId')

        if not user_id:
            return error_response('user_id가 필요합니다')
        if not context_id:
            return error_response('context_id가 필요합니다')

        # 컨텍스트 정보 조회
        context_result = aac_service.context_manager.get_context(context_id)
        if context_result['status'] != 'success':
            return error_response(f'컨텍스트를 찾을 수 없습니다: {context_id}', 404)

        context_data = {
            'time': context_result['context']['time'],
            'place': context_result['context']['place'],
            'interaction_partner': context_result['context']['interaction_partner'],
            'current_activity': context_result['context']['current_activity']
        }

        # 카드 추천 시스템 상태 확인
        if not hasattr(aac_service, 'card_recommender') or aac_service.card_recommender is None:
            return error_response('카드 추천 시스템이 초기화되지 않았습니다', 503)

        # 카드 선택 인터페이스 생성
        result = aac_service.get_card_selection_interface(user_id, context_data, context_id)

        if result['status'] == 'success':
            interface_data = result['interface_data']
            cards = interface_data['selection_options']

            # 카드 정보 포맷팅
            formatted_cards = []
            for i, card_filename in enumerate(cards):
                # 카드 파일명에서 ID 추출 (예: "2248_물.png" -> "2248")
                card_id = card_filename.split('_')[0] if '_' in card_filename else card_filename.replace('.png', '')
                card_name = card_filename.replace('.png', '').replace('_', ' ')

                formatted_cards.append({
                    'id': card_id,
                    'name': card_name,
                    'filename': card_filename,
                    'image_path': f'/dataset/images/{card_filename}',
                    'index': i
                })

            response_data = {
                'cards': formatted_cards,
                'total': len(formatted_cards),
                'context_info': interface_data.get('context_info'),
                'selection_rules': interface_data.get('selection_rules'),
                'total_pages': interface_data.get('total_pages', 1),
                'current_page': 1
            }

            return success_response(response_data)
        else:
            return error_response('카드 추천 생성에 실패했습니다')

    except Exception as e:
        print(f"카드 추천 오류: {str(e)}")
        return error_response(f'카드 추천 중 오류가 발생했습니다: {str(e)}', 500)

@app.route('/cards/recommendations/history/<context_id>', methods=['GET'])
def get_recommendation_history_summary(context_id):
    """카드 추천 히스토리 요약 조회"""
    try:
        result = aac_service.get_card_recommendation_history_summary(context_id)

        if result['status'] == 'success':
            return success_response({
                'total_pages': result['total_pages'],
                'latest_page': result['latest_page'],
                'history_summary': result['history_summary'],
                'context_id': context_id
            })
        else:
            return error_response(result['message'], 404)

    except Exception as e:
        print(f"추천 히스토리 조회 오류: {str(e)}")
        return error_response(f'추천 히스토리 조회 중 오류가 발생했습니다: {str(e)}', 500)

@app.route('/cards/recommendations/history/<context_id>/page/<int:page_number>', methods=['GET'])
def get_recommendation_history_page(context_id, page_number):
    """카드 추천 히스토리 특정 페이지 조회"""
    try:
        result = aac_service.get_card_recommendation_history_page(context_id, page_number)

        if result['status'] == 'success':
            cards = result['cards']

            # 카드 정보 포맷팅
            formatted_cards = []
            for i, card_filename in enumerate(cards):
                card_id = card_filename.split('_')[0] if '_' in card_filename else card_filename.replace('.png', '')
                card_name = card_filename.replace('.png', '').replace('_', ' ')

                formatted_cards.append({
                    'id': card_id,
                    'name': card_name,
                    'filename': card_filename,
                    'image_path': f'/dataset/images/{card_filename}',
                    'index': i
                })

            return success_response({
                'cards': formatted_cards,
                'page_number': result['page_number'],
                'total_pages': result['total_pages'],
                'timestamp': result['timestamp'],
                'context_id': context_id
            })
        else:
            return error_response(result['message'], 404)

    except Exception as e:
        print(f"추천 페이지 조회 오류: {str(e)}")
        return error_response(f'추천 페이지 조회 중 오류가 발생했습니다: {str(e)}', 500)

@app.route('/cards/validate', methods=['POST'])
def validate_card_selection():
    """사용자 카드 선택 유효성 검증"""
    try:
        data = validate_json_request()
        if not data:
            return error_response('유효한 JSON 데이터가 필요합니다')

        selected_cards = data.get('selected_cards', [])
        available_options = data.get('available_options', [])

        if not selected_cards:
            return error_response('선택된 카드가 없습니다')
        if not available_options:
            return error_response('선택 가능한 카드 옵션이 없습니다')

        # 카드 선택 검증
        result = aac_service.validate_card_selection(selected_cards, available_options)

        if result['status'] == 'success':
            return success_response({
                'valid': result['valid'],
                'selected_count': len(selected_cards),
                'message': result['message']
            })
        else:
            return success_response({
                'valid': result['valid'],
                'message': result['message']
            }, 422)  # Unprocessable Entity

    except Exception as e:
        print(f"카드 선택 검증 오류: {str(e)}")
        return error_response(f'카드 선택 검증 중 오류가 발생했습니다: {str(e)}', 500)

# ===== 4. 카드 해석 엔드포인트 =====

@app.route('/cards/interpret', methods=['POST'])
def interpret_cards():
    """선택된 AAC 카드들 해석"""
    try:
        data = validate_json_request()
        if not data:
            return error_response('유효한 JSON 데이터가 필요합니다')

        selected_cards = data.get('selected_cards', []) or data.get('selectedCards', [])
        user_id = data.get('user_id') or data.get('userId')
        context_id = data.get('context_id') or data.get('contextId')

        if not user_id:
            return error_response('user_id가 필요합니다')
        if not selected_cards:
            return error_response('선택된 카드가 필요합니다')

        # 선택된 카드 파일명 추출
        card_filenames = []
        if isinstance(selected_cards[0], dict):
            # 카드 객체에서 filename 우선 사용, 없으면 name으로 생성
            for card in selected_cards:
                if 'filename' in card:
                    card_filenames.append(card['filename'])
                elif 'name' in card:
                    name = card['name'].replace(' ', '_') + '.png'
                    card_filenames.append(name)
                else:
                    return error_response('카드 정보가 불완전합니다')
        else:
            # 문자열 배열인 경우 그대로 사용
            card_filenames = selected_cards

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

        # 카드 해석기 상태 확인
        if not hasattr(aac_service, 'card_interpreter') or aac_service.card_interpreter is None:
            return error_response('카드 해석 시스템이 초기화되지 않았습니다', 503)

        # 카드 해석 수행
        result = aac_service.interpret_cards(user_id, card_filenames, context)

        if result['status'] == 'success':
            return success_response({
                'interpretations': result['interpretations'],
                'feedback_id': result['feedback_id'],
                'method': result['method'],
                'selected_cards': card_filenames,
                'interpretation_count': len(result['interpretations']),
                'message': result['message']
            })
        else:
            return error_response('카드 해석에 실패했습니다')

    except Exception as e:
        print(f"카드 해석 오류: {str(e)}")
        return error_response(f'카드 해석 중 오류가 발생했습니다: {str(e)}', 500)

# ===== 5. 피드백 관리 엔드포인트 =====

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Partner 피드백 제출 (확인 요청 및 응답)"""
    try:
        data = validate_json_request()
        if not data:
            return error_response('유효한 JSON 데이터가 필요합니다')

        feedback_type = data.get('type', 'partner_feedback')

        if feedback_type == 'partner_confirmation':
            # Partner의 해석 확인 요청
            user_id = data.get('user_id') or data.get('userId')
            cards = data.get('cards', [])
            context = data.get('context', {})
            interpretations = data.get('interpretations', [])
            partner_info = data.get('partner_info', {}) or data.get('partnerInfo', {})

            # 필수 필드 검증
            if not all([user_id, cards, interpretations]):
                return error_response('user_id, cards, interpretations가 필요합니다')

            result = aac_service.request_partner_confirmation(
                user_id=user_id,
                cards=cards,
                context=context,
                interpretations=interpretations,
                partner_info=partner_info
            )

            if result['status'] == 'success':
                return success_response({
                    'confirmation_id': result['confirmation_id'],
                    'confirmation_request': result['confirmation_request'],
                    'message': result['message']
                }, 201)
            else:
                return error_response(result['message'])

        elif feedback_type == 'partner_submit':
            # Partner의 피드백 제출
            confirmation_id = data.get('confirmation_id') or data.get('confirmationId')
            selected_interpretation_index = data.get('selected_interpretation_index') or data.get('selectedInterpretationIndex')
            direct_feedback = data.get('direct_feedback') or data.get('directFeedback')

            if not confirmation_id:
                return error_response('confirmation_id가 필요합니다')

            result = aac_service.submit_partner_feedback(
                confirmation_id=confirmation_id,
                selected_interpretation_index=selected_interpretation_index,
                direct_feedback=direct_feedback
            )

            if result['status'] == 'success':
                return success_response({
                    'feedback_result': result['feedback_result'],
                    'message': result['message']
                })
            else:
                return error_response(result['message'])

        else:
            return error_response(f'지원하지 않는 피드백 타입입니다: {feedback_type}')

    except Exception as e:
        print(f"피드백 제출 오류: {str(e)}")
        return error_response(f'피드백 제출 중 오류가 발생했습니다: {str(e)}', 500)

@app.route('/feedback/pending', methods=['GET'])
def get_pending_feedback():
    """대기 중인 Partner 확인 요청들 조회"""
    try:
        partner_filter = request.args.get('partner')

        # 이 메서드가 구현되어 있지 않다면 임시로 빈 결과 반환
        try:
            result = aac_service.get_pending_partner_confirmations(partner_filter)
        except AttributeError:
            result = {
                'pending_requests': [],
                'total_count': 0
            }

        return success_response({
            'pending_requests': result['pending_requests'],
            'total_count': result['total_count'],
            'message': '대기 중인 확인 요청을 조회했습니다'
        })

    except Exception as e:
        print(f"대기 피드백 조회 오류: {str(e)}")
        return error_response(f'대기 피드백 조회 중 오류가 발생했습니다: {str(e)}', 500)

# ===== 6. 메모리 관리 엔드포인트 =====

@app.route('/memory/update', methods=['POST'])
def update_memory():
    """대화 메모리 업데이트 - 카드-해석 연결성 학습"""
    try:
        data = validate_json_request()
        if not data:
            return error_response('유효한 JSON 데이터가 필요합니다')

        user_id = data.get('user_id') or data.get('userId')
        cards = data.get('cards', [])
        context = data.get('context', {})
        interpretations = data.get('interpretations', [])
        final_interpretation = data.get('final_interpretation') or data.get('finalInterpretation')

        if not user_id:
            return error_response('user_id가 필요합니다')

        # ConversationSummaryMemory가 없는 경우 기본 처리
        if not hasattr(aac_service, 'conversation_memory') or aac_service.conversation_memory is None:
            print(f"메모리 업데이트 (기본 모드) - 사용자: {user_id}")
            return success_response({
                'memory_updated': True,
                'message': '메모리 업데이트 완료 (기본 모드)'
            })

        # 실제 메모리 시스템 사용
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
                return success_response({
                    'summary': result['summary'],
                    'memory_updated': result['memory_updated'],
                    'message': result['message']
                })
            else:
                return error_response(result['message'])
        else:
            # 기본 처리 (기존 호환성)
            print(f"메모리 업데이트 - 사용자: {user_id}")
            return success_response({
                'memory_updated': True,
                'message': '메모리 업데이트 완료'
            })

    except Exception as e:
        print(f"메모리 업데이트 오류: {str(e)}")
        return error_response(f'메모리 업데이트 중 오류가 발생했습니다: {str(e)}', 500)

@app.route('/memory/<user_id>/summary', methods=['GET'])
def get_memory_summary(user_id):
    """사용자 메모리 요약 조회"""
    try:
        if not hasattr(aac_service, 'conversation_memory') or aac_service.conversation_memory is None:
            return success_response({
                'summary': '',
                'conversation_count': 0,
                'status': 'not_available',
                'message': '메모리 시스템이 사용할 수 없습니다'
            })

        result = aac_service.conversation_memory.get_user_memory_summary(user_id)

        return success_response({
            'summary': result['summary'],
            'conversation_count': result['conversation_count'],
            'status': result['status'],
            'user_id': user_id
        })

    except Exception as e:
        print(f"메모리 요약 조회 오류: {str(e)}")
        return error_response(f'메모리 요약 조회 중 오류가 발생했습니다: {str(e)}', 500)

@app.route('/memory/<user_id>/patterns', methods=['GET'])
def get_memory_patterns(user_id):
    """사용자의 최근 사용 패턴 조회"""
    try:
        limit = request.args.get('limit', 5, type=int)

        if not hasattr(aac_service, 'conversation_memory') or aac_service.conversation_memory is None:
            return success_response({
                'recent_patterns': [],
                'suggestions': [],
                'status': 'not_available',
                'message': '메모리 시스템이 사용할 수 없습니다'
            })

        result = aac_service.conversation_memory.get_recent_patterns(user_id, limit)

        return success_response({
            'recent_patterns': result['recent_patterns'],
            'suggestions': result['suggestions'],
            'status': result['status'],
            'user_id': user_id,
            'limit': limit
        })

    except Exception as e:
        print(f"메모리 패턴 조회 오류: {str(e)}")
        return error_response(f'메모리 패턴 조회 중 오류가 발생했습니다: {str(e)}', 500)

# ===== 7. 관리자 엔드포인트 =====

@app.route('/admin/cleanup', methods=['POST'])
def cleanup_system():
    """시스템 정리 (오래된 데이터 삭제)"""
    try:
        data = validate_json_request() or {}
        max_age_days = data.get('max_age_days', 30)

        # 컨텍스트 정리
        try:
            context_result = aac_service.context_manager.cleanup_old_contexts(max_age_days)
        except AttributeError:
            context_result = {'cleaned_count': 0, 'remaining_count': 0}

        # 피드백 요청 정리
        try:
            feedback_result = aac_service.feedback_manager.cleanup_old_requests(max_age_days)
        except AttributeError:
            feedback_result = {'cleaned_count': 0, 'remaining_count': 0}

        return success_response({
            'context_cleanup': {
                'cleaned_count': context_result['cleaned_count'],
                'remaining_count': context_result['remaining_count']
            },
            'feedback_cleanup': {
                'cleaned_count': feedback_result['cleaned_count'],
                'remaining_count': feedback_result['remaining_count']
            },
            'max_age_days': max_age_days,
            'message': f'{max_age_days}일 이상 된 데이터가 정리되었습니다'
        })

    except Exception as e:
        print(f"시스템 정리 오류: {str(e)}")
        return error_response(f'시스템 정리 중 오류가 발생했습니다: {str(e)}', 500)

# ===== 서버 시작 =====

if __name__ == '__main__':
    print("AAC Interpreter API Server 시작 중...")
    print("서버 주소: http://localhost:8000")
    print("헬스체크: http://localhost:8000/health")
    print("사용 가능한 엔드포인트:")
    print("사용자 관리:")
    print("  POST /users - 회원가입")
    print("  POST /users/<id>/auth - 로그인")
    print("  GET  /users/<id> - 사용자 조회")
    print("  PUT  /users/<id>/persona - 페르소나 업데이트")
    print("컨텍스트 관리:")
    print("  POST /contexts - 대화 상황 생성")
    print("  GET  /contexts/<id> - 컨텍스트 조회")
    print("카드 추천 및 해석:")
    print("  POST /cards/recommendations - 카드 추천")
    print("  POST /cards/validate - 카드 선택 검증")
    print("  POST /cards/interpret - 카드 해석")
    print("  GET  /cards/recommendations/history/<id> - 추천 히스토리")
    print("피드백:")
    print("  POST /feedback - 피드백 제출")
    print("  GET  /feedback/pending - 대기 피드백 조회")
    print("메모리:")
    print("  POST /memory/update - 메모리 업데이트")
    print("  GET /memory/<id>/summary - 메모리 요약")
    print("  GET /memory/<id>/patterns - 사용 패턴")

    app.run(host='0.0.0.0', port=8000, debug=True)
