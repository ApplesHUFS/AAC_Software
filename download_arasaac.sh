#!/bin/bash

# 고속 한국어 ARASAAC 픽토그램 다운로더
# 병렬 처리를 통한 빠른 다운로드

set -euo pipefail

# 전역 변수 설정
readonly BASE_URL="https://api.arasaac.org/v1"
readonly STATIC_URL="https://static.arasaac.org/pictograms"
readonly LANGUAGE="ko"
readonly BASE_DIR="./dataset"

# 디렉토리 경로
readonly IMAGES_DIR="${BASE_DIR}/images"
readonly METADATA_DIR="${BASE_DIR}/metadata"
readonly LOGS_DIR="${BASE_DIR}/logs"

# 시스템 리소스 기반 최적 병렬 처리 수 계산
readonly MAX_WORKERS=$(($(nproc) * 2))

# 통계 변수
SUCCESS_COUNT=0
FAILED_COUNT=0
TOTAL_SIZE=0

# 로그 파일 설정
readonly TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
readonly LOG_FILE="${LOGS_DIR}/download_log_${TIMESTAMP}.txt"

# 초기화 함수
init_directories() {
    mkdir -p "$IMAGES_DIR" "$METADATA_DIR" "$LOGS_DIR"
    
    echo "고속 다운로더 초기화 완료" >&2
    echo "다운로드 디렉토리: $(realpath "$BASE_DIR")" >&2
    echo "동시 처리 프로세스: ${MAX_WORKERS}개" >&2
}

# 로그 기록 함수
log_message() {
    local message="$1"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[${timestamp}] ${message}" | tee -a "$LOG_FILE"
}

# API에서 픽토그램 메타데이터 가져오기
fetch_pictogram_metadata() {
    local api_url="${BASE_URL}/pictograms/all/${LANGUAGE}"
    local metadata_file="${METADATA_DIR}/pictograms_metadata_${TIMESTAMP}.json"
    
    echo "한국어 픽토그램 메타데이터 요청 중..." >&2
    
    if curl -s --max-time 30 --retry 3 "$api_url" > "$metadata_file"; then
        local count=$(jq length "$metadata_file")
        echo "총 ${count}개의 한국어 픽토그램 발견" >&2
        echo "$metadata_file"
    else
        echo "API 요청 실패" >&2
        exit 1
    fi
}

# 단일 픽토그램 다운로드 함수
download_pictogram() {
    local pictogram_id="$1"
    local korean_keyword="$2"
    
    # 파일명 생성 (한국어 키워드 포함)
    local filename="${pictogram_id}.png"
    if [[ -n "$korean_keyword" ]]; then
        # 파일명에서 문제가 될 수 있는 문자 제거
        local safe_keyword=$(echo "$korean_keyword" | tr '/' '_' | tr '\\' '_' | cut -c1-15)
        if [[ -n "$safe_keyword" ]]; then
            filename="${pictogram_id}_${safe_keyword}.png"
        fi
    fi
    
    local filepath="${IMAGES_DIR}/${filename}"
    local image_url="${STATIC_URL}/${pictogram_id}/${pictogram_id}.png"
    
    # 이미 존재하는 파일 건너뛰기
    if [[ -f "$filepath" ]]; then
        return 0
    fi
    
    # 이미지 다운로드
    if curl -s --max-time 10 --retry 2 -o "$filepath" "$image_url"; then
        # 다운로드 성공 시 파일 크기 확인
        if [[ -s "$filepath" ]]; then
            local file_size=$(stat -c%s "$filepath")
            echo "SUCCESS,$pictogram_id,$filename,$file_size"
            return 0
        else
            rm -f "$filepath"
        fi
    fi
    
    echo "FAILED,$pictogram_id,download_error,0"
    return 1
}

