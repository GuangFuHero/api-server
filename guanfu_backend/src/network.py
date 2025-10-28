"""
網路相關的工具函數

提供網路請求處理的共用工具，包括 IP 位址取得等功能。
"""

from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    取得客戶端的真實 IP 位址

    此函數會依序檢查以下來源來取得客戶端 IP：
    1. x-forwarded-for header（適用於反向代理，如 Nginx、Cloudflare）
    2. x-real-ip header（某些代理服務器使用）
    3. request.client.host（直接連接的客戶端）

    Args:
        request: FastAPI Request 物件

    Returns:
        str: 客戶端 IP 位址，如果無法取得則返回 "unknown"

    Examples:
        >>> from fastapi import Request
        >>> client_ip = get_client_ip(request)
        >>> print(f"Client IP: {client_ip}")
        Client IP: 192.168.1.100

    Note:
        - 當使用 x-forwarded-for 時，會取第一個 IP（避免代理鏈中的中間節點）
        - 在生產環境中，確保反向代理正確設定這些 headers
    """
    # 優先使用 x-forwarded-for（處理反向代理）
    x_forwarded_for = request.headers.get("x-forwarded-for", "")
    if x_forwarded_for:
        # 取第一個 IP（客戶端真實 IP）
        ip = x_forwarded_for.split(",")[0].strip()
        if ip:
            return ip

    # 次要使用 x-real-ip
    x_real_ip = request.headers.get("x-real-ip", "")
    if x_real_ip:
        return x_real_ip

    # 最後使用直接連接的客戶端 IP
    if request.client and request.client.host:
        return request.client.host

    # 如果都無法取得，返回 unknown
    return "unknown"
