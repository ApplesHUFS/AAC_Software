#!/bin/bash

# 한국어 ARASAAC 픽토그램 다운로더
# dataset/images에 이미지 파일들을 병렬 다운로드

set -e

# 설정
API_URL="https://api.arasaac.org/v1/pictograms/all/ko"
STATIC_URL="https://static.arasaac.org/pictograms"
OUTPUT_DIR="dataset/images"
MAX_PARALLEL=20
TEMP_DIR=$(mktemp -d)

# 필수 도구 확인
check_dependencies() {
    local missing=""
    
    command -v curl >/dev/null 2>&1 || missing="$missing curl"
    command -v jq >/dev/null 2>&1 || missing="$missing jq"
    command -v parallel >/dev/null 2>&1 || missing="$missing parallel"
    
    if [ -n "$missing" ]; then
        echo "오류: 다음 도구들이 필요합니다:$missing"
        echo "Ubuntu/Debian: sudo apt-get install curl jq parallel"
        echo "macOS: brew install curl jq parallel"
        exit 1
    fi
}

# 디렉토리 생성
setup_directories() {
    mkdir -p "$OUTPUT_DIR"
    echo "출력 디렉토리: $OUTPUT_DIR"
}

# 픽토그램 메타데이터 가져오기
fetch_metadata() {
    echo "한국어 픽토그램 메타데이터 요청 중..."
    
    curl -s --fail --connect-timeout 30 --max-time 60 "$API_URL" > "$TEMP_DIR/metadata.json"
    
    if [ ! -s "$TEMP_DIR/metadata.json" ]; then
        echo "오류: 메타데이터를 가져올 수 없습니다."
        exit 1
    fi
    
    local count
    count=$(jq length "$TEMP_DIR/metadata.json")
    echo "총 $count개의 픽토그램 발견"
}

# 단일 이미지 다운로드 함수
download_image() {
    local id="$1"
    local image_url="$STATIC_URL/$id/$id.png"
    local output_file="$OUTPUT_DIR/$id.png"
    
    # 이미 존재하면 스킵
    if [ -f "$output_file" ]; then
        return 0
    fi
    
    # 이미지 다운로드
    if curl -s --fail --connect-timeout 10 --max-time 30 "$image_url" -o "$output_file" 2>/dev/null; then
        return 0
    else
        # 실패한 파일 제거
        [ -f "$output_file" ] && rm -f "$output_file"
        return 1
    fi
}

# 이미지 ID 목록 추출 및 다운로드
download_all_images() {
    echo "이미지 ID 추출 중..."
    
    # JSON에서 _id 필드만 추출하여 임시 파일에 저장
    jq -r '.[].id // .[].["_id"] // empty' "$TEMP_DIR/metadata.json" > "$TEMP_DIR/ids.txt"
    
    local total_count
    total_count=$(wc -l < "$TEMP_DIR/ids.txt")
    
    if [ "$total_count" -eq 0 ]; then
        echo "오류: 유효한 픽토그램 ID를 찾을 수 없습니다."
        exit 1
    fi
    
    echo "$total_count개 이미지 병렬 다운로드 시작 (동시 처리: $MAX_PARALLEL개)"
    
    # export 함수를 parallel에서 사용할 수 있도록
    export -f download_image
    export STATIC_URL OUTPUT_DIR
    
    # parallel을 사용해서 병렬 다운로드
    parallel -j "$MAX_PARALLEL" --progress download_image {} < "$TEMP_DIR/ids.txt"
    
    # 결과 확인
    local success_count
    success_count=$(find "$OUTPUT_DIR" -name "*.png" | wc -l)
    
    echo "다운로드 완료: $success_count/$total_count 성공"
    
    if [ "$success_count" -eq 0 ]; then
        echo "경고: 다운로드된 이미지가 없습니다."
    fi
}

# 정리
cleanup() {
    rm -rf "$TEMP_DIR"
}

# 메인 실행
main() {
    echo "ARASAAC 한국어 픽토그램 다운로더 시작"
    
    check_dependencies
    setup_directories
    
    # 정리 함수 등록
    trap cleanup EXIT
    
    fetch_metadata
    download_all_images
    
    echo "모든 작업이 완료되었습니다."
    echo "이미지 저장 위치: $(realpath "$OUTPUT_DIR")"
}

main "$@"