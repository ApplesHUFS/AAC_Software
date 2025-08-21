from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import uuid
from datetime import datetime

from aac_interpreter_service import AACInterpreterService

app = Flask(__name__)
CORS(app)

# AAC 서비스 인스턴스 생성
aac_service = AACInterpreterService()

# 에러 핸들러
@app.errorhandler(Exception)
def handle_error(error):
    print(f"Error occurred: {str(error)}")
    traceback.print_exc()
    return jsonify({
        'error': str(error),
        'message': 'Internal server error occurred'
    }), 500

# 루트 경로 처리
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'AAC Interpreter Service API',
        'version': '1.0.0',
        'status': 'running',
        'available_endpoints': {
            'health': '/health',
            'users': '/users',
            'contexts': '/contexts',
            'cards': '/cards/*',
            'feedback': '/feedback',
            'memory': '/memory/*'
        }
    })

# 헬스체크 엔드포인트
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'AAC Interpreter Service',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# ===== 사용자 관리 엔드포인트 =====

@app.route('/users', methods=['POST'])
def create_user():
    """새 사용자 생성"""
    try:
        data = request.get_json()

        # 페르소나 데이터 생성
        persona_data = {
            'name': data.get('name'),
            'age': data.get('age'),
            'gender': data.get('gender'),
            'disability_type': data.get('disability_type'),
            'communication_characteristics': data.get('communication_characteristics', ''),
            'interesting_topics': data.get('interesting_topics'),
            'password': data.get('password')
        }

        result = aac_service.register_user(persona_data)

        return jsonify({
            'id': str(result.get('user_id')),
            'name': data.get('name', ''),
            'status': 'created'
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """사용자 정보 조회"""
    try:
        result = aac_service.get_user_info(int(user_id))

        if result['status'] == 'success':
            user_data = result['user']
            return jsonify({
                'id': user_id,
                'name': user_data.get('name', f'사용자{user_id}'),
                'age': user_data.get('age'),
                'gender': user_data.get('gender'),
                'disability_type': user_data.get('disability_type'),
                'communication_characteristics': user_data.get('communication_characteristics'),
                'interesting_topics': user_data.get('interesting_topics', []),
                'preferred_category_types': user_data.get('preferred_category_types', []),
                'created_at': user_data.get('created_at'),
                'updated_at': user_data.get('updated_at'),
                'needs_category_recalculation': user_data.get('needs_category_recalculation', False)
            })
        else:
            return jsonify({'error': result['message']}), 404

    except ValueError:
        return jsonify({'error': '유효하지 않은 사용자 ID입니다'}), 400
    except Exception as e:
        print(f"사용자 조회 오류: {str(e)}")
        return jsonify({'error': f'사용자 조회 실패: {str(e)}'}), 500

@app.route('/users/<user_id>/persona', methods=['PUT'])
def update_persona(user_id):
    """사용자 페르소나 정보 업데이트"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON 데이터가 필요합니다'}), 400

        # UserManager의 업데이트 기능 사용
        result = aac_service.user_manager.update_user_persona(int(user_id), data)

        if result['status'] == 'success':
            # interesting_topics가 업데이트되어 카테고리 재계산이 필요한 경우
            user_info = aac_service.get_user_info(int(user_id))
            if (user_info['status'] == 'success' and
                user_info['user'].get('needs_category_recalculation', False)):

                # preferred_category_types 재계산
                interesting_topics = user_info['user'].get('interesting_topics', [])
                preferred_categories = aac_service._calculate_preferred_categories(interesting_topics)

                # 재계산된 카테고리 적용
                category_result = aac_service.user_manager.update_preferred_categories(
                    int(user_id), preferred_categories
                )

                if category_result['status'] == 'success':
                    result['message'] += ' 선호 카테고리도 재계산되었습니다.'

            return jsonify({
                'success': True,
                'updated_fields': result['updated_fields'],
                'message': result['message']
            })
        else:
            return jsonify({'error': result['message']}), 400

    except ValueError:
        return jsonify({'error': '유효하지 않은 사용자 ID입니다'}), 400
    except Exception as e:
        print(f"페르소나 업데이트 오류: {str(e)}")
        return jsonify({'error': f'페르소나 업데이트 실패: {str(e)}'}), 500

@app.route('/users/<user_id>/auth', methods=['POST'])
def authenticate_user(user_id):
    """사용자 인증"""
    try:
        data = request.get_json()
        if not data or 'password' not in data:
            return jsonify({'error': 'password가 필요합니다'}), 400

        result = aac_service.authenticate_user(int(user_id), data['password'])

        return jsonify({
            'authenticated': result['authenticated'],
            'message': result['message'],
            'user_info': result.get('user_info')
        }), 200 if result['authenticated'] else 401

    except ValueError:
        return jsonify({'error': '유효하지 않은 사용자 ID입니다'}), 400
    except Exception as e:
        print(f"사용자 인증 오류: {str(e)}")
        return jsonify({'error': f'인증 실패: {str(e)}'}), 500

# ===== 컨텍스트 관리 엔드포인트 =====

@app.route('/contexts', methods=['POST'])
def create_context():
    """새로운 대화 상황 컨텍스트 생성"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON 데이터가 필요합니다'}), 400

        user_id = data.get('userId')
        place = data.get('place', '').strip()
        interaction_partner = data.get('interaction_partner', '').strip()
        current_activity = data.get('current_activity', '').strip()

        # 필수 필드 검증
        if not place:
            return jsonify({'error': 'place는 필수 입력사항입니다'}), 400
        if not interaction_partner:
            return jsonify({'error': 'interaction_partner는 필수 입력사항입니다'}), 400

        # AAC 서비스를 통해 컨텍스트 생성
        result = aac_service.update_user_context(
            int(user_id) if user_id else None,
            place,
            interaction_partner,
            current_activity if current_activity else None
        )

        if result['status'] == 'success':
            return jsonify({
                'id': result['context_id'],
                'userId': user_id,
                'place': place,
                'interaction_partner': interaction_partner,
                'current_activity': current_activity,
                'time': datetime.now().strftime("%H시 %M분"),
                'status': 'created',
                'message': result['message']
            }), 201
        else:
            return jsonify({'error': result['message']}), 400

    except ValueError:
        return jsonify({'error': '유효하지 않은 사용자 ID입니다'}), 400
    except Exception as e:
        print(f"컨텍스트 생성 오류: {str(e)}")
        return jsonify({'error': f'컨텍스트 생성 실패: {str(e)}'}), 500

@app.route('/contexts/<context_id>', methods=['GET'])
def get_context(context_id):
    """컨텍스트 정보 조회"""
    try:
        # ContextManager를 통해 실제 컨텍스트 조회
        result = aac_service.context_manager.get_context(context_id)

        if result['status'] == 'success':
            return jsonify(result['context'])
        else:
            return jsonify({'error': result['message']}), 404

    except Exception as e:
        print(f"컨텍스트 조회 오류: {str(e)}")
        return jsonify({'error': f'컨텍스트 조회 실패: {str(e)}'}), 500

@app.route('/users/<user_id>/contexts', methods=['GET'])
def get_user_contexts(user_id):
    """사용자의 컨텍스트 이력 조회"""
    try:
        limit = request.args.get('limit', 10, type=int)

        result = aac_service.context_manager.get_user_contexts(str(user_id), limit)

        return jsonify({
            'contexts': result['contexts'],
            'total_count': result['total_count'],
            'message': result['message']
        })

    except Exception as e:
        print(f"사용자 컨텍스트 조회 오류: {str(e)}")
        return jsonify({'error': f'컨텍스트 조회 실패: {str(e)}'}), 500

# ===== 카드 추천 및 해석 엔드포인트 =====

@app.route('/cards/recommendations', methods=['POST'])
def get_card_recommendations():
    """개인화된 AAC 카드 추천"""
    try:
        data = request.get_json()
        user_id = data.get('userId')
        context_id = data.get('contextId')

        if not user_id:
            return jsonify({'error': 'userId가 필요합니다'}), 400

        # 컨텍스트 정보 조회
        context_result = aac_service.context_manager.get_context(context_id)
        if context_result['status'] == 'success':
            context_data = {
                'time': context_result['context']['time'],
                'place': context_result['context']['place'],
                'interaction_partner': context_result['context']['interaction_partner'],
                'current_activity': context_result['context']['current_activity']
            }
        else:
            return jsonify({'error': f'컨텍스트를 찾을 수 없습니다: {context_id}'}), 404

        # AAC 서비스가 없거나 초기화되지 않은 경우 처리
        if not hasattr(aac_service, 'card_recommender') or aac_service.card_recommender is None:
            return jsonify({'error': 'Failed to get recommendations'}), 400

        result = aac_service.get_card_selection_interface(int(user_id), context_data)

        if result['status'] == 'success':
            interface_data = result['interface_data']
            cards = interface_data['selection_options']

            # 카드 정보 제공
            formatted_cards = []
            for i, card_filename in enumerate(cards):
                formatted_cards.append({
                    'id': i + 1,
                    'name': card_filename.replace('.png', '').replace('_', ' '),
                    'filename': card_filename,  # "2248_물.png"
                    'image_path': f'dataset/images/{card_filename}'
                })

            return jsonify({
                'cards': formatted_cards,
                'total': len(formatted_cards)
            })
        else:
            return jsonify({'error': 'Failed to get recommendations'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/cards/interpret', methods=['POST'])
def interpret_cards():
    """선택된 AAC 카드들 해석"""
    try:
        data = request.get_json()
        selected_cards = data.get('selectedCards', [])
        user_id = data.get('userId')
        context_id = data.get('contextId')

        if not user_id:
            return jsonify({'error': 'userId가 필요합니다'}), 400
        if not selected_cards:
            return jsonify({'error': 'selectedCards가 필요합니다'}), 400

        # 선택된 카드 파일명 추출
        if isinstance(selected_cards[0], dict):
            # 카드 객체에서 filename 우선 사용, 없으면 name으로 생성
            card_filenames = []
            for card in selected_cards:
                if 'filename' in card:
                    card_filenames.append(card['filename'])
                elif 'name' in card:
                    name = card['name'].replace(' ', '_') + '.png'
                    card_filenames.append(name)
                else:
                    card_filenames.append('')
        else:
            # 문자열 배열인 경우 그대로 사용
            card_filenames = selected_cards

        # 컨텍스트 처리
        if context_id:
            context_result = aac_service.context_manager.get_context(context_id)
            if context_result['status'] == 'success':
                context = {
                    'time': context_result['context']['time'],
                    'place': context_result['context']['place'],
                    'interaction_partner': context_result['context']['interaction_partner'],
                    'current_activity': context_result['context']['current_activity']
                }

        # CardInterpreter가 없는 경우 처리
        if not hasattr(aac_service, 'card_interpreter') or aac_service.card_interpreter is None:
            return jsonify({'error': 'Failed to interpret cards'}), 400

        result = aac_service.interpret_cards(
            int(user_id),
            card_filenames,  # 실제 파일명 사용
            context
        )

        if result['status'] == 'success':
            # 해석 문자열 배열 반환
            return jsonify({
                'interpretations': result['interpretations'],
                'feedback_id': result['feedback_id'],
                'method': result['method'],
                'message': result['message']
            })
        else:
            return jsonify({'error': 'Failed to interpret cards'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ===== 피드백 관리 엔드포인트 =====

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Partner 피드백 제출"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON 데이터가 필요합니다'}), 400

        feedback_type = data.get('type', 'partner_feedback')

        if feedback_type == 'partner_confirmation':
            # Partner의 해석 확인 요청
            user_id = data.get('userId')
            cards = data.get('cards', [])
            context = data.get('context', {})
            interpretations = data.get('interpretations', [])
            partner_info = data.get('partnerInfo', {})

            if not all([user_id, cards, interpretations]):
                return jsonify({'error': 'userId, cards, interpretations가 필요합니다'}), 400

            result = aac_service.request_partner_confirmation(
                user_id=int(user_id),
                cards=cards,
                context=context,
                interpretations=interpretations,
                partner_info=partner_info
            )

            if result['status'] == 'success':
                return jsonify({
                    'success': True,
                    'confirmation_id': result['confirmation_id'],
                    'message': result['message']
                })
            else:
                return jsonify({'error': result['message']}), 400

        elif feedback_type == 'partner_submit':
            # Partner의 피드백 제출
            confirmation_id = data.get('confirmationId')
            selected_interpretation_index = data.get('selectedInterpretationIndex')
            direct_feedback = data.get('directFeedback')

            if not confirmation_id:
                return jsonify({'error': 'confirmationId가 필요합니다'}), 400

            result = aac_service.submit_partner_feedback(
                confirmation_id=confirmation_id,
                selected_interpretation_index=selected_interpretation_index,
                direct_feedback=direct_feedback
            )

            if result['status'] == 'success':
                return jsonify({
                    'success': True,
                    'feedback_result': result['feedback_result'],
                    'message': result['message']
                })
            else:
                return jsonify({'error': result['message']}), 400

    except ValueError:
        return jsonify({'error': '유효하지 않은 사용자 ID입니다'}), 400
    except Exception as e:
        print(f"피드백 제출 오류: {str(e)}")
        return jsonify({'error': f'피드백 제출 실패: {str(e)}'}), 500

@app.route('/feedback/pending', methods=['GET'])
def get_pending_feedback():
    """대기 중인 Partner 확인 요청들 조회"""
    try:
        partner_filter = request.args.get('partner')

        result = aac_service.get_pending_partner_confirmations(partner_filter)

        return jsonify({
            'pending_requests': result['pending_requests'],
            'total_count': result['total_count'],
            'message': '대기 중인 확인 요청을 조회했습니다.'
        })

    except Exception as e:
        print(f"대기 피드백 조회 오류: {str(e)}")
        return jsonify({'error': f'대기 피드백 조회 실패: {str(e)}'}), 500

# ===== 메모리 관리 엔드포인트 =====

@app.route('/memory/update', methods=['POST'])
def update_memory():
    """대화 메모리 업데이트 - 실제 시스템 연결"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON 데이터가 필요합니다'}), 400

        user_id = data.get('userId')
        cards = data.get('cards', [])
        context = data.get('context', {})
        interpretations = data.get('interpretations', [])
        final_interpretation = data.get('finalInterpretation')  # Partner가 선택/입력한 최종 해석

        if not user_id:
            return jsonify({'error': 'userId가 필요합니다'}), 400

        # ConversationSummaryMemory가 없는 경우 기본 처리
        if not hasattr(aac_service, 'conversation_memory') or aac_service.conversation_memory is None:
            print(f"Memory update for user {user_id}: {data}")
            return jsonify({
                'success': True,
                'message': 'Memory updated successfully (basic mode)'
            })

        # 실제 메모리 시스템 사용
        if final_interpretation and cards:
            result = aac_service.conversation_memory.add_conversation_memory(
                user_id=int(user_id),
                cards=cards,
                context=context,
                interpretations=interpretations,
                selected_interpretation=final_interpretation if final_interpretation in interpretations else None,
                user_correction=final_interpretation if final_interpretation not in interpretations else None
            )

            if result['status'] == 'success':
                return jsonify({
                    'success': True,
                    'summary': result['summary'],
                    'memory_updated': result['memory_updated'],
                    'message': result['message']
                })
            else:
                return jsonify({'error': result['message']}), 400
        else:
            # 기본 처리 (기존 호환성)
            print(f"Memory update for user {user_id}: {data}")
            return jsonify({
                'success': True,
                'message': 'Memory updated successfully'
            })

    except ValueError:
        return jsonify({'error': '유효하지 않은 사용자 ID입니다'}), 400
    except Exception as e:
        print(f"메모리 업데이트 오류: {str(e)}")
        return jsonify({'error': f'메모리 업데이트 실패: {str(e)}'}), 500

@app.route('/memory/<user_id>/summary', methods=['GET'])
def get_memory_summary(user_id):
    """사용자 메모리 요약 조회"""
    try:
        result = aac_service.conversation_memory.get_user_memory_summary(int(user_id))

        return jsonify({
            'summary': result['summary'],
            'conversation_count': result['conversation_count'],
            'status': result['status']
        })

    except ValueError:
        return jsonify({'error': '유효하지 않은 사용자 ID입니다'}), 400
    except Exception as e:
        print(f"메모리 요약 조회 오류: {str(e)}")
        return jsonify({'error': f'메모리 요약 조회 실패: {str(e)}'}), 500

@app.route('/memory/<user_id>/patterns', methods=['GET'])
def get_memory_patterns(user_id):
    """사용자의 최근 사용 패턴 조회"""
    try:
        limit = request.args.get('limit', 5, type=int)

        result = aac_service.conversation_memory.get_recent_patterns(int(user_id), limit)

        return jsonify({
            'recent_patterns': result['recent_patterns'],
            'suggestions': result['suggestions'],
            'status': result['status']
        })

    except ValueError:
        return jsonify({'error': '유효하지 않은 사용자 ID입니다'}), 400
    except Exception as e:
        print(f"메모리 패턴 조회 오류: {str(e)}")
        return jsonify({'error': f'메모리 패턴 조회 실패: {str(e)}'}), 500

# ===== 시스템 관리 엔드포인트 =====

@app.route('/admin/cleanup', methods=['POST'])
def cleanup_system():
    """시스템 정리 (오래된 데이터 삭제)"""
    try:
        data = request.get_json() or {}
        max_age_days = data.get('maxAgeDays', 30)

        # 컨텍스트 정리
        context_result = aac_service.context_manager.cleanup_old_contexts(max_age_days)

        # 피드백 요청 정리
        feedback_result = aac_service.feedback_manager.cleanup_old_requests(max_age_days)

        return jsonify({
            'success': True,
            'context_cleanup': {
                'cleaned_count': context_result['cleaned_count'],
                'remaining_count': context_result['remaining_count']
            },
            'feedback_cleanup': {
                'cleaned_count': feedback_result['cleaned_count'],
                'remaining_count': feedback_result['remaining_count']
            },
            'message': f'{max_age_days}일 이상 된 데이터가 정리되었습니다.'
        })

    except Exception as e:
        print(f"시스템 정리 오류: {str(e)}")
        return jsonify({'error': f'시스템 정리 실패: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting AAC Interpreter API Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔍 Health check: http://localhost:8000/health")
    print("📚 Available endpoints:")
    print("   POST /users - 사용자 생성")
    print("   GET  /users/<id> - 사용자 조회")
    print("   PUT  /users/<id>/persona - 페르소나 업데이트")
    print("   POST /users/<id>/auth - 사용자 인증")
    print("   POST /contexts - 컨텍스트 생성")
    print("   GET  /contexts/<id> - 컨텍스트 조회")
    print("   POST /cards/recommendations - 카드 추천")
    print("   POST /cards/interpret - 카드 해석")
    print("   POST /feedback - 피드백 제출")
    print("   GET  /feedback/pending - 대기 피드백 조회")
    print("   POST /memory/update - 메모리 업데이트")
    print("   GET  /memory/<id>/summary - 메모리 요약")
    app.run(host='0.0.0.0', port=8000, debug=True)
