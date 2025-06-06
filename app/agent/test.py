from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv(dotenv_path=r'c:\Users\lenovo\Desktop\agent\.env')
print("Loaded key:", os.getenv("GROQ_API_KEY"))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Try different models that are commonly available
models_to_try = [
    "llama3-8b-8192",
    "llama3-70b-8192", 
    "mixtral-8x7b-32768",
    "gemma-7b-it"
]

for model in models_to_try:
    try:
        print(f"\nTrying model: {model}")
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Say hello"}
            ],
            max_tokens=10
        )
        print(f"✅ SUCCESS with {model}:", completion.choices[0].message.content)
        break
    except Exception as e:
        print(f"❌ Failed with {model}:", str(e))

# If all models fail, try listing models
try:
    print("\n📋 Available models:")
    models = client.models.list()
    for model in models.data:
        print(f"  - {model.id}")
except Exception as e:
    print("❌ Could not list models:", e)