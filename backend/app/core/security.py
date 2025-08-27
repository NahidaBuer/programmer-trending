import secrets

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.core.config import get_settings

security = HTTPBasic()


def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """验证 HTTP Basic Auth 凭据，返回用户名"""
    settings = get_settings()
    
    # 使用安全的字符串比较避免时序攻击
    correct_username = secrets.compare_digest(credentials.username, settings.admin_username)
    correct_password = secrets.compare_digest(credentials.password, settings.admin_password)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username


def verify_admin_credentials(username: str, password: str) -> bool:
    """验证管理员凭据"""
    settings = get_settings()
    
    correct_username = secrets.compare_digest(username, settings.admin_username)
    correct_password = secrets.compare_digest(password, settings.admin_password)
    
    return correct_username and correct_password