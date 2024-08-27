import bd
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

key = '05092006!'


def validar_data(data):
    try:
        data_dividida = data.split('/')
        if len(data_dividida[0]) != 2 or len(data_dividida[1]) != 2:
            print(data_dividida, "Data no formato errado")
            return False
        
        dia, mes = data_dividida
        ano_atual = datetime.now().year
        data_completa = f"{ano_atual}-{mes.zfill(2)}-{dia.zfill(2)}"

        datetime.strptime(data_completa, '%Y-%m-%d')
        return True

    except ValueError:
        return False

    
def validar_hora(hora):
    try:
        if len(hora) != 5:
            return False

        datetime.strptime(hora, '%H:%M')
        return True
    except ValueError:
        return False
    
def horario_permitido(hora):

    horarios = [
    '08:00', '08:40', '09:20', '10:00', '10:40', '11:20', '12:00', '12:40', '13:20',
    '14:00', '14:40', '15:20', '16:00', '16:40', '17:20', '18:00', '18:40', '19:20',
    '20:00', '20:40', '21:20', '22:00'
    ]

    if hora not in horarios:
        return False
    return True



# ex_dict = {
#     "nome_usuario": "lucas",
#     "senha_usuario": "12312",
#     "email_usuario": "lucas_sbn@outlook.com",
#     "cpf_usuario": 11876787406,
#     "tipo_usuario": "cliente" #cliente ou barbeiro
# }


# --nome,senha, email, cpf(opcional para usuario), tipo 
@app.route('/add_user', methods=['POST'])
def add_user():
    dados = request.get_json()

    nome_usuario = dados.get('nome_usuario')
    senha_usuario = dados.get('senha_usuario')
    email_usuario = dados.get('email_usuario')
    tipo_usuario = dados.get('tipo_usuario')
    cpf_usuario = dados.get('cpf_usuario')

    campos_necessarios = ['nome_usuario', 'senha_usuario', 'email_usuario', 'tipo_usuario', 'cpf_usuario']
    campos_ausentes = [campo for campo in campos_necessarios if dados.get(campo) is None]

    if campos_ausentes:
        return jsonify({
            "error": "Dados ausentes",
            "campos_ausentes": campos_ausentes
        }), 400

    # Convertendo para string e verificando se todos os campos são strings
    nome_usuario = str(nome_usuario) if nome_usuario is not None else ""
    senha_usuario = str(senha_usuario) if senha_usuario is not None else ""
    email_usuario = str(email_usuario) if email_usuario is not None else ""
    tipo_usuario = str(tipo_usuario) if tipo_usuario is not None else ""
    cpf_usuario = str(cpf_usuario) if cpf_usuario is not None else ""

    if not all(isinstance(campo, str) for campo in [nome_usuario, senha_usuario, email_usuario, tipo_usuario, cpf_usuario]):
        return jsonify({
            "error": "Todos os campos devem ser strings", 
            "tipos": {
                "nome_usuario": type(nome_usuario).__name__,
                "senha_usuario": type(senha_usuario).__name__,
                "email_usuario": type(email_usuario).__name__,
                "tipo_usuario": type(tipo_usuario).__name__,
                "cpf_usuario": type(cpf_usuario).__name__,
            }
        }), 400

    if tipo_usuario.lower() == "barbeiro" and not cpf_usuario:
        return jsonify({
                "error": "CPF necessário para barbeiros"
            }), 400

    return jsonify({
        "message": "Adicionando ao banco de dados...",
        "add_bd": bd.client_user(nome_usuario, senha_usuario, email_usuario, tipo_usuario, cpf_usuario),
        "update": "Adicionado com sucesso!"
    }), 200




# ex_dict_agendamento = {
#     "data": "05/09",
#     "nome": "Lucas",
#     "hora": "12:00",
#     "descricao": "Corte americano"
# }


# agendamentos
# -- data e hora, id do barbeiro, id do usuário, status

from datetime import datetime, timedelta

