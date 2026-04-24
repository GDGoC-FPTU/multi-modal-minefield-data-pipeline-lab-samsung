import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from schema import UnifiedDocument

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def extract_pdf_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    model = genai.GenerativeModel('gemini-2.5-flash')

    print(f"Uploading {file_path} to Gemini...")
    try:
        pdf_file = genai.upload_file(path=file_path)
    except Exception as e:
        print(f"Failed to upload file to Gemini: {e}")
        return None

    prompt = """
Analyze this document and extract a summary and the author.
Output exactly as a JSON object matching this exact format:
{
    "document_id": "pdf-doc-001",
    "content": "Summary: [Insert your 3-sentence summary here]",
    "source_type": "PDF",
    "author": "[Insert author name here]",
    "timestamp": null,
    "source_metadata": {"original_file": "lecture_notes.pdf"}
}
"""

    print("Generating content from PDF using Gemini...")
    try:
        response = model.generate_content([pdf_file, prompt])
        content_text = response.text
    except Exception as e:
        print(f"Failed to generate content from PDF: {e}")
        return None

    if content_text.startswith("```json"):
        content_text = content_text[7:]
    if content_text.endswith("```"):
        content_text = content_text[:-3]
    if content_text.startswith("```"):
        content_text = content_text[3:]

    try:
        extracted_data = json.loads(content_text.strip())
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from Gemini response: {e}")
        print(f"Raw response: {content_text}")
        return None

    try:
        doc = UnifiedDocument(**extracted_data)
        return doc.model_dump(mode='json')
    except Exception as e:
        print(f"Failed to validate extracted data against schema: {e}")
        return extracted_data
