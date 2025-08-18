import unittest
import json
import tempfile
from unittest.mock import Mock, patch
from pathlib import Path
from src.card_recommender import CardRecommender


class TestCardRecommender(unittest.TestCase):
    
    def setUp(self):
        """테스트 초기화"""
        # 테스트 데이터 생성
        self.test_cluster_tags = {
            "1": ["음식", "식사", "간식"],
            "2": ["놀이", "게임", "재미"],
            "3": ["감정", "기분", "느낌"]
        }
        
        self.test_embeddings = {
            "filenames": ["food1.png", "food2.png", "play1.png", "happy.png"],
            "image_embeddings": [[0.1, 0.2, 0.3], [0.2, 0.3, 0.4], [0.5, 0.6, 0.7], [0.8, 0.9, 1.0]],
            "text_embeddings": [[0.1, 0.1, 0.1], [0.2, 0.2, 0.2], [0.3, 0.3, 0.3], [0.4, 0.4, 0.4]]
        }
        
        self.test_clustering_results = {
            "clustered_files": {
                "1": ["food1.png", "food2.png"],
                "2": ["play1.png"],
                "3": ["happy.png"]
            }
        }
        
        # 임시 파일들 생성
        self.cluster_tags_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(self.test_cluster_tags, self.cluster_tags_file)
        self.cluster_tags_file.close()
        
        self.embeddings_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(self.test_embeddings, self.embeddings_file)
        self.embeddings_file.close()
        
        self.clustering_results_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(self.test_clustering_results, self.clustering_results_file)
        self.clustering_results_file.close()
        
        # CardRecommender 초기화
        self.recommender = CardRecommender(
            cluster_tags_path=self.cluster_tags_file.name,
            embeddings_path=self.embeddings_file.name,
            clustering_results_path=self.clustering_results_file.name
        )
    
    def tearDown(self):
        """테스트 정리"""
        import os
        for file_path in [self.cluster_tags_file.name, self.embeddings_file.name, self.clustering_results_file.name]:
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    def test_initialization_success(self):
        """초기화 성공 테스트"""
        self.assertEqual(len(self.recommender.cluster_tags), 3)
        self.assertEqual(len(self.recommender.clustered_files), 3)
        self.assertEqual(len(self.recommender.filenames), 4)
        self.assertIsNotNone(self.recommender.embeddings)
    
    def test_initialization_with_missing_files(self):
        """파일 없을 때 초기화 테스트"""
        recommender = CardRecommender(
            cluster_tags_path="nonexistent.json",
            embeddings_path="nonexistent.json",
            clustering_results_path="nonexistent.json"
        )
        
        self.assertEqual(len(recommender.cluster_tags), 0)
        self.assertEqual(len(recommender.clustered_files), 0)
        self.assertIsNone(recommender.embeddings)
    
    def test_recommend_cards_basic(self):
        """기본 카드 추천 테스트"""
        persona = {
            'interesting_topics': ['음식'],
            'preferred_category_types': [1],
            'selection_complexity': 'moderate'
        }
        
        result = self.recommender.recommend_cards(persona, num_cards=2)
        
        self.assertEqual(result['status'], 'success')
        self.assertLessEqual(len(result['cards']), 2)
        self.assertGreater(len(result['cards']), 0)
        self.assertIn(1, result['clusters_used'])
    
    def test_recommend_cards_simple_complexity(self):
        """단순한 복잡도로 카드 추천 테스트"""
        persona = {
            'interesting_topics': ['놀이'],
            'preferred_category_types': [2],
            'selection_complexity': 'simple'
        }
        
        result = self.recommender.recommend_cards(persona, num_cards=4)
        
        self.assertEqual(result['status'], 'success')
        # simple은 최대 2장까지
        self.assertLessEqual(len(result['cards']), 2)
        self.assertGreater(len(result['cards']), 0)
    
    def test_recommend_cards_complex_complexity(self):
        """복잡한 복잡도로 카드 추천 테스트"""
        persona = {
            'interesting_topics': ['감정', '음식'],
            'preferred_category_types': [1, 3],
            'selection_complexity': 'complex'
        }
        
        result = self.recommender.recommend_cards(persona, num_cards=4)
        
        self.assertEqual(result['status'], 'success')
        # complex는 2-4장
        self.assertGreaterEqual(len(result['cards']), 2)
        self.assertLessEqual(len(result['cards']), 4)
    
    def test_recommend_cards_no_preferred_clusters(self):
        """선호 클러스터 없을 때 카드 추천 테스트"""
        persona = {
            'interesting_topics': [],
            'preferred_category_types': [],
            'selection_complexity': 'moderate'
        }
        
        result = self.recommender.recommend_cards(persona, num_cards=2)
        
        self.assertEqual(result['status'], 'success')
        self.assertGreater(len(result['cards']), 0)
        self.assertGreater(len(result['clusters_used']), 0)
    
    def test_recommend_cards_empty_data(self):
        """빈 데이터로 카드 추천 테스트"""
        empty_recommender = CardRecommender()
        
        persona = {
            'interesting_topics': ['음식'],
            'preferred_category_types': [1],
            'selection_complexity': 'moderate'
        }
        
        result = empty_recommender.recommend_cards(persona, num_cards=2)
        
        self.assertEqual(result['status'], 'error')
        self.assertEqual(len(result['cards']), 0)
        self.assertIn('클러스터 태그 또는 클러스터링 데이터가 없습니다', result['message'])
    
    def test_get_cluster_info_success(self):
        """클러스터 정보 조회 성공 테스트"""
        result = self.recommender.get_cluster_info(1)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['cluster_info']['cluster_id'], 1)
        self.assertEqual(result['cluster_info']['num_files'], 2)
        self.assertIn('음식', result['cluster_info']['tags'])
        self.assertIn('food1.png', result['cluster_info']['sample_files'])
    
    def test_get_cluster_info_not_found(self):
        """존재하지 않는 클러스터 정보 조회 테스트"""
        result = self.recommender.get_cluster_info(999)
        
        self.assertEqual(result['status'], 'error')
        self.assertIsNone(result['cluster_info'])
        self.assertIn('클러스터 ID 999 없음', result['message'])
    
    def test_get_all_clusters_info(self):
        """모든 클러스터 정보 조회 테스트"""
        result = self.recommender.get_all_clusters_info()
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['total_count'], 3)
        self.assertEqual(len(result['clusters']), 3)
        
        # 각 클러스터 정보 확인
        cluster_ids = [cluster['cluster_id'] for cluster in result['clusters']]
        self.assertIn(1, cluster_ids)
        self.assertIn(2, cluster_ids)
        self.assertIn(3, cluster_ids)
    
    def test_weighted_choice_functionality(self):
        """가중치 선택 기능 테스트"""
        persona = {
            'interesting_topics': ['음식'],
            'preferred_category_types': [1],
            'selection_complexity': 'moderate'
        }
        
        # 여러 번 추천해서 다양성 확인
        results = []
        for _ in range(5):
            result = self.recommender.recommend_cards(persona, num_cards=1)
            if result['status'] == 'success' and result['cards']:
                results.append(result['cards'][0])
        
        # 최소한 하나의 결과는 있어야 함
        self.assertGreater(len(results), 0)
        
        # 음식 관련 카드가 포함되어야 함
        food_cards = ['food1.png', 'food2.png']
        has_food_card = any(card in food_cards for card in results)
        self.assertTrue(has_food_card)
    
    def test_embeddings_normalization(self):
        """임베딩 정규화 테스트"""
        # 임베딩이 정규화되었는지 확인
        import numpy as np
        
        if self.recommender.embeddings is not None:
            norms = np.linalg.norm(self.recommender.embeddings, axis=1)
            # 정규화된 벡터의 노름은 1에 가까워야 함 (부동소수점 오차 고려)
            for norm in norms:
                self.assertAlmostEqual(norm, 1.0, places=5)
    
    def test_filename_to_idx_mapping(self):
        """파일명-인덱스 매핑 테스트"""
        expected_files = ["food1.png", "food2.png", "play1.png", "happy.png"]
        
        for i, filename in enumerate(expected_files):
            self.assertEqual(self.recommender.filename_to_idx[filename], i)
    
    def test_cluster_id_conversion(self):
        """클러스터 ID 변환 테스트 (문자열 -> 정수)"""
        # cluster_tags와 clustered_files의 키가 정수로 변환되었는지 확인
        for cluster_id in self.recommender.cluster_tags.keys():
            self.assertIsInstance(cluster_id, int)
        
        for cluster_id in self.recommender.clustered_files.keys():
            self.assertIsInstance(cluster_id, int)


if __name__ == '__main__':
    unittest.main()