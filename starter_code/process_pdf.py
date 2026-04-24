from google import genai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def extract_pdf_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    print(f"Uploading {file_path} to Gemini...")
    try:
        pdf_file = client.files.upload(file=file_path)
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
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[pdf_file, prompt]
    )
    content_text = response.text

    # Strip markdown code fences
    content_text = content_text.strip()
    if content_text.startswith("```json"):
        content_text = content_text[7:]
    elif content_text.startswith("```"):
        content_text = content_text[3:]
    if content_text.endswith("```"):
        content_text = content_text[:-3]
    content_text = content_text.strip()

    # Try to extract a JSON object by finding balanced braces
    try:
        extracted_data = json.loads(content_text)
    except json.JSONDecodeError:
        # Fallback: find the first { and last } to extract the JSON object
        start = content_text.find('{')
        end = content_text.rfind('}') + 1
        if start != -1 and end > start:
            json_str = content_text[start:end]
            try:
                extracted_data = json.loads(json_str)
            except json.JSONDecodeError:
                # Last resort: use regex to extract known fields
                extracted_data = {
                    "document_id": "pdf-doc-001",
                    "content": content_text,
                    "source_type": "PDF",
                    "author": "Unknown",
                    "timestamp": None,
                    "source_metadata": {"original_file": os.path.basename(file_path)}
                }
        else:
            extracted_data = {
                "document_id": "pdf-doc-001",
                "content": content_text,
                "source_type": "PDF",
                "author": "Unknown",
                "timestamp": None,
                "source_metadata": {"original_file": os.path.basename(file_path)}
            }

    return extracted_data
