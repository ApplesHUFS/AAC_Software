import json
import os
import base64
import time
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm


class DatasetGenerator:
    def __init__(self, dataset_path: str, images_folder: str, output_path: Optional[str] = None, config: Optional[Dict] = None):
        load_dotenv()

        self.dataset_path = dataset_path
        self.images_folder = Path(images_folder)
        self.output_path = output_path or dataset_path.replace('.json', '_completed.json')

        self.config = config or {}
        self.overwrite_mode = self.config.get('overwrite_mode', False)
        self.model = self.config.get('openai_model', 'gpt-4o-2024-08-06')
        self.temperature = self.config.get('openai_temperature', 0.8)
        self.context_max_tokens = self.config.get('context_max_tokens', 300)
        self.interpretation_max_tokens = self.config.get('interpretation_max_tokens', 400)
        self.request_delay = self.config.get('request_delay', 1)

        self.client = OpenAI()

        with open(dataset_path, 'r', encoding='utf-8') as f:
            self.dataset = json.load(f)

        print(f"Dataset loaded: {len(self.dataset)} samples")

    def _encode_image(self, image_path: Path) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _prepare_image_content(self, card_combinations: List[str]) -> List[Dict[str, Any]]:
        content = []

        for i, card_filename in enumerate(card_combinations, 1):
            image_path = self.images_folder / card_filename

            if not image_path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")

            base64_image = self._encode_image(image_path)

            content.extend([
                {
                    "type": "text",
                    "text": f"\n카드 {i}:"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}",
                        "detail": "high"
                    }
                }
            ])

        return content

    def _clean_interpretations(self, interpretations: List[str]) -> List[str]:
        cleaned = []
        patterns = [
            r'^첫\s*번째\s*해석:\s*',
            r'^두\s*번째\s*해석:\s*',
            r'^세\s*번째\s*해석:\s*',
            r'^\d+\.\s*',
            r'^-\s*'
        ]

        for interpretation in interpretations:
            cleaned_text = interpretation.strip()
            for pattern in patterns:
                cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
            cleaned_text = cleaned_text.strip()
            if cleaned_text:
                cleaned.append(cleaned_text)

        return cleaned

    def _is_context_complete(self, context: Dict[str, Any]) -> bool:
        if not context:
            return False

        required_fields = ['time', 'place', 'interaction_partner', 'current_activity']
        for field in required_fields:
            value = context.get(field)
            if not value or value in [None, "", "오류"]:
                return False

        return True

    def _is_output_complete(self, output: Any) -> bool:
        if not output:
            return False

        if isinstance(output, str):
            return output not in ["", "Processing error"]

        if isinstance(output, list):
            if not output or output == ["Processing error"]:
                return False
            return len(output) >= 3 and all(isinstance(item, str) and item.strip() for item in output)

        return False

    def _should_process_item(self, item: Dict[str, Any]) -> bool:
        if self.overwrite_mode:
            return True

        context_complete = self._is_context_complete(item['input']['context'])
        output_complete = self._is_output_complete(item.get('output'))

        return not (context_complete and output_complete)

    def _generate_context(self, persona: Dict[str, Any], card_combination: List[str]) -> Optional[Dict[str, str]]:
        system_prompt = """당신은 AAC(보완대체의사소통) 전문가입니다.
제공된 AAC 카드 이미지들을 보고, 페르소나 정보와 함께 이 상황이 일어날 수 있는 현실적인 맥락(context)을 생성해주세요.

이미지를 직접 보고 판단하여, 자연스럽게 연결되는 일상적인 상황을 만들어주세요."""

        image_content = self._prepare_image_content(card_combination)

        user_content = [{
            "type": "text",
            "text": f"""페르소나:
- 나이: {persona['age']}
- 성별: {persona['gender']}
- 장애 유형: {persona['disability_type']}
- 의사소통 특성: {persona['communication_characteristics']}

위 페르소나가 제공된 AAC 카드 이미지들을 사용하는 상황을 상상해주세요."""
        }]

        user_content.extend(image_content)
        user_content.append({
            "type": "text",
            "text": """
위 이미지들을 보고 다음 형식의 JSON으로 context를 생성해주세요:

실제 일어날 법한 자연스러운 상황으로 만들어주세요."""
        })

        context_schema = {
            "type": "json_schema",
            "json_schema": {
                "name": "context_generation",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "time": {
                            "type": "string",
                            "description": "오전/오후 X시 형식 또는 아침/점심/저녁 등"
                        },
                        "place": {
                            "type": "string",
                            "description": "구체적인 장소"
                        },
                        "interaction_partner": {
                            "type": "string",
                            "description": "대화 상대"
                        },
                        "current_activity": {
                            "type": "string",
                            "description": "현재 하고 있는 활동이나 상황"
                        }
                    },
                    "required": ["time", "place", "interaction_partner", "current_activity"],
                    "additionalProperties": False
                }
            }
        }

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format=context_schema,
                temperature=self.temperature,
                max_tokens=self.context_max_tokens
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"Error generating context: {e}")
            return None

    def _generate_interpretations(self, persona: Dict[str, Any], context: Dict[str, str],
                                card_combination: List[str]) -> Optional[List[str]]:
        system_prompt = """당신은 AAC(보완대체의사소통) 해석 전문가입니다.
제공된 AAC 카드 이미지들을 직접 보고, 주어진 페르소나와 상황(context)을 고려하여 3가지 해석을 생성해주세요.

해석 원칙:
1. 첫 번째 해석: 이미지 순서와 내용을 보고 가장 가능성이 높고 직관적인 해석
2. 두 번째 해석: 같은 이미지들을 다른 관점에서 해석
3. 세 번째 해석: 창의적이면서도 맥락상 가능한 해석

각 해석은 자연스러운 한국어 문장으로 작성하되, 사용자의 의도를 명확히 전달해야 합니다.
이미지의 시각적 요소와 순서를 중요하게 고려하세요.
해석 앞에 '첫 번째 해석:', '두 번째 해석:' 등의 접두사는 붙이지 마세요."""

        image_content = self._prepare_image_content(card_combination)

        user_content = [{
            "type": "text",
            "text": f"""페르소나:
- 나이: {persona['age']}
- 성별: {persona['gender']}
- 장애 유형: {persona['disability_type']}
- 의사소통 특성: {persona['communication_characteristics']}

상황(Context):
- 시간: {context['time']}
- 장소: {context['place']}
- 대화 상대: {context['interaction_partner']}
- 현재 활동: {context['current_activity']}

아래 AAC 카드 이미지들을 순서대로 보고 해석해주세요:"""
        }]

        user_content.extend(image_content)
        user_content.append({
            "type": "text",
            "text": """
위 이미지들을 보고 이 사람이 전달하고자 하는 메시지를 3가지로 해석해주세요.
이미지의 시각적 내용과 순서를 반드시 고려하세요.
각 해석은 접두사 없이 바로 내용으로 시작하세요."""
        })

        interpretations_schema = {
            "type": "json_schema",
            "json_schema": {
                "name": "interpretations_generation",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "interpretations": {
                            "type": "array",
                            "description": "3가지 해석 후보",
                            "items": {
                                "type": "string",
                                "description": "개별 해석"
                            },
                            "minItems": 3,
                            "maxItems": 3
                        }
                    },
                    "required": ["interpretations"],
                    "additionalProperties": False
                }
            }
        }

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format=interpretations_schema,
                temperature=0.9,
                max_tokens=self.interpretation_max_tokens
            )

            result = json.loads(response.choices[0].message.content)
            raw_interpretations = result.get("interpretations", [])

            return self._clean_interpretations(raw_interpretations)

        except Exception as e:
            print(f"Error generating interpretations: {e}")
            return None

    def _validate_cards(self, card_combination: List[str]) -> None:
        for card in card_combination:
            image_path = self.images_folder / card
            if not image_path.exists():
                raise FileNotFoundError(f"Image not found: {card}")

    def process_dataset(self, start_idx: int = 0, end_idx: Optional[int] = None,
                       save_interval: int = 10) -> None:
        if end_idx is None:
            end_idx = len(self.dataset)

        save_interval = self.config.get('save_interval', save_interval)

        print(f"Processing samples {start_idx} to {end_idx-1} ({end_idx-start_idx} samples)")
        print(f"Overwrite mode: {self.overwrite_mode}")

        processed_count = 0
        error_count = 0
        skipped_count = 0

        for idx in tqdm(range(start_idx, end_idx), desc="Processing dataset"):
            item = self.dataset[idx]

            if not self._should_process_item(item):
                skipped_count += 1
                continue

            try:
                persona = item['input']['persona']
                card_combination = item['input']['AAC_card_combination']

                self._validate_cards(card_combination)

                if self.overwrite_mode or not self._is_context_complete(item['input']['context']):
                    context = self._generate_context(persona, card_combination)
                    if context:
                        item['input']['context'] = context
                else:
                    context = item['input']['context']

                if context and (self.overwrite_mode or not self._is_output_complete(item.get('output'))):
                    interpretations = self._generate_interpretations(persona, context, card_combination)
                    if interpretations:
                        item['output'] = interpretations

                processed_count += 1

                if processed_count % save_interval == 0:
                    self._save_dataset(f"{self.output_path}.tmp")
                    print(f"\nIntermediate save: {processed_count} processed, {error_count} errors, {skipped_count} skipped")

            except Exception as e:
                print(f"\nError processing sample {idx}: {e}")
                error_count += 1
                if self.config.get('enable_error_recovery', True):
                    item['input']['context'] = {
                        "time": "오류",
                        "place": "오류",
                        "interaction_partner": "오류",
                        "current_activity": "오류"
                    }
                    item['output'] = ["Processing error"]

            time.sleep(self.request_delay)

        self._save_dataset(self.output_path)
        print(f"\nProcessing complete!")
        print(f"Success: {processed_count}, Errors: {error_count}, Skipped: {skipped_count}")
        print(f"Results saved to: {self.output_path}")

    def _save_dataset(self, path: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.dataset, f, ensure_ascii=False, indent=2)

    def print_sample(self, idx: int = 0) -> None:
        if idx >= len(self.dataset):
            print(f"Index {idx} out of range")
            return

        item = self.dataset[idx]
        print(f"\n=== Sample {idx} ===")
        print(f"Persona: {item['input']['persona']['age']} {item['input']['persona']['gender']}")
        print(f"Disability: {item['input']['persona']['disability_type']}")

        print(f"\nCard combination:")
        for card in item['input']['AAC_card_combination']:
            print(f"  - {card}")
            image_path = self.images_folder / card
            status = "✓" if image_path.exists() else "✗"
            print(f"    {status} Image status")

        print(f"\nContext:")
        print(json.dumps(item['input']['context'], ensure_ascii=False, indent=2))

        print(f"\nInterpretations:")
        if item.get('output'):
            for i, interp in enumerate(item['output'], 1):
                print(f"  {i}. {interp}")

        print(f"\nProcessing status:")
        print(f"  Context complete: {self._is_context_complete(item['input']['context'])}")
        print(f"  Output complete: {self._is_output_complete(item.get('output'))}")
        print(f"  Should process: {self._should_process_item(item)}")
