import os
import json
import jwt
import httpx
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

ALGORITHMS = ["RS256"]

security = HTTPBearer()

def get_jwks():
    auth0_domain = os.getenv("AUTH0_DOMAIN")
    if not auth0_domain:
        raise ValueError("AUTH0_DOMAIN is not set in environment variables.")
    jwks_url = f"https://{auth0_domain}/.well-known/jwks.json"
    response = httpx.get(jwks_url)
    response.raise_for_status()
    return response.json()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validates the JWT token against Auth0 JWKS.
    Returns the decoded token payload on success.
    """
    if os.getenv("TESTING") == "True":
        # Support mock_token_{custom_id} to simulate multiple users
        token_str = credentials.credentials
        if token_str.startswith("mock_token_"):
            return {"sub": token_str.split("mock_token_")[1]}
        return {"sub": "qa_test_user_123"}

    token = credentials.credentials
    # Check if the token is a JWT (3 parts separated by dots)
    if len(token.split(".")) != 3:
        # It's an opaque token. Verify via Auth0 /userinfo endpoint.
        auth0_domain = os.getenv("AUTH0_DOMAIN")
        userinfo_url = f"https://{auth0_domain}/userinfo"
        try:
            resp = httpx.get(
                userinfo_url,
                headers={"Authorization": f"Bearer {token}"}
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid opaque token or unable to fetch user info",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Error validating opaque token: {str(e)}",
            )

    try:
        unverified_header = jwt.get_unverified_header(token)
        jwks = get_jwks()
        
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
                
        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate key in JWKS",
            )
            
        payload = jwt.decode(
            token,
            jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(rsa_key)),
            algorithms=ALGORITHMS,
            audience=os.getenv("AUTH0_AUDIENCE") if os.getenv("AUTH0_AUDIENCE") else None,
            issuer=f"https://{os.getenv('AUTH0_DOMAIN')}/"
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error validating token: {str(e)}",
        )
