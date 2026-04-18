import json
import pyscopg2

# Estabelecer ligação com a base de dados
conn = psycopg2.connect( #configurar isto direito
    dbname="minha_db",
    user="meu_user",
    password="minha_pass",
    host="localhost",
    port="5432"
)# depois colcoar o nome correto da base de dados
cursor = conn.cursor()

# Ler o ficheiro JSON
with open ('../newsletter.json', 'r') as json_file:
    data = json.load(json_file)

# Inserir dados
for item in data:
    cursor.execute(
        "INSERT INTO newsletter (title, date, link, date_checked) VALUES (%?, %?, %?, %?, %?)",
        (item['title'], item['date'], item['link'], item['date_checked'])
    )

conn.commit()
cursor.close()
conn.close()