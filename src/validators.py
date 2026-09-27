import re

# 1. Structure générique de tableau / formulaire (Agnostique au mot-clé)
# Capture n'importe quel intitulé de champ (2 à 30 lettres) suivi d'un délimiteur et d'un nom propre
RE_GENERIC_KEY_VALUE = re.compile(
    r'(?m)^[ \t]*([A-Za-zÀ-ÿ\s\'-]{2,30})[ \t]*[:|=][ \t]*'
    r'([A-ZÀ-ÿ][a-zÀ-ÿ\-]+(?:\s+[A-ZÀ-ÿ][a-zÀ-ÿ\-]+){1,3})'
)

# 2. Coordonnées réseau et communication (Normes RFC)
RE_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b')
RE_IP = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')

# 3. Téléphonie (Formats nationaux et internationaux)
RE_PHONE = re.compile(
    r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.\-_]?\d{2}){4}\b|'
    r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,9}\b'
)

# 4. Dates, Horodatages et plages calendaires
RE_FULL_DATETIME = re.compile(r'\b\d{2}[\/\-.]\d{2}[\/\-.](?:19|20)\d{2}(?:\s*[\-–—@]\s*\d{1,2}:\d{2}(?::\d{2})?)?\b')
RE_DATE_NUM = re.compile(r'\b(?:0[1-9]|[12]\d|3[01])[\/\-.](?:0[1-9]|1[0-2])[\/\-.](?:19|20)\d{2}\b')
RE_DATE_RANGE = re.compile(
    r'\bdu\s+(?:0?[1-9]|[12]\d|3[01])(?:\s*(?:au|-)\s*(?:0?[1-9]|[12]\d|3[01]))?\s+'
    r'(?:janvier|février|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre)(?:\s+(?:19|20)\d{2})?\b',
    re.IGNORECASE
)

# 5. Adresses et voiries (Typologie cadastrale officielle)
RE_FULL_ADDRESS = re.compile(
    r'\b\d{1,4}(?:\s*(?:bis|ter))?,?\s+'
    r'(?:rue|avenue|av\.|boulevard|bd|chemin|impasse|place|allée|cours|route|voie)\s+'
    r'[A-Za-zÀ-ÿ\s\'-]+,?\s+'
    r'(?:0[1-9]|[1-8]\d|9[0-8])\d{3}\s+[A-Za-zÀ-ÿ\s\'-]+\b',
    re.IGNORECASE
)
RE_STREET_ALONE = re.compile(
    r'\b\d{1,4}(?:\s*(?:bis|ter))?,?\s+'
    r'(?:rue|avenue|av\.|boulevard|bd|chemin|impasse|place|allée|cours|route|voie)\s+'
    r'[A-Za-zÀ-ÿ\s\'-]+?(?=\s+(?:à|dans|en|vers|près|au|aux|\b[0-9]{5}\b|\[ID-|,|\.|$))',
    re.IGNORECASE
)

# 6. Identifiants techniques et bancaires
RE_REFS = re.compile(r'\b[A-Z]{2,6}[\-_][A-Za-z0-9]{3,12}\b')
RE_IBAN_CANDIDATE = re.compile(r'\b[A-Z]{2}\d{2}(?:[\s\-]?[A-Z0-9]{1,4}){3,8}\b', re.IGNORECASE)
RE_SIRET_EXPLICIT = re.compile(r'\bSIRET\s*[:\s]*(\d{3}[\s.]?\d{3}[\s.]?\d{3}[\s.]?\d{5})\b', re.IGNORECASE)
RE_SIRET_STANDALONE = re.compile(r'\b\d{3}\s?\d{3}\s?\d{3}\s?\d{5}\b|\b\d{14}\b')

# 7. Montants financiers universels (symboles monétaires et codes devises ISO)
RE_FINANCIAL_AMOUNTS = re.compile(
    r'\b\d{1,3}(?:[\s\u00A0.]\d{3})*(?:[.,]\d{1,2})?\s*(?:€|euros?|eur|\$|dollars?|usd|£|livres?|gbp|chf)(?!\w)',
    re.IGNORECASE
)

