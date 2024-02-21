
import datetime
import jwt
import os


JWT_SECRET = os.environ.get(
    "JWT_SECRET",
    "django-insecure-0hme7v3mamz1a^=a(*2i8(4=)wair_wm#!2lj93m$o+&7u+sp&qtec_solutionjwt",
)
JWT_HEADER = "JW"
JWT_EXPIRE_DATE = os.environ.get("JWT_EXPIRE_DATE", 30)





def generate_access_token(username,user_type, secret=JWT_SECRET, expiration_days=JWT_EXPIRE_DATE):
    payload = {
        "username": username,
        "user_type":user_type,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(days=int(expiration_days)),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_access_token(access_token, secret=JWT_SECRET):
    try:
        payload = jwt.decode(access_token, secret, algorithms=["HS256"])
        if "exp" in payload:
            exp = payload["exp"]
            if isinstance(exp, int):
                exp = datetime.datetime.fromtimestamp(exp)
            if exp < datetime.datetime.utcnow():
                return False, None
        return True, payload
    except:
        return False, None
    
    
from django.http import JsonResponse
from functools import wraps

def verify_access_token_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = args[1].headers.get("Authorization", None)
        if not access_token:
            return JsonResponse(
                {"errors": [{"field": "auth", "message": "Access token is required"}]},
                status=401,
            )
        _header, _token = access_token.split(" ")
        is_valid, decoded_payload = verify_access_token(_token)  # Assuming verify_access_token is a function that checks the token validity
        if not is_valid:
            return JsonResponse(
                {"errors": [{"field": "auth", "message": "Access token is not valid"}]},
                status=401,
            )
        kwargs["is_valid"] = is_valid
        kwargs["decoded_payload"] = decoded_payload
        username=decoded_payload["username"]
        user_type= decoded_payload["user_type"]
        kwargs["username"] = username
        kwargs["user_type"] = user_type

        return func(*args, **kwargs)

    return wrapper
