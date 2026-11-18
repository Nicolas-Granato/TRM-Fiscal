SETUP_DATABASE = """
CREATE TEMP TABLE Xml (
    chNF VARCHAR(44) PRIMARY KEY,
    CFOP VARCHAR(4),
    dEmi DATE,
    cnpjEmit VARCHAR(14),
    cnpjDest VARCHAR(14),
    vlrProd INTEGER,
    vNF INTEGER,
    bcICMS INTEGER,
    vlrICMS INTEGER,
    bcST INTEGER,
    vlrST INTEGER,
    vlrIPI INTEGER,
    Outras INTEGER,
    Desconto INTEGER,
    Cancelada BOOLEAN DEFAULT FALSE
);
"""