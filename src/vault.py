import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class SecureVault:
    SECRET_KEY = os.getenv("ANONYMIZER_VAULT_KEY", AESGCM.generate_key(bit_length=256))

    @classmethod
    def _get_key_bytes(cls) -> bytes:
        if isinstance(cls.SECRET_KEY, bytes):
            return cls.SECRET_KEY
        return cls.SECRET_KEY.encode("utf-8")[:32]

    @classmethod
    def seal_mapping(cls, mapping: dict, output_path: str = None) -> str:
        if not mapping:
            return ""

        aesgcm = AESGCM(cls._get_key_bytes())
        nonce = os.urandom(12)
        payload = json.dumps(mapping, ensure_ascii=False).encode("utf-8")
        ciphertext = aesgcm.encrypt(nonce, payload, None)
        bundle = nonce + ciphertext

        if output_path:
            with open(output_path, "wb") as f:
                f.write(bundle)

        return base64.b64encode(bundle).decode("utf-8")

    @classmethod
    def unseal_mapping(cls, encrypted_data) -> dict:
        if isinstance(encrypted_data, str):
            raw_bytes = base64.b64decode(encrypted_data.encode("utf-8"))
        else:
            raw_bytes = bytes(encrypted_data)

        if len(raw_bytes) < 13:
            return {}

        aesgcm = AESGCM(cls._get_key_bytes())
        nonce = raw_bytes[:12]
        ciphertext = raw_bytes[12:]
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        return json.loads(decrypted.decode("utf-8"))
