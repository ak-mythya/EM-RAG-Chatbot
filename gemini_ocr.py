import google.generativeai as genai
import PIL.Image
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = "AIzaSyB8QjzwpuK2z1-RkzCPJux1J11_QSLYZy8"

class GeminiOCR:
    def __init__(self):
        """Initialize Gemini OCR with API key."""
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")

    def extract_text(self, image_path: str) -> str:
        """
        Extract text from an image using Gemini Pro Vision.
        
        :param image_path: Path to the image file.
        :return: Extracted text as a string.
        """
        try:
            image = PIL.Image.open(image_path)
            # Add a specific prompt to instruct the model to perform OCR
            prompt = "Perform OCR on this image and return the exact text content as it appears, without summarizing or interpreting it."
            response = self.model.generate_content([prompt, image], stream=False)
            return response.text.strip() if response.text else "No text detected"
        except Exception as e:
            return f"Error processing image: {str(e)}"

if __name__ == "__main__":
    # Create an instance of GeminiOCR
    ocr = GeminiOCR()

    # Provide an image path
    image_path = "test.jpg"  # Change this to your actual image

    # Perform OCR and print result
    extracted_text = ocr.extract_text(image_path)
    print("Extracted Text:")
    print(extracted_text)