def luhn_checksum(val_str: str) -> bool:
    digits = [int(c) for c in val_str if c.isdigit()]
    if len(digits) < 9:
        return False
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(int(c) for c in str(d * 2))
    return total % 10 == 0

def iban_checksum(iban: str) -> bool:
    clean = re.sub(r'[\s\-]', '', iban).upper()
    if len(clean) < 14 or not clean[:2].isalpha():
        return False
    reordered = clean[4:] + clean[:4]
    digits = ""
    for c in reordered:
        if c.isdigit():
            digits += c
        elif c.isalpha():
            digits += str(ord(c) - 55)
        else:
            return False
    return int(digits) % 97 == 1

def extract_deterministic_pii(text: str):
    entities = []

    for m in RE_GENERIC_KEY_VALUE.finditer(text):
        entities.append({
            "type": "PER",
            "text": m.group(2).strip(),
            "start": m.start(2),
            "end": m.end(2),
            "score": 1.0
        })

    for m in RE_FULL_DATETIME.finditer(text):
        entities.append({"type": "DATETIME", "text": m.group().strip(), "start": m.start(), "end": m.end(), "score": 1.0})

    for m in RE_DATE_NUM.finditer(text):
        entities.append({"type": "DATE", "text": m.group().strip(), "start": m.start(), "end": m.end(), "score": 1.0})

    for m in RE_DATE_RANGE.finditer(text):
        entities.append({"type": "DATE_RANGE", "text": m.group().strip(), "start": m.start(), "end": m.end(), "score": 0.96})

    for m in RE_EMAIL.finditer(text):
        entities.append({"type": "EMAIL", "text": m.group(), "start": m.start(), "end": m.end(), "score": 1.0})

    for m in RE_IP.finditer(text):
        entities.append({"type": "IP_ADDRESS", "text": m.group(), "start": m.start(), "end": m.end(), "score": 0.95})

    for m in RE_PHONE.finditer(text):
        val = m.group().strip()
        digits = re.sub(r'\D', '', val)
        if 9 <= len(digits) <= 15:
            entities.append({"type": "PHONE_NUMBER", "text": val, "start": m.start(), "end": m.end(), "score": 0.99})

    for m in RE_FULL_ADDRESS.finditer(text):
        entities.append({"type": "ADDRESS", "text": m.group().strip(), "start": m.start(), "end": m.end(), "score": 0.99})

    for m in RE_STREET_ALONE.finditer(text):
        entities.append({"type": "ADDRESS", "text": m.group().strip(), "start": m.start(), "end": m.end(), "score": 0.98})

    for m in RE_REFS.finditer(text):
        entities.append({"type": "DOCUMENT_REF", "text": m.group().strip(), "start": m.start(), "end": m.end(), "score": 0.99})

    for m in RE_IBAN_CANDIDATE.finditer(text):
        clean_iban = re.sub(r'[\s\-]', '', m.group())
        if iban_checksum(clean_iban):
            entities.append({"type": "IBAN", "text": m.group().strip(), "start": m.start(), "end": m.end(), "score": 1.0})

    for m in RE_SIRET_EXPLICIT.finditer(text):
        entities.append({"type": "SIRET", "text": m.group(1).strip(), "start": m.start(1), "end": m.end(1), "score": 1.0})

    for m in RE_SIRET_STANDALONE.finditer(text):
        digits_only = re.sub(r'\D', '', m.group())
        if len(digits_only) == 14 and luhn_checksum(digits_only):
            entities.append({"type": "SIRET", "text": m.group().strip(), "start": m.start(), "end": m.end(), "score": 1.0})

    for m in RE_FINANCIAL_AMOUNTS.finditer(text):
        entities.append({"type": "FINANCIAL_AMOUNT", "text": m.group().strip(), "start": m.start(), "end": m.end(), "score": 1.0})

    return entities
