import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
from google.generativeai import types
import io
import base64

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model_name = "gemini-2.0-flash"
image_model_name = "gemini-1.5-pro"

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
    # Handle blocked/empty responses
    if not response.text:
        return "Unable to generate response. The request may have been blocked by safety filters or the model encountered an error."
    
    return response.text

def generate_agent_image(prompt):
    try:
        model = genai.GenerativeModel(image_model_name)
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7
            }
        )

        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data"):
                image_bytes = part.inline_data.data

                # Enforce square output
                image = Image.open(io.BytesIO(image_bytes))
                image = image.resize((1024, 1024))

                out = io.BytesIO()
                image.save(out, format="PNG")
                return out.getvalue()

    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None

generate_agent_image("Hello World, I am a robot")