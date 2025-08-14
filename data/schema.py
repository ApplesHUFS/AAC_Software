import json
from pathlib import Path
from typing import List, Dict, Any


class DatasetSchema:
    @staticmethod
    def create_empty_entry(data_id: int, persona: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": data_id,
            "input": {
                "persona": persona,
                "context": {
                    "time": None,
                    "place": "",
                    "interaction_partner": "",
                    "current_activity": ""
                },
                "past_interpretation": "",
                "AAC_card_combination": []
            },
            "output": ""
        }

    @staticmethod
    def generate_dataset(persona_json_path: str = None, output_path: str = "", samples_per_persona: int = 200) -> int:
        with open(persona_json_path, 'r', encoding='utf-8') as f:
            personas_data = json.load(f)
            personas = [item for item in personas_data]

        dataset: List[Dict[str, Any]] = []
        data_id = 1

        for persona_item in personas:
            persona = persona_item if 'persona' in persona_item else persona_item
            for _ in range(samples_per_persona):
                entry = DatasetSchema.create_empty_entry(data_id, persona)
                dataset.append(entry)
                data_id += 1

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)

        total_samples = len(dataset)
        return total_samples
