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
    def generate_dataset(persona_json_path: str, output_path: str, samples_per_persona: int = 200) -> int:
        with open(persona_json_path, 'r', encoding='utf-8') as f:
            personas: List[Dict[str, Any]] = json.load(f)

        dataset: List[Dict[str, Any]] = []
        data_id = 1

        for persona in personas:
            for _ in range(samples_per_persona):
                entry = DatasetSchema.create_empty_entry(data_id, persona["persona"])
                dataset.append(entry)
                data_id += 1

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)

        total_samples = len(dataset)
        print(f"Generated {total_samples} samples ({len(personas)} personas × {samples_per_persona} samples)")
        return total_samples
