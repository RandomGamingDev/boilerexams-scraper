import os
import time
from pathlib import Path
from google import genai
from PIL import Image

# ==========================================
# CONFIGURATION
# ==========================================
IMAGE_DIR = "./boilerexam-questions/resources/IMAGE"
MODEL_NAME = "gemini-3.1-flash-lite" 
RPM_LIMIT = 15

# ==========================================
# SYSTEM PROMPT
# ==========================================
VISION_PROMPT = """You are an expert technical vision model. Your job is to describe this image exhaustively so a text-only math and physics AI model can solve complex problems based solely on your description.

Extract and describe the following explicitly:
1. ALL text, numbers, variables, and mathematical symbols exactly as written.
2. Spatial relationships and geometry (e.g., 'Block A is resting on a 30-degree incline').
3. For graphs: state the axis labels, units, scale, key coordinate points, intercepts, and the general shape.
4. For diagrams: list all dimensions, node labels, boundary conditions, and flow directions.

Do not attempt to solve the problem. Provide a pure, highly structured, and exhaustive visual transcription."""

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set.")
        return

    client = genai.Client(api_key=api_key)
    sleep_time = (60.0 / RPM_LIMIT) + 0.5
    
    image_dir_path = Path(IMAGE_DIR)
    if not image_dir_path.exists():
        print(f"❌ Error: Image directory {IMAGE_DIR} not found.")
        return

    all_image_paths = list(image_dir_path.glob("*.png")) + list(image_dir_path.glob("*.jpg"))
    pending_images = [img for img in all_image_paths if not img.with_suffix('.txt').exists()]
    
    print(f"Total images found: {len(all_image_paths)}")
    print(f"Already processed: {len(all_image_paths) - len(pending_images)}")
    print(f"Remaining to process: {len(pending_images)}\n")

    if not pending_images:
        print("🎉 All images have been processed! You are ready to build your dataset.")
        return

    success_count = 0

    for img_path in pending_images:
        txt_path = img_path.with_suffix('.txt')
        print(f"Processing {img_path.name}...")
        
        # Retry loop: Keeps trying the same image until it succeeds or hits a non-rate-limit error
        while True:
            try:
                img = Image.open(img_path)
                
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[VISION_PROMPT, img]
                )
                
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
                    
                print(f"✅ Saved description for {img_path.name}")
                success_count += 1
                break # Success! Break out of the retry loop and move to the next image
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    print("⚠️ Rate limit hit. Waiting 30 seconds for the bucket to refill...")
                    time.sleep(30) 
                    # Does NOT break. The while loop will restart and try this image again.
                else:
                    print(f"❌ Error processing {img_path.name}: {error_msg}")
                    break # If it's a real error (like a corrupted image), skip it and move on
            
        # Respect the standard free tier rate limits strictly between successful calls
        time.sleep(sleep_time)

    print(f"\nFinished session. Successfully generated {success_count} new descriptions.")

if __name__ == "__main__":
    main()
