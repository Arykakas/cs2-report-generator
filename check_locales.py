import json
from pathlib import Path

# Paths to catalogs
locales_dir = Path(r"C:\Code\cs2-report\cs2_report\locales")
en_path = locales_dir / "en.json"
da_path = locales_dir / "da-DK.json"
ru_path = locales_dir / "ru-RU.json"

def check():
    with open(str(en_path), 'r', encoding='utf-8') as f:
        base = json.load(f)
    
    results = {}
    for path in [da_path, ru_path]:
        with open(str(path), 'r', encoding='utf-8') as f:
            target = json.load(f)
        
        missing = []
        mismatch = []
        for k, v in base.items():
            if k not in target:
                missing.append(k)
            else:
                import re
                b_ph = set(re.findall(r'\{(\w+)\}', v))
                t_ph = set(re.findall(r'\{(\w+)\}', target[k]))
                if b_ph != t_ph:
                    mismatch.append((k, list(b_ph), list(t_ph)))
        results[path.name] = {"missing": missing, "mismatch": mismatch}
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    check()
