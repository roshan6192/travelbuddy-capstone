import json
import re

def cleanup_json(raw_text: str):
    """
    Remove ```json code fences and parse JSON.
    If parsing fails, return the original text.
    """

    if not isinstance(raw_text, str):
        return raw_text

    # Remove ```json and ``` markers
    cleaned = re.sub(r"```json|```", "", raw_text, flags=re.IGNORECASE).strip()

    # Strip extra backticks / whitespace
    cleaned = cleaned.strip("` \n\t")

    try:
        return json.loads(cleaned)
    except Exception:
        # If it isn't valid JSON, just return the cleaned string
        return cleaned
