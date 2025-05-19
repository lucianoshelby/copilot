from flask import Flask, render_template, request, jsonify, session
import sys
import os
sys.path.append('C:\\Users\\IMEI\\Documents\\AutoMX\\automacoes')
from automacoes.pecas import sincronizar_pecas
from testes.config import conectar_perfil_principal, configurar_driver_producao, carregar_todos_cookies, capturar_todos_cookies
from multiprocessing import Process, Lock, Queue
from flask_socketio import SocketIO, emit
from flask_session import Session
import threading
import time
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)
os_em_processamento = set()
lock = Lock()
COOKIES_TEMP_PATH = "cookies_temp.json"
progress_queue = Queue()

def processar_os(os_gspn, sid, queue):
    os_gspn = os_gspn.strip()
    driver = None
    print(f"Iniciando processar_os para OS {os_gspn}")
    try:
        print(f"Estado de os_em_processamento antes de sincronizar: {os_em_processamento}")
        queue.put({'os': os_gspn, 'step': 'Iniciando', 'status': 'running', 'sid': sid})
        sucesso = sincronizar_pecas(os_gspn, queue, sid)
        print(f"sincronizar_pecas retornou: {sucesso}")
        if sucesso:
            queue.put({'os': os_gspn, 'step': 'Tudo certo', 'status': 'completed', 'sid': sid})
            time.sleep(0.8)
        else:
            queue.put({'os': os_gspn, 'step': 'Processo concluído', 'status': 'failed', 'error': 'Erro desconhecido', 'sid': sid})
    except Exception as e:
        print(f"Exceção capturada: {str(e)}")
        queue.put({'os': os_gspn, 'step': 'Erro geral', 'status': 'failed', 'error': str(e), 'sid': sid})
    finally:
        with lock:
            print(f"Estado de os_em_processamento no finally: {os_em_processamento}")
            if os_gspn in os_em_processamento:
                os_em_processamento.remove(os_gspn)
                print(f"OS {os_gspn} removida da fila")
            else:
                print(f"OS {os_gspn} NÃO está em os_em_processamento no finally")
        if driver:
            driver.quit()
        print(f"Processo para OS {os_gspn} concluído")

@app.route('/')
def index():
    return render_template('sincronizar_pecas.html')

@app.route('/submit_os', methods=['POST'])
def submit_os():
    data = request.get_json()
    os_gspn = data.get('os_gspn')
    sid = session.get('sid')
    if not os_gspn:
        return jsonify({'status': 'error', 'message': 'OS não fornecida'}), 400
    with lock:
        print(f"Estado de os_em_processamento antes de adicionar: {os_em_processamento}")
        if os_gspn in os_em_processamento:
            return jsonify({'status': 'error', 'message': f'OS {os_gspn} já está sendo processada'}), 409
        os_em_processamento.add(os_gspn)
        print(f"OS {os_gspn} adicionada a os_em_processamento: {os_em_processamento}")
    p = Process(target=processar_os, args=(os_gspn, sid, progress_queue))
    print(f"Iniciando processo para OS {os_gspn}")
    p.start()
    return jsonify({'status': 'success', 'message': f'OS {os_gspn} enviada para processamento'})

@app.route('/status', methods=['GET'])
def status():
    with lock:
        em_processamento = list(os_em_processamento)
    return jsonify({'em_processamento': em_processamento})

@socketio.on('connect')
def handle_connect():
    session['sid'] = request.sid
    print(f"Cliente conectado: {request.sid}")

def progress_listener():
    while True:
        message = progress_queue.get()
        print(f"Mensagem recebida da fila: {message}")
        if 'sid' in message and 'os' in message:
            socketio.emit('progress', {
                'os': message['os'],
                'step': message['step'],
                'status': message['status'],
                'error': message.get('error', '')
            }, room=message['sid'])

if __name__ == '__main__':
    capturar_todos_cookies()
    threading.Thread(target=progress_listener, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)