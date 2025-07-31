import pyodbc

conn = pyodbc.connect(
    "Driver={ODBC Driver 18 for SQL Server};Server=tcp:notes-1231234.database.windows.net,1433;Database=Notes;Uid=CloudSAddd44548;Pwd=#Admin123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;",
    timeout=30
)
print("Connected!")