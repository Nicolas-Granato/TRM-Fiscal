# --- Canceled report queries ---

CANCELED_REPORT_QUERY = """
SELECT
    SUBSTRING(chNF, 21, 2) AS mod,
    SUBSTRING(chNF, 23, 3) AS serie,
    SUBSTRING(chNF, 26, 9) AS nNF,
    COALESCE(vlrProd, 0) AS vlrProd,
    COALESCE(vNF, 0) AS vlrTotal
FROM Xml
WHERE Cancelada = TRUE
ORDER BY dEmi NULLS LAST, serie, nNF;
"""

TOTAL_CANCELED = """
SELECT
    COUNT(*) AS qtd_canceladas,
    COALESCE(SUM(vlrProd), 0) AS total_vlrProd,
    COALESCE(SUM(vNF), 0) AS total_vlrTotal
FROM Xml
WHERE Cancelada = TRUE;
"""

# --- Resume report queries ---

RESUME_REPORT_QUERY = """
SELECT
    SUBSTRING(chNF, 21, 2) AS mod,
    SUBSTRING(chNF, 26, 9) AS nNF,
    dEmi,
    chNF,
    COALESCE(vNF, 0) AS vNF
FROM Xml
WHERE cnpjEmit = ?
  AND Cancelada = FALSE
ORDER BY dEmi, mod, nNF;
"""

# --- CFOP_model_report queries ---

CFOP_MODEL_REPORT_QUERY = """
SELECT
    SUBSTRING(chNF, 21, 2) AS mod,
    CFOP,
    COALESCE(SUM(vNF), 0) AS total_vNF,
    COALESCE(SUM(bcICMS), 0) AS total_bcICMS,
    COALESCE(SUM(vlrICMS), 0) AS total_vlrICMS
FROM Xml
WHERE cnpjEmit = ?
  AND Cancelada = FALSE
  AND LEFT(CFOP, 1) NOT IN ('1', '2')
GROUP BY
    SUBSTRING(chNF, 21, 2),
    CFOP
ORDER BY
    mod,
    CFOP;
"""

TOTAL_CFOP_MODEL = """
SELECT
    COALESCE(SUM(vNF), 0) AS geral_vNF,
    COALESCE(SUM(bcICMS), 0) AS geral_bcICMS,
    COALESCE(SUM(vlrICMS), 0) AS geral_vlrICMS
FROM Xml
WHERE cnpjEmit = ?
  AND Cancelada = FALSE
  AND LEFT(CFOP, 1) NOT IN ('1', '2');
"""

# --- Purchase report queries ---

PURCHASE_REPORT_QUERY = """
SELECT
    SUBSTRING(chNF, 21, 2) AS mod,
    SUBSTRING(chNF, 23, 3) AS serie,
    SUBSTRING(chNF, 26, 9) AS nNF,
    dEmi,
    chNF,
    COALESCE(vlrProd, 0) AS vlrProd,
    COALESCE(vNF, 0) AS vNF
FROM Xml
WHERE cnpjEmit != ?
  AND cnpjDest = ?
  AND Cancelada = FALSE
ORDER BY dEmi, serie, nNF;
"""

TOTAL_PURCHASE = """
SELECT
    COALESCE(SUM(bcICMS), 0) AS total_bcICMS,
    COALESCE(SUM(vlrICMS), 0) AS total_vlrICMS,
    COALESCE(SUM(bcST), 0) AS total_bcST,
    COALESCE(SUM(vlrST), 0) AS total_vlrST,
    COALESCE(SUM(vlrIPI), 0) AS total_vlrIPI,
    COALESCE(SUM(Outras), 0) AS total_Outras,
    COALESCE(SUM(Desconto), 0) AS total_Desconto,
    COALESCE(SUM(vlrProd), 0) AS total_vlrProd,
    COALESCE(SUM(vNF), 0) AS total_vNF
FROM Xml
WHERE cnpjEmit != ?
  AND cnpjDest = ?
  AND Cancelada = FALSE;
"""