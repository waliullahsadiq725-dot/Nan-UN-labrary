import base64, hashlib, hmac, json, secrets, time
from fastapi import HTTPException, status
from .config import SECRET_KEY, TOKEN_EXPIRE_MINUTES

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return "scrypt$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(digest).decode()

def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_text, digest_text = stored.split("$", 2)
        if scheme != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode())
        expected = base64.urlsafe_b64decode(digest_text.encode())
        actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def create_token(user_id: int, role: str) -> str:
    now = int(time.time())
    header = _b64(json.dumps({"alg":"HS256","typ":"JWT"}, separators=(",", ":")).encode())
    payload = _b64(json.dumps({"sub":str(user_id),"role":role,"iat":now,"exp":now + TOKEN_EXPIRE_MINUTES*60}, separators=(",", ":")).encode())
    body = header + "." + payload
    signature = _b64(hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest())
    return body + "." + signature

def decode_token(token: str) -> dict:
    try:
        header, payload, signature = token.split(".")
        body = header + "." + payload
        expected = _b64(hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("signature")
        data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        if int(data["exp"]) < int(time.time()):
            raise ValueError("expired")
        return data
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
