SETUP_DATABASE = """
CREATE TEMP TABLE Xml (
    chNF VARCHAR(44) PRIMARY KEY,
    CFOP VARCHAR(4),
    vlrProd INTEGER,
    vlrNF INTEGER,
    dEntrada DATE,
    dSaida DATE,
    bcICMS INTEGER,
    vlrICMS INTEGER,
    bcST INTEGER,
    vlrST INTEGER,
    vlrIPI INTEGER,
    Outras INTEGER,
    Desconto INTEGER,
    Cancelada BOOLEAN
);
"""