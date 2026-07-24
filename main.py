from flask import Flask, render_template, request, redirect, url_for
import subprocess
import re

app = Flask(__name__)

model = "llama3.2:3b"
mensagens = []

def limpar_saida(texto):
    """Remove códigos de escape ANSI e caracteres de controle"""

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    controle = re.compile(r'[\x00-\x1f\x7f-\x9f]')
    
    texto_limpo = ansi_escape.sub('', texto)
    texto_limpo = controle.sub('', texto_limpo)
    return texto_limpo.strip()

@app.route('/')
def index():
    return render_template('index.html', mensagens=mensagens)

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form.get('prompt')
    
    if prompt:

        mensagens.append({'tipo': 'usuario', 'texto': prompt})

        resultado = subprocess.run(
            f"ollama run {model} {prompt}",
            shell=True,
            capture_output=True,
            text=True
        )

        resposta_bruta = resultado.stdout
        resposta_limpa = limpar_saida(resposta_bruta)

        if not resposta_limpa:
            resposta_limpa = limpar_saida(resultado.stderr)

        mensagens.append({'tipo': 'bot', 'texto': resposta_limpa})
    
    return redirect(url_for('index'))

@app.route('/clear', methods=['GET'])
def clear_messages():
    global mensagens
    mensagens = []
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
