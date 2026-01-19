import re
import json
from datetime import datetime, timedelta
import json


def parse_get_params(raw_text: str) -> dict:
    if not raw_text or not raw_text.strip():
        return {}

    raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, dict):
            return parsed
    except:
        pass

    params = {}
    lines = raw_text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line or ":" not in line:
            i += 1
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value == "":
            buffer = []
            i += 1

            while i < len(lines):
                next_line = lines[i].strip()

                if ":" in next_line and not next_line.startswith("{"):
                    break

                buffer.append(next_line)
                i += 1

            raw_block = "\n".join(buffer).strip()

            try:
                params[key] = json.loads(raw_block)
            except:
                params[key] = raw_block

            continue

        val_lower = value.lower()
        if val_lower == "true":
            value = True
        elif val_lower == "false":
            value = False
        else:
            try:
                value = int(value)
            except:
                try:
                    value = float(value)
                except:
                    pass

        params[key] = value
        i += 1

    return params



def normalize_params(params: dict) -> dict:
    final_params = {}

    for key, value in params.items():

        # ✅ SPECIAL CASE: commandValue must stay JSON
        if key == "commandValue" and isinstance(value, dict):
            from_val = value.get("From")

            if not from_val:
                raise ValueError("commandValue.From is required")

            from_dt = _to_datetime(from_val)
            to_dt = from_dt + timedelta(hours=1)

            final_params[key] = json.dumps({
                "From": from_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "To": to_dt.strftime("%Y-%m-%d %H:%M:%S")
            })

            continue

        # 1️⃣ Dict range → flatten (for all OTHER params)
        if isinstance(value, dict):
            for sub_key, sub_val in value.items():
                final_params[f"{key}{sub_key}"] = _normalize_datetime(sub_val)
            continue

        # 2️⃣ String range: "date to date"
        if isinstance(value, str):
            match = re.match(
                r"^\s*(\d{4}-\d{2}-\d{2})(?:\s+\d{2}:\d{2}:\d{2})?\s+to\s+"
                r"(\d{4}-\d{2}-\d{2})(?:\s+\d{2}:\d{2}:\d{2})?\s*$",
                value,
                re.IGNORECASE
            )
            if match:
                final_params[f"{key}From"] = _normalize_datetime(match.group(1))
                final_params[f"{key}To"] = _normalize_datetime(match.group(2))
                continue

        # 3️⃣ Single scalar
        final_params[key] = _normalize_datetime(value)

    return final_params


def _normalize_datetime(value):
    if isinstance(value, str):
        if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            return f"{value} 00:00:00"
    return value


def _to_datetime(value: str) -> datetime:
    if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        value = f"{value} 00:00:00"
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")





















    







