import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

def main():
    print("Available models and their supported methods:\n")
    for model in client.models.list():
        # Many models will have attributes like:
        # model.name and model.supported_generation_methods
        name = getattr(model, "name", "UNKNOWN_NAME")
        methods = getattr(model, "supported_generation_methods", [])
        print(f"- {name}")
        print(f"  supported_generation_methods: {methods}\n")

if __name__ == "__main__":
    main()
