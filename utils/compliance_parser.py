import json

# def extract_compliance(raw_output):
#     try:
#         cleaned = raw_output.replace("```", "").replace("json", "").strip()
#         return json.loads(cleaned).get("branding")
#     except Exception:
#         return print("Error Parsing.") 
#         #TODO: error parsing


def extract_compliance(raw_output):
    try:
        cleaned = raw_output.replace("```", "").replace("json", "").strip()
        return json.loads(cleaned).get("branding")

    except Exception:
        text = raw_output.lower()

        # FAIL first (more conservative)
        if re.search(r'\bfail(ed|ure)?\b', text):
            return "fail"

        if re.search(r'\bpass(ed|ing)?\b', text):
            return "pass"

        return None
