"""임베딩 최적화 유틸리티

런타임 검색을 위한 임베딩 인덱스 생성 및 최적화
전처리 단계에서 생성된 임베딩을 효율적인 형태로 변환
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def load_embeddings(embeddings_path: str) -> Dict[str, Any]:
    """임베딩 JSON 파일 로드

    Args:
        embeddings_path: embeddings.json 파일 경로

    Returns:
        filenames, image_embeddings, text_embeddings를 포함한 딕셔너리
    """
    with open(embeddings_path, "r", encoding="utf-8") as f:
        return json.load(f)


def fuse_embeddings(
    image_embeddings: np.ndarray,
    text_embeddings: np.ndarray,
    image_weight: float = 0.8,
) -> np.ndarray:
    """이미지와 텍스트 임베딩 융합

    Args:
        image_embeddings: (N, D) 이미지 임베딩 행렬
        text_embeddings: (N, D) 텍스트 임베딩 행렬
        image_weight: 이미지 가중치 (0~1)

    Returns:
        L2 정규화된 융합 임베딩 (N, D)
    """
    fused = image_weight * image_embeddings + (1 - image_weight) * text_embeddings
    norms = np.linalg.norm(fused, axis=1, keepdims=True)
    return fused / np.maximum(norms, 1e-10)


def create_optimized_index(
    embeddings_path: str,
    output_path: str,
    image_weight: float = 0.8,
) -> Dict[str, Any]:
    """최적화된 벡터 인덱스 생성

    JSON 형식의 임베딩을 NumPy 바이너리 형식으로 변환하여
    로딩 시간을 대폭 단축

    Args:
        embeddings_path: 입력 embeddings.json 경로
        output_path: 출력 .npz 파일 경로
        image_weight: 이미지-텍스트 융합 가중치

    Returns:
        생성된 인덱스 통계 정보
    """
    data = load_embeddings(embeddings_path)

    filenames = data["filenames"]
    img_emb = np.array(data["image_embeddings"], dtype=np.float32)
    txt_emb = np.array(data["text_embeddings"], dtype=np.float32)

    # 융합 및 정규화
    fused = fuse_embeddings(img_emb, txt_emb, image_weight)

    # 바이너리 형식 저장
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        output_path,
        filenames=np.array(filenames, dtype=object),
        embeddings=fused,
    )

    file_size_mb = output_path.stat().st_size / (1024 * 1024)

    return {
        "num_embeddings": len(filenames),
        "embedding_dim": fused.shape[1],
        "file_size_mb": round(file_size_mb, 2),
        "output_path": str(output_path),
    }


def compute_cluster_centroids(
    embeddings_path: str,
    clustering_path: str,
    output_path: str,
    image_weight: float = 0.8,
) -> Dict[int, List[float]]:
    """클러스터 중심 임베딩 계산

    각 클러스터의 중심 벡터를 계산하여
    클러스터 수준의 유사도 검색에 활용

    Args:
        embeddings_path: embeddings.json 경로
        clustering_path: clustering_results.json 경로
        output_path: 출력 JSON 경로
        image_weight: 이미지-텍스트 융합 가중치

    Returns:
        클러스터 ID → 중심 임베딩 매핑
    """
    # 임베딩 로드
    emb_data = load_embeddings(embeddings_path)
    filenames = emb_data["filenames"]
    img_emb = np.array(emb_data["image_embeddings"], dtype=np.float32)
    txt_emb = np.array(emb_data["text_embeddings"], dtype=np.float32)
    fused = fuse_embeddings(img_emb, txt_emb, image_weight)

    # 클러스터링 결과 로드
    with open(clustering_path, "r", encoding="utf-8") as f:
        cluster_data = json.load(f)

    # 파일명 → 인덱스 매핑
    filename_to_idx = {fn: i for i, fn in enumerate(filenames)}

    # 클러스터별 중심 계산
    centroids: Dict[int, List[float]] = {}

    for cluster_id_str, cluster_files in cluster_data.get("clustered_files", {}).items():
        cluster_id = int(cluster_id_str)
        indices = [filename_to_idx[fn] for fn in cluster_files if fn in filename_to_idx]

        if indices:
            cluster_embeddings = fused[indices]
            centroid = np.mean(cluster_embeddings, axis=0)
            centroid = centroid / (np.linalg.norm(centroid) + 1e-10)
            centroids[cluster_id] = centroid.tolist()

    # 저장
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(centroids, f, ensure_ascii=False, indent=2)

    return centroids


def validate_embeddings(embeddings_path: str) -> Dict[str, Any]:
    """임베딩 파일 유효성 검증

    Args:
        embeddings_path: embeddings.json 경로

    Returns:
        검증 결과 및 통계
    """
    data = load_embeddings(embeddings_path)

    filenames = data.get("filenames", [])
    img_emb = data.get("image_embeddings", [])
    txt_emb = data.get("text_embeddings", [])

    issues: List[str] = []

    # 기본 검증
    if not filenames:
        issues.append("No filenames found")
    if not img_emb:
        issues.append("No image embeddings found")
    if not txt_emb:
        issues.append("No text embeddings found")

    # 크기 일관성 검증
    if len(filenames) != len(img_emb):
        issues.append(f"Filename count ({len(filenames)}) != image embedding count ({len(img_emb)})")
    if len(filenames) != len(txt_emb):
        issues.append(f"Filename count ({len(filenames)}) != text embedding count ({len(txt_emb)})")

    # 차원 검증
    if img_emb and len(img_emb[0]) != 768:
        issues.append(f"Unexpected image embedding dimension: {len(img_emb[0])} (expected 768)")
    if txt_emb and len(txt_emb[0]) != 768:
        issues.append(f"Unexpected text embedding dimension: {len(txt_emb[0])} (expected 768)")

    # 정규화 검증 (샘플)
    if img_emb:
        sample_norm = np.linalg.norm(np.array(img_emb[0]))
        if not (0.99 < sample_norm < 1.01):
            issues.append(f"Image embeddings may not be normalized (sample norm: {sample_norm:.4f})")

    return {
        "valid": len(issues) == 0,
        "num_embeddings": len(filenames),
        "embedding_dim": len(img_emb[0]) if img_emb else 0,
        "issues": issues,
    }


def get_similar_cards(
    query_embedding: np.ndarray,
    embeddings: np.ndarray,
    filenames: List[str],
    top_k: int = 20,
    excluded: Optional[set] = None,
) -> List[Tuple[str, float]]:
    """쿼리 임베딩과 유사한 카드 검색

    Args:
        query_embedding: 쿼리 벡터 (1D, 정규화됨)
        embeddings: 전체 임베딩 행렬 (N, D, 정규화됨)
        filenames: 파일명 목록
        top_k: 반환할 결과 수
        excluded: 제외할 파일명 집합

    Returns:
        (파일명, 유사도) 튜플 목록
    """
    excluded = excluded or set()

    # 코사인 유사도 계산
    similarities = embeddings @ query_embedding

    # 제외 처리
    for i, fn in enumerate(filenames):
        if fn in excluded:
            similarities[i] = -np.inf

    # top-k 선택
    top_indices = np.argsort(similarities)[::-1][:top_k]

    return [
        (filenames[idx], float(similarities[idx]))
        for idx in top_indices
        if similarities[idx] > -np.inf
    ]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Embedding utilities")
    parser.add_argument("command", choices=["validate", "optimize", "centroids"])
    parser.add_argument("--embeddings", default="./dataset/processed/embeddings.json")
    parser.add_argument("--clustering", default="./dataset/processed/clustering_results.json")
    parser.add_argument("--output", default="./dataset/processed/optimized_index.npz")
    parser.add_argument("--image-weight", type=float, default=0.8)

    args = parser.parse_args()

    if args.command == "validate":
        result = validate_embeddings(args.embeddings)
        print(f"Valid: {result['valid']}")
        print(f"Embeddings: {result['num_embeddings']}")
        if result["issues"]:
            print("Issues:")
            for issue in result["issues"]:
                print(f"  - {issue}")

    elif args.command == "optimize":
        result = create_optimized_index(
            args.embeddings, args.output, args.image_weight
        )
        print(f"Created optimized index: {result['output_path']}")
        print(f"Size: {result['file_size_mb']} MB")

    elif args.command == "centroids":
        centroids = compute_cluster_centroids(
            args.embeddings,
            args.clustering,
            args.output.replace(".npz", "_centroids.json"),
            args.image_weight,
        )
        print(f"Computed {len(centroids)} cluster centroids")