# 픽토그램 목록을 CSV로 변환
generate_pictogram_list() {
    local metadata_file="$1"
    local temp_list="${METADATA_DIR}/pictogram_list_${TIMESTAMP}.txt"
    
    echo "다운로드 목록 생성 중..." >&2
    
    jq -r '.[] | 
        "\(._id)," + 
        ((.keywords // []) | 
         map(select(.keyword != null and .keyword != "")) | 
         map(.keyword) | 
         first // ""
        )' "$metadata_file" > "$temp_list"
    
    echo "$temp_list"
}

# 병렬 다운로드 실행
execute_parallel_download() {
    local pictogram_list="$1"
    local total_count=$(wc -l < "$pictogram_list")
    
    echo "다운로드 대상: ${total_count}개" >&2
    echo "병렬 처리 시작..." >&2
    
    local start_time=$(date +%s)
    local results_file="${LOGS_DIR}/download_results_${TIMESTAMP}.txt"
    local counter_file="${LOGS_DIR}/counter_${TIMESTAMP}.txt"
    
    # 카운터 파일 초기화
    echo "0" > "$counter_file"
    
    # 진행바 프로세스 시작
    {
        local last_count=0
        while [[ $last_count -lt $total_count ]]; do
            if [[ -f "$results_file" ]]; then
                local current_count=$(wc -l < "$results_file" 2>/dev/null || echo "0")
                if [[ $current_count -gt $last_count ]]; then
                    local success=$(grep -c "^SUCCESS," "$results_file" 2>/dev/null || echo "0")
                    local failed=$(grep -c "^FAILED," "$results_file" 2>/dev/null || echo "0")
                    local percent=$((current_count * 100 / total_count))
                    local filled=$((percent / 2))
                    local empty=$((50 - filled))
                    
                    printf "\r["
                    printf "%*s" $filled | tr ' ' '='
                    printf "%*s" $empty | tr ' ' '-'
                    printf "] %d%% (%d/%d) 성공:%d 실패:%d" \
                           $percent $current_count $total_count $success $failed
                    
                    last_count=$current_count
                fi
            fi
            sleep 0.1
        done
        echo "" >&2
        rm -f "$counter_file"
    } &
    
    local progress_pid=$!
    
    # 병렬 다운로드 실행
    export -f download_pictogram
    export STATIC_URL IMAGES_DIR
    
    while IFS=',' read -r pictogram_id korean_keyword; do
        echo "$pictogram_id,$korean_keyword"
    done < "$pictogram_list" | \
    xargs -P "$MAX_WORKERS" -I {} bash -c '
        IFS="," read -r id keyword <<< "{}"
        download_pictogram "$id" "$keyword"
    ' >> "$results_file"
    
    # 진행바 프로세스 종료 대기
    wait $progress_pid
    
    local end_time=$(date +%s)
    local total_time=$((end_time - start_time))
    
    # 결과 집계
    SUCCESS_COUNT=$(grep -c "^SUCCESS," "$results_file")
    FAILED_COUNT=$(grep -c "^FAILED," "$results_file")
    
    # 총 다운로드 크기 계산
    if (( SUCCESS_COUNT > 0 )); then
        TOTAL_SIZE=$(grep "^SUCCESS," "$results_file" | cut -d',' -f4 | paste -sd+ - | bc)
    fi
    
    # 결과 출력
    print_results "$SUCCESS_COUNT" "$FAILED_COUNT" "$total_time" "$TOTAL_SIZE"
    
    echo "$results_file"
}

# 연구용 CSV 파일 생성
create_research_csv() {
    local metadata_file="$1"
    local results_file="$2"
    local csv_file="${METADATA_DIR}/pictograms_research_${TIMESTAMP}.csv"
    
    echo "연구용 CSV 파일 생성 중..." >&2
    
    # CSV 헤더 작성
    cat > "$csv_file" << 'EOF'
id,korean_keywords,categories,aac_suitable,color_available,has_skin_option,has_hair_option,created_date,last_updated,image_filename,download_success
EOF
    
    # 성공한 다운로드 목록 생성
    local success_ids="[]"
    if [[ -f "$results_file" ]]; then
        success_ids=$(grep "^SUCCESS," "$results_file" | cut -d',' -f2 | sort | jq -R . | jq -s .)
    fi
    
    # JSON 데이터를 CSV로 변환
    jq -r --argjson success_list "$success_ids" '
        .[] | 
        [
            ._id,
            ((.keywords // []) | map(.keyword // "") | join("; ")),
            ((.categories // []) | map(tostring) | join("; ")),
            (.aac // false),
            (.aacColor // false),
            (.skin // false),
            (.hair // false),
            (.created // ""),
            (.lastUpdated // ""),
            (._id + ".png"),
            (._id as $id | $success_list | index($id) != null)
        ] | @csv
    ' "$metadata_file" >> "$csv_file"
    
    echo "CSV 파일 생성 완료: $(basename "$csv_file")" >&2
}

# 실패 목록 저장
save_failed_list() {
    local results_file="$1"
    local failed_file="${LOGS_DIR}/failed_downloads_${TIMESTAMP}.txt"
    
    if (( FAILED_COUNT > 0 )); then
        grep "^FAILED," "$results_file" | cut -d',' -f2 > "$failed_file"
        echo "실패 목록 저장: $(basename "$failed_file")" >&2
    fi
}

# 최종 결과 출력
print_results() {
    local success="$1"
    local failed="$2" 
    local time="$3"
    local total_size="$4"
    
    local total=$((success + failed))
    local success_rate=0
    
    if (( total > 0 )); then
        success_rate=$(echo "scale=1; $success * 100 / $total" | bc)
    fi
    
    echo ""
    echo "=================================================="
    echo "다운로드 완료!"
    echo "=================================================="
    echo "성공: ${success}개"
    echo "실패: ${failed}개"
    echo "성공률: ${success_rate}%"
    echo "총 소요시간: ${time}초"
    
    if (( success > 0 && time > 0 )); then
        local speed=$(echo "scale=1; $success / $time" | bc)
        echo "평균 속도: ${speed}개/초"
        
        if (( total_size > 0 )); then
            local size_mb=$(echo "scale=1; $total_size / 1024 / 1024" | bc)
            local speed_mb=$(echo "scale=1; $size_mb / $time" | bc)
            echo "총 다운로드 크기: ${size_mb} MB"
            echo "평균 다운로드 속도: ${speed_mb} MB/초"
        fi
    fi
    
    echo "저장 위치: $(realpath "$BASE_DIR")"
    echo "=================================================="
}

# 메인 실행 함수
main() {
    echo "한국어 ARASAAC 픽토그램 다운로더 시작" >&2
    
    # 필수 도구 확인
    for tool in curl jq bc; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            echo "필수 도구 '$tool'이 설치되어 있지 않습니다." >&2
            exit 1
        fi
    done
    
    # 초기화
    init_directories
    
    # 메타데이터 가져오기
    local metadata_file
    metadata_file=$(fetch_pictogram_metadata)
    
    # 픽토그램 목록 생성
    local pictogram_list
    pictogram_list=$(generate_pictogram_list "$metadata_file")
    
    # 병렬 다운로드 실행
    local results_file
    results_file=$(execute_parallel_download "$pictogram_list")
    
    # 연구용 CSV 생성
    create_research_csv "$metadata_file" "$results_file"
    
    # 실패 목록 저장
    save_failed_list "$results_file"
    
    # 임시 파일 정리
    rm -f "$pictogram_list"
    
    log_message "다운로드 작업 완료"
}

# 인터럽트 핸들러
cleanup() {
    echo "" >&2
    echo "사용자에 의해 중단되었습니다." >&2
    echo "지금까지의 파일은 $BASE_DIR에 저장되어 있습니다." >&2
    exit 130
}

trap cleanup SIGINT SIGTERM

# 메인 함수 실행
main "$@"