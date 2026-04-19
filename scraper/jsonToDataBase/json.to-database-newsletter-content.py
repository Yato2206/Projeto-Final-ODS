import json
import pyscopg2

# Estabelecer ligação com a base de dados
conn = pyscopg2.connect( #configurar isto direito
    dbname="postgres",
    user="postgres",
    password="iselPs123",
    host="localhost",
    port="5432"
)# depois colocar o nome correto da base de dados
cursor = conn.cursor()

# Ler o ficheiro JSON
with open ('../newsletter-content.json', 'r') as json_file:
    data = json.load(json_file)

# Inserir dados
for item in data:
    cursor.execute(
        "INSERT INTO newsletter (title, politecnico_titulo, politecnico_texto, noticias, date_checked) VALUES (%?, %?, %?, %?, %?)",
        (item['title'], item['politecnico_titulo'], item['politecnico_texto'], item['noticias'], item['date_checked'])
    )

conn.commit()
cursor.close()
conn.close()