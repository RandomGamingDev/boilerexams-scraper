import os
import json
import string
from pathlib import Path
from datasets import Dataset

def build_dataset(data_dir: str = "./boilerexam-questions", output_dir: str = "./boilerexams-hf-dataset"):
    base_path = Path(data_dir)
    image_dir = base_path / "resources" / "IMAGE"
    
    if not base_path.exists():
        print(f"Error: Directory {data_dir} not found.")
        return

    processed_question_ids = set()
    dataset_records = []
    
    # Letters: A, B, C, D, etc.
    letters = list(string.ascii_uppercase)

    # Recursively find all question JSON files
    for question_file in base_path.rglob("question-*.json"):
        with open(question_file, 'r', encoding='utf-8') as f:
            q_data = json.load(f)
            
        q_id = q_data.get("id")
        
        # Prevent duplicates
        if q_id in processed_question_ids:
            continue
        processed_question_ids.add(q_id)

        # Extract Question Text
        question_body = q_data.get("data", {}).get("body", "").strip()
        if not question_body:
            continue

        choices = q_data.get("data", {}).get("answerChoices", [])
        solution_indices = q_data.get("data", {}).get("solution", [])
        
        formatted_choices = []
        correct_answer = ""
        
        # Format Multiple Choice Options (if they exist)
        if choices:
            # Sort choices by their index just in case the API returns them out of order
            # Safely handle if 'index' is a string or missing
            def safe_int(val, default=999):
                try:
                    return int(val)
                except (ValueError, TypeError):
                    return default

            choices = sorted(choices, key=lambda x: safe_int(x.get("index")))
            
            for choice in choices:
                idx = safe_int(choice.get("index"))
                # Failsafe in case there are more choices than letters or a weird index
                letter = letters[idx] if 0 <= idx < len(letters) else str(choice.get("index", "?"))
                choice_text = choice.get("body", "").strip()
                formatted_choices.append(f"{letter}) {choice_text}")
                
            # Map the solution indices to their corresponding letters securely
            if solution_indices:
                correct_letters = []
                for sol in solution_indices:
                    sol_idx = safe_int(sol, default=-1)
                    if 0 <= sol_idx < len(letters):
                        correct_letters.append(letters[sol_idx])
                    else:
                        # If it's a weird string that couldn't be parsed, just keep it as is
                        correct_letters.append(str(sol))
                        
                correct_answer = ",".join(correct_letters)
                
            full_prompt_text = f"{question_body}\n\nChoices:\n" + "\n".join(formatted_choices)
        else:
            # Handle open-ended or miscategorized questions
            full_prompt_text = question_body
            # correct_answer remains "" so Gemini can fill it in later
            
        # Gather associated images
        images = []
        for resource in q_data.get("resources", []):
            if resource.get("type") == "IMAGE":
                img_key = resource.get("data", {}).get("key")
                img_path = image_dir / f"{img_key}.png"
                if img_path.exists():
                    images.append(str(img_path.absolute()))
                    
        # Format exactly for the GRPO Trainer setup
        record = {
            "id": q_id,
            "type": q_data.get("type", "UNKNOWN"),
            "prompt": [
                {
                    "role": "system",
                    "content": "Solve the problem. Show your reasoning inside <think></think> tags, and put your final answer inside <answer></answer> tags."
                },
                {
                    "role": "user",
                    "content": full_prompt_text
                }
            ],
            "answers": correct_answer,
            "images": images
        }
        
        dataset_records.append(record)

    if not dataset_records:
        print("❌ No valid questions found! Please check your data directory.")
        return

    # Convert to HuggingFace Dataset
    print(f"✅ Successfully processed {len(dataset_records)} unique questions.")
    
    hf_dataset = Dataset.from_list(dataset_records)
    
    # Save the dataset to disk
    hf_dataset.save_to_disk(output_dir)
    print(f"💾 Dataset saved to {output_dir}/")
    
    # Show a sample of a successfully populated record
    sample = next((r for r in dataset_records if r["answers"]), dataset_records[0])
    print("\n--- SAMPLE RECORD ---")
    print(f"ID: {sample['id']}")
    print(f"Type: {sample['type']}")
    print("Prompt:\n", sample['prompt'][1]['content'])
    print("Answer:\n", sample['answers'])

if __name__ == "__main__":
    build_dataset(data_dir="./boilerexam-questions", output_dir="./boilerexams-hf-dataset")
