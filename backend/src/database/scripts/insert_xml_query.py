INSERT_XML = """
INSERT OR IGNORE INTO Xml (
    chNF,
    CFOP,
    dEmi,
    cnpjEmit,
    cnpjDest,
    vlrProd,
    vNF,
    bcICMS,
    vlrICMS,
    bcST,
    vlrST,
    vlrIPI,
    Outras,
    Desconto
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""