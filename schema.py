import json

def generate_aac_dataset(persona_json_path, output_path, samples_per_persona=200):
    with open(persona_json_path, 'r', encoding='utf-8') as f:
        personas = json.load(f)
    
    dataset = []
    data_id = 1
    
    for persona in personas:
        for _ in range(samples_per_persona):
            data_entry = {
                "id": data_id,
                "input": {
                    "persona": persona["persona"],
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
            dataset.append(data_entry)
            data_id += 1
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
if __name__ == "__main__":
    generate_aac_dataset(
        persona_json_path="data/persona.json",
        output_path="data/aac_dataset.json",
        samples_per_persona=200
    )
    print("done")