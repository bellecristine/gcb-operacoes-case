import requests
import pandas as pd
import json
import time
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://api.exemplo.com/v1/operacoes"
OUTPUT_FILE = Path("operacoes.parquet")

MAX_TENTATIVAS = 5
MAX_FALHAS_SEGUIDAS = 3


def buscar_pagina(
    session: requests.Session,
    page: int,
    contadores_erro: dict
) -> dict | None:
    """
    Tenta buscar uma página da API.
    Separa erro temporário (retry) de erro definitivo (para).
    Atualiza contadores de erro por tipo.
    """
    for tentativa in range(MAX_TENTATIVAS):
        try:
            resp = session.get(
                BASE_URL,
                params={"page": page},
                timeout=10
            )

            if resp.status_code == 200:
                return resp.json()

            # Erro de rate limit — respeita Retry-After
            if resp.status_code == 429:
                espera = int(resp.headers.get("Retry-After", 2 ** tentativa))
                contadores_erro["status_429"] += 1
                logger.warning(
                    f"Página {page} — rate limit. "
                    f"Aguardando {espera}s."
                )
                time.sleep(espera)
                continue

            # Erro de servidor — vale tentar de novo
            if resp.status_code >= 500:
                espera = int(resp.headers.get("Retry-After", 2 ** tentativa))
                contadores_erro["status_5xx"] += 1
                logger.warning(
                    f"Página {page} — erro {resp.status_code}. "
                    f"Tentativa {tentativa + 1}/{MAX_TENTATIVAS}. "
                    f"Aguardando {espera}s."
                )
                time.sleep(espera)
                continue

            # Erro definitivo — não adianta tentar de novo
            logger.error(
                f"Página {page} retornou {resp.status_code}. "
                f"Erro definitivo, pulando."
            )
            return None

        except requests.exceptions.Timeout:
            espera = 2 ** tentativa
            contadores_erro["timeout"] += 1
            logger.warning(
                f"Timeout na página {page}. "
                f"Tentativa {tentativa + 1}/{MAX_TENTATIVAS}. "
                f"Aguardando {espera}s."
            )
            time.sleep(espera)

        except requests.exceptions.ConnectionError:
            espera = 2 ** tentativa
            contadores_erro["conexao"] += 1
            logger.warning(
                f"Erro de conexão na página {page}. "
                f"Aguardando {espera}s."
            )
            time.sleep(espera)

    # Esgotou tentativas
    contadores_erro["max_tentativas"] += 1
    logger.error(f"Página {page} falhou após {MAX_TENTATIVAS} tentativas.")
    return None


def ids_ja_salvos() -> set:
    """Lê IDs já persistidos para evitar duplicação."""
    if not OUTPUT_FILE.exists():
        return set()
    df = pd.read_parquet(OUTPUT_FILE, columns=["id"])
    return set(df["id"].tolist())


def executar():
    inicio = datetime.now()
    session = requests.Session()

    registros_novos = []
    contadores_erro = {
        "timeout": 0,
        "conexao": 0,
        "status_5xx": 0,
        "status_429": 0,
        "max_tentativas": 0
    }
    pagina = 1
    falhas_seguidas = 0
    ids_existentes = ids_ja_salvos()

    while True:
        resultado = buscar_pagina(session, pagina, contadores_erro)

        if resultado is None:
            falhas_seguidas += 1

            if falhas_seguidas >= MAX_FALHAS_SEGUIDAS:
                logger.error(
                    f"Circuit breaker: {MAX_FALHAS_SEGUIDAS} falhas "
                    f"seguidas. Encerrando."
                )
                break

            pagina += 1
            continue

        dados = resultado.get("data", [])

        # Sem dados — chegou no fim
        if not dados:
            break

        # Só adiciona o que ainda não foi salvo
        novos = [r for r in dados if r["id"] not in ids_existentes]
        registros_novos.extend(novos)
        falhas_seguidas = 0
        pagina += 1

    # Salva em parquet
    if registros_novos:
        df_novo = pd.DataFrame(registros_novos)
        if OUTPUT_FILE.exists():
            df_atual = pd.read_parquet(OUTPUT_FILE)
            df_final = pd.concat([df_atual, df_novo], ignore_index=True)
        else:
            df_final = df_novo
        df_final.to_parquet(OUTPUT_FILE, index=False)

    # Gera log estruturado
    duracao = (datetime.now() - inicio).total_seconds()
    total_paginas = pagina - 1
    total_erros = sum(contadores_erro.values())

    logger.info(f"Execução finalizada: {log}")


if __name__ == "__main__":
    executar()