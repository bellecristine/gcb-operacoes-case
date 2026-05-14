import hmac
import hashlib
import os


def validar_assinatura(payload_bruto: bytes, assinatura_recebida: str) -> bool:
    """
    Valida assinatura HMAC-SHA256 de webhook recebido.

    Args:
        payload_bruto: corpo da requisição em bytes, sem modificação
        assinatura_recebida: valor do header X-Signature

    Returns:
        True se válida, False caso contrário
    """
    chave_secreta = os.environ.get("WEBHOOK_SECRET")
    if not chave_secreta:
        raise EnvironmentError("WEBHOOK_SECRET não configurado.")

    assinatura_esperada = hmac.new(
        key=chave_secreta.encode("utf-8"),
        msg=payload_bruto,
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(assinatura_esperada, assinatura_recebida)