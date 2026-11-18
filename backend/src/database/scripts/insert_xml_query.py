INSERT_XML = """
INSERT OR IGNORE INTO Xml (
    chNF, CFOP, vlrProd, dEmi, bcICMS, vlrICMS, bcST, vlrST, vlrIPI, Outras, Desconto
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""