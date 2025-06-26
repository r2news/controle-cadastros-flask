from flask import Flask, render_template, request, redirect, url_for, Response
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'banco.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    print(f"Iniciando o banco de dados em: {DB_PATH}")
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cadastro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                telefone TEXT NOT NULL
            );
        ''')
    print('Banco inicializado.')

@app.route('/')
def index():
    conn = get_db_connection()
    cadastros = conn.execute('SELECT * FROM cadastro').fetchall()
    conn.close()
    return render_template('index.html', cadastros=cadastros)

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    conn = get_db_connection()
    conn.execute('INSERT INTO cadastro (nome, email, telefone) VALUES (?, ?, ?)', (nome, email, telefone))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/remover/<int:id>')
def remover(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM cadastro WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    conn = get_db_connection()
    cadastros = conn.execute('SELECT * FROM cadastro').fetchall()
    conn.close()
    linhas = ["Nome,E-mail,Telefone"]
    for c in cadastros:
        # Para garantir que não haja vírgula errada, usamos aspas em volta
        linhas.append(f'"{c["nome"]}","{c["email"]}","{c["telefone"]}"')
    csv_content = "\n".join(linhas)
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=cadastros.csv"}
    )

if __name__ == '__main__':
    print(f"Caminho absoluto do banco: {DB_PATH}")
    print("Iniciando aplicação...")
    init_db()
    app.run(debug=True, use_reloader=False)
