CANCEL_XML = """
UPDATE Xml SET Cancelada = TRUE 
WHERE chNF = ?;
"""