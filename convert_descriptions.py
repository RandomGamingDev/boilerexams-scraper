import json
from pathlib import Path

def main():
    image_dir = Path('boilerexam-questions/resources/IMAGE')
    descriptions = {}
    
    if not image_dir.exists():
        print(f"Error: Directory '{image_dir}' does not exist.")
        return

    for txt_file in image_dir.glob('*.txt'):
        image_id = txt_file.stem
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                description = f.read().strip()
                descriptions[image_id] = description
        except Exception as e:
            print(f"Error reading {txt_file}: {e}")

    output_file = 'descriptions.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(descriptions, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully converted {len(descriptions)} descriptions into {output_file}")

if __name__ == '__main__':
    main()
