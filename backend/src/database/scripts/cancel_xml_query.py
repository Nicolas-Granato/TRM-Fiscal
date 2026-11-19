CANCEL_XML = """
INSERT INTO Xml (chNF, Cancelada)
VALUES (?, TRUE)
ON CONFLICT (chNF) DO UPDATE SET Cancelada = TRUE;
"""