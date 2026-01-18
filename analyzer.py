import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model_name = "gemini-1.5-flash"

def call_gemini(prompt):
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.7,
            "top_p": 0.9,
            "max_output_tokens": 300
        }
    )
    return response.text