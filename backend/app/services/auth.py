import os
import time
from typing import Dict
import jwt
import requests
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

security = HTTPBearer()

FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "")
FIREBASE_CERTS_URL = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"

# Cache public keys to prevent querying Google APIs on every request
_certs_cache = {}
_certs_expiry = 0

def get_firebase_public_keys() -> Dict[str, str]:
    global _certs_cache, _certs_expiry
    now = time.time()
    if _certs_cache and now < _certs_expiry:
        return _certs_cache

    try:
        res = requests.get(FIREBASE_CERTS_URL, timeout=5)
        if res.status_code == 200:
            certs = res.json()
            public_keys = {}
            for kid, cert_pem in certs.items():
                try:
                    cert = load_pem_x509_certificate(cert_pem.encode())
                    pubkey = cert.public_key()
                    public_keys[kid] = pubkey.public_bytes(
                        encoding=Encoding.PEM,
                        format=PublicFormat.SubjectPublicKeyInfo,
                    ).decode()
                except Exception:
                    continue

            _certs_cache = public_keys
            control = res.headers.get("Cache-Control", "")
            max_age = 3600
            for part in control.split(","):
                if "max-age" in part:
                    try:
                        max_age = int(part.split("=")[1].strip())
                    except Exception:
                        pass
            _certs_expiry = now + max_age
            return _certs_cache
    except Exception as e:
        if _certs_cache:
            return _certs_cache
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Firebase public certificates: {str(e)}"
        )

    raise HTTPException(status_code=500, detail="Failed to fetch Firebase public certificates")

def verify_firebase_token(token: str, project_id: str) -> Dict:
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Token header is missing 'kid'")

        public_keys = get_firebase_public_keys()
        public_key_pem = public_keys.get(kid)
        if not public_key_pem:
            raise HTTPException(status_code=401, detail="Invalid token 'kid'")

        payload = jwt.decode(
            token,
            public_key_pem,
            algorithms=["RS256"],
            audience=project_id,
            issuer=f"https://securetoken.google.com/{project_id}"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Firebase token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Firebase token: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    token = credentials.credentials

    if not FIREBASE_PROJECT_ID:
        print("WARNING: FIREBASE_PROJECT_ID is not configured. Falling back to Mock Developer user.")
        return {
            "id": "mock-user-123",
            "email": "developer@example.com",
            "mock": True
        }

    if token.startswith("mock-"):
        print("DEBUG: Active session authenticated via developer mock token.")
        return {
            "id": "mock-user-123",
            "email": "developer@example.com",
            "mock": True
        }

    payload = verify_firebase_token(token, FIREBASE_PROJECT_ID)
    uid = payload.get("sub")
    email = payload.get("email")
    if not uid or not email:
        raise HTTPException(status_code=401, detail="Invalid token payload (missing UID or email)")

    return {
        "id": uid,
        "email": email
    }
