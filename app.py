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

# 헬스체크 엔드포인트
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'AAC Interpreter Service',
        'timestamp': datetime.now().isoformat()
    })

# 사용자 생성
@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()

        # 기본 페르소나 데이터 생성
        persona_data = {
            'name': data.get('name', ''),
            'age': None,
            'gender': None,
            'disability_type': None,
            'communication_characteristics': '',
            'interesting_topics': ''
        }

        result = aac_service.register_user(persona_data)

        return jsonify({
            'id': str(result.get('user_id')),
            'name': data.get('name', ''),
            'status': 'created'
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 사용자 정보 조회
@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        result = aac_service.get_user_info(int(user_id))

        if not result.get('success'):
            return jsonify({'error': 'User not found'}), 404

        return jsonify(result.get('user_info', {}))

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 페르소나 정보 업데이트
@app.route('/users/<user_id>/persona', methods=['PUT'])
def update_persona(user_id):
    try:
        data = request.get_json()

        # 기존 사용자 정보 가져오기
        user_result = aac_service.get_user_info(int(user_id))
        if not user_result.get('success'):
            return jsonify({'error': 'User not found'}), 404

        # 페르소나 데이터 업데이트 (실제 구현에서는 사용자 정보를 업데이트하는 로직 필요)
        return jsonify({'success': True, 'message': 'Persona updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 컨텍스트 생성
@app.route('/contexts', methods=['POST'])
def create_context():
    try:
        data = request.get_json()
        user_id = data.get('userId')

        context_data = {
            'time': data.get('time', datetime.now().isoformat()),
            'place': data.get('place', ''),
            'interaction_partner': data.get('interaction_partner', ''),
            'current_activity': data.get('current_activity', '')
        }

        result = aac_service.update_user_context(
            int(user_id),
            context_data['place'],
            context_data['interaction_partner'],
            context_data.get('current_activity')
        )

        context_id = str(uuid.uuid4())

        return jsonify({
            'id': context_id,
            'status': 'created',
            **context_data
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 컨텍스트 조회
@app.route('/contexts/<context_id>', methods=['GET'])
def get_context(context_id):
    try:
        # 간단한 컨텍스트 정보 반환 (실제 구현에서는 데이터베이스에서 조회)
        return jsonify({
            'id': context_id,
            'status': 'active'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 카드 추천
@app.route('/cards/recommendations', methods=['POST'])
def get_card_recommendations():
    try:
        data = request.get_json()
        user_id = data.get('userId')
        context_id = data.get('contextId')

        # 더미 컨텍스트 데이터로 카드 추천 요청
        context_data = {
            'place': '집',
            'interaction_partner': '가족',
            'current_activity': '일상대화'
        }

        result = aac_service.get_card_selection_interface(int(user_id), context_data)

        if result.get('success'):
            cards = result.get('card_options', [])
            # 카드 데이터 포맷 변환
            formatted_cards = []
            for i, card in enumerate(cards):
                formatted_cards.append({
                    'id': i + 1,
                    'name': card,
                    'category': '일반',
                    'image_path': None
                })

            return jsonify({
                'cards': formatted_cards,
                'total': len(formatted_cards)
            })
        else:
            return jsonify({'error': 'Failed to get recommendations'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 카드 해석
@app.route('/cards/interpret', methods=['POST'])
def interpret_cards():
    try:
        data = request.get_json()
        selected_cards = data.get('selectedCards', [])
        user_id = data.get('userId')
        context_id = data.get('contextId')

        # 선택된 카드 이름 추출
        card_names = [card.get('name', '') for card in selected_cards]

        # 더미 컨텍스트와 페르소나로 해석 요청
        context = {
            'place': '집',
            'interaction_partner': '가족'
        }

        persona = {
            'age': 10,
            'disability_type': 'autism'
        }

        result = aac_service.interpret_cards(
            int(user_id),
            card_names,
            context,
            persona
        )

        if result.get('success'):
            interpretations_data = result.get('interpretations', {})

            # 해석 결과를 배열 형태로 변환
            interpretations = []
            if isinstance(interpretations_data, dict):
                for i, (key, value) in enumerate(interpretations_data.items()):
                    interpretations.append({
                        'text': value,
                        'context': f'카드 조합: {", ".join(card_names)}',
                        'confidence': 0.8 - (i * 0.1)  # 순서대로 신뢰도 감소
                    })

            # 최소 3개의 해석 보장
            while len(interpretations) < 3:
                interpretations.append({
                    'text': f'선택하신 카드들을 통해 {len(interpretations)+1}번째 의미를 표현하고 계신 것 같습니다.',
                    'context': '일반적인 해석',
                    'confidence': 0.6 - (len(interpretations) * 0.1)
                })

            return jsonify({
                'interpretations': interpretations[:3]  # 상위 3개만 반환
            })
        else:
            return jsonify({'error': 'Failed to interpret cards'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 피드백 제출
@app.route('/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        user_id = data.get('userId')

        # 피드백 데이터 처리 (실제 구현에서는 데이터베이스에 저장)
        print(f"Feedback received for user {user_id}: {data}")

        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 메모리 업데이트
@app.route('/memory/update', methods=['POST'])
def update_memory():
    try:
        data = request.get_json()
        user_id = data.get('userId')

        # 메모리 업데이트 처리 (실제 구현에서는 대화 메모리 시스템 연동)
        print(f"Memory update for user {user_id}: {data}")

        return jsonify({
            'success': True,
            'message': 'Memory updated successfully'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("🚀 Starting AAC Interpreter API Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔍 Health check: http://localhost:8000/health")
    app.run(host='0.0.0.0', port=8000, debug=True)
