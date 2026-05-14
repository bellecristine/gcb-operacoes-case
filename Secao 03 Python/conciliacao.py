import pandas as pd
from typing import Tuple


def conciliar_aportes(
    aportes: pd.DataFrame,
    transacoes_pix: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Concilia aportes internos com transações PIX do banco.

    Chave de conciliação: CPF + valor, com tolerância de D±1 na data.
    Duplicatas no lado PIX (mesmo CPF, valor e dia) são removidas
    antes do cruzamento.

    Args:
        aportes: colunas esperadas [id_aporte, cpf, valor, data_aporte]
        transacoes_pix: colunas esperadas [id_pix, cpf, valor, data_pix]

    Returns:
        conciliados, aportes_sem_pix, pix_sem_aporte
    """
    aportes = aportes.copy()
    transacoes_pix = transacoes_pix.copy()

    # Garantir que datas estão no formato certo
    aportes["data_aporte"] = pd.to_datetime(aportes["data_aporte"])
    transacoes_pix["data_pix"] = pd.to_datetime(transacoes_pix["data_pix"])

    # Remover duplicatas no lado PIX antes de cruzar
    # Critério: mesmo CPF, valor e dia → fica só a primeira
    transacoes_pix["data_pix_dia"] = transacoes_pix["data_pix"].dt.date
    transacoes_pix = transacoes_pix.drop_duplicates(
        subset=["cpf", "valor", "data_pix_dia"]
    ).drop(columns=["data_pix_dia"])

    # Cruzar pela chave principal: CPF + valor
    merged = aportes.merge(
        transacoes_pix,
        on=["cpf", "valor"],
        how="outer",
        indicator=True,
        suffixes=("_aporte", "_pix")
    )

    # Aplicar tolerância de D±1 nos que cruzaram nos dois lados
    ambos = merged[merged["_merge"] == "both"].copy()
    ambos["diff_dias"] = (
    ambos["data_pix"] - ambos["data_aporte"]
).abs().dt.days

    conciliados = ambos[ambos["diff_dias"] <= 1].drop(
        columns=["diff_dias", "_merge"]
    )

    # O que sobrou sem par
    ids_aporte_ok = set(conciliados["id_aporte"])
    ids_pix_ok = set(conciliados["id_pix"])

    aportes_sem_pix = aportes[
        ~aportes["id_aporte"].isin(ids_aporte_ok)
    ].copy()
    pix_sem_aporte = transacoes_pix[
        ~transacoes_pix["id_pix"].isin(ids_pix_ok)
    ].copy()

    return conciliados, aportes_sem_pix, pix_sem_aporte


# Testes
def test_caminho_feliz():
    """Par perfeito deve ser conciliado."""
    aportes = pd.DataFrame([{
        "id_aporte": 1, "cpf": "12345678900",
        "valor": 1000.0, "data_aporte": "2026-05-10"
    }])
    pix = pd.DataFrame([{
        "id_pix": 1, "cpf": "12345678900",
        "valor": 1000.0, "data_pix": "2026-05-10"
    }])

    conciliados, sem_pix, sem_aporte = conciliar_aportes(aportes, pix)

    assert len(conciliados) == 1
    assert len(sem_pix) == 0
    assert len(sem_aporte) == 0


def test_pix_duplicado_mesmo_dia():
    """Dois PIX iguais no mesmo dia não devem duplicar o aporte."""
    aportes = pd.DataFrame([{
        "id_aporte": 1, "cpf": "12345678900",
        "valor": 500.0, "data_aporte": "2026-05-10"
    }])
    pix = pd.DataFrame([
        {"id_pix": 1, "cpf": "12345678900",
         "valor": 500.0, "data_pix": "2026-05-10"},
        {"id_pix": 2, "cpf": "12345678900",
         "valor": 500.0, "data_pix": "2026-05-10"},
    ])

    conciliados, sem_pix, sem_aporte = conciliar_aportes(aportes, pix)

    assert len(conciliados) == 1
    assert len(sem_aporte) == 0


if __name__ == "__main__":
    test_caminho_feliz()
    test_pix_duplicado_mesmo_dia()
    print("Todos os testes passaram.")