@app.route('/add_agendamento', methods=['POST'])
def add_agendamento():
    dados = request.get_json()

    primeira_data_recebida = dados.get('data')
    nome_agendamento = dados.get('nome')
    hora_agendamento = dados.get('hora')
    descricao_agendamento = dados.get('descricao')
    status_agendamento = dados.get('status', 'P')  # P = pendente, C = cancelado, F = finalizado, I = iniciado
    ano_atual = datetime.now().year

    campos_necessarios = ['data', 'nome', 'hora', 'descricao']
    campos_ausentes = [campo for campo in campos_necessarios if dados.get(campo) is None]

    if campos_ausentes:
        return jsonify({
            "error": "Dados ausentes",
            "campos_ausentes": campos_ausentes
        }), 400

    if not validar_data(primeira_data_recebida):
        return jsonify({
            "error": "Formato de data inválido [DD/MM]",
            "data_invalida": primeira_data_recebida
        }), 400

    # Verifica se a data está dentro dos próximos 2 meses
    dia, mes = primeira_data_recebida.split('/')
    data_agendada = datetime.strptime(f"{dia}/{mes}/{ano_atual}", '%d/%m/%Y')
    
    data_atual = datetime.now()
    
    if data_agendada < data_atual:
        data_agendada = datetime.strptime(f"{dia}/{mes}/{ano_atual + 1}", '%d/%m/%Y')
    
    data_limite = data_atual + timedelta(days=60)

    if not (data_atual <= data_agendada <= data_limite):
        return jsonify({
            "error": f"A data de agendamento deve estar entre {data_atual.strftime('%d/%m/%Y')} e {data_limite.strftime('%d/%m/%Y')}."
        }), 400

    if not horario_permitido(hora_agendamento):
        return jsonify({
            "error": "Horário indisponível",
            "horario_invalido": hora_agendamento
        }), 400

    if not validar_hora(hora_agendamento):
        return jsonify({
            "error": "Formato de hora inválido [HH:MM]",
            "hora_invalida": hora_agendamento
        }), 400

    func_corte_disp = bd.verificar_horarios_disponivel(hora_agendamento, primeira_data_recebida)
    if func_corte_disp.get("status") == 400:
        return jsonify({
            "message": "Horário indisponível"
        }), 400

    data_recebida = data_agendada.strftime('%Y-%m-%d')
    bd.add_agendamento(data_recebida, nome_agendamento, hora_agendamento, descricao_agendamento, status_agendamento)

    return jsonify({
        "message": "Agendamento adicionado com sucesso!",
    }), 200



# ex_dict_verHorarioDisp = {
#     "data": "03/01",
#     "hora": "09:30"
# }

@app.route('/ver_horarios_disponiveis', methods=['GET'])
def verificar_horarios_disponiveis():
    dados = request.get_json()
    data_recebida = dados.get('data')

    # Verifica se a data foi fornecida corretamente
    if not data_recebida:
        return jsonify({"error": "Data não fornecida"}), 400

    # Consulta os horários disponíveis no banco de dados
    horarios_disponiveis = bd.ver_horarios_disponiveis(data_recebida)
    
    return jsonify(horarios_disponiveis)




# ex_dict_deletar_agendamento ={
#     "id_agendamento": 18
# }

@app.route('/deletar_agendamento', methods=['DELETE'])
def deletar_agendamento():
    try:
        dados = request.get_json()
        id_agendamento = dados.get('id_agendamento')
        
        if id_agendamento:
            
            resposta, status_code = bd.deletar_por_id(id_agendamento)
            return jsonify(resposta), status_code
        else:
            return jsonify({"status": 400, "message": "Id do agendamento não fornecido"}), 400
    
    except TypeError:
        return jsonify({"status": 500, "message": "Erro de tipo ocorrido"}), 500
    except Exception as e:
        return jsonify({"status": 500, "message": f"Erro ao deletar: {str(e)}"}), 500

@app.route('/cortes_do_dia', methods=['POST'])
def cortes_do_dia():
    try:
        dados = request.get_json()
    except json.JSONDecodeError:
        return jsonify({"error": "Falha ao decodificar JSON. Verifique o formato dos dados."}), 400
    
    if not dados or 'data' not in dados:
        return jsonify({"error": "Data não fornecida"}), 400
    
    data_recebida = dados.get('data')
    
    try:
        quantidade_cortes = bd.cortes_executados_dia(data_recebida)
    except Exception as e:
        return jsonify({"error": f"Erro no servidor: {str(e)}"}), 500
    
    if quantidade_cortes == 0:
        return jsonify({"message": "Nenhum corte executado para essa data"}), 404

    return jsonify({
        "Quantidade de cortes": quantidade_cortes
    }), 200

        
if __name__ == '__main__':
    app.run(app.run(debug=True, threaded=True, host='0.0.0.0', port=8000))