import bd
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime



# sistema de agendamento

# usuário (GET/POST/DELETE/UPDATE)
# babeiro (GET/POST/DELETE/UPDATE)



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

    campos_necessarios = ['nome_usuario', 'senha_usuario', 'email_usuario', 'tipo_usuario']
    campos_ausentes = [i for i in campos_necessarios if i not in dados]

    if campos_ausentes:
        return jsonify({
            "error": "Dados ausentes",
            "campos_ausentes": campos_ausentes
        }), 400

    if tipo_usuario.lower() == "barbeiro" and not cpf_usuario:
        return jsonify({
                "message": "CPF necessário para barbeiros"
            }), 400
    
    

    return jsonify({"message": "Adicionando ao banco de dados...",
                    "add_bd": (bd.client_user(nome_usuario, senha_usuario, email_usuario, tipo_usuario, cpf_usuario)),
                    "update": "Adicionado com sucesso!"
                    })



# ex_dict_agendamento = {
#     "data": "05/09",
#     "nome": "Lucas",
#     "hora": "12:00",
#     "descricao": "Corte americano"
# }

# agendamentos
# -- data e hora, id do barbeiro, id do usuário, status

@app.route('/add_agendamento', methods=['POST'])
def add_agendamento():
    dados = request.get_json()

    primeira_data_recebida = dados.get('data')
    nome_agendamento = dados.get('nome')
    hora_agendamento = dados.get('hora')
    descricao_agendamento = dados.get('descricao')
    status_agendamento = dados.get('status', 'P') # p = pendente // C = cancelado // F = finalizado // I = iniciado
    ano_atual = datetime.now().year

    data_recebida = primeira_data_recebida.split('/')
    dia = data_recebida[0]
    mes = data_recebida[1]

    data_recebida = str(ano_atual) + '-' + str(mes) + '-' + str(dia)

    campos_necessarios = ['data', 'nome', 'hora', 'descricao']
    campos_ausentes = [campo for campo in campos_necessarios if dados.get(campo) is None]


    func_corte_disp = bd.verificar_horarios_disponivel(hora_agendamento, primeira_data_recebida)
    
    status = func_corte_disp.get("status")
    if status:
        if func_corte_disp["status"] == 400:
            return jsonify({
                "message": "Horário indisponível"
                }), 400

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
    
    if not horario_permitido(hora_agendamento):
        return jsonify({
            "error": "Horário Indisponível",
            "horario_invalido": hora_agendamento
        }), 400

    if not validar_hora(hora_agendamento):
        return jsonify({
            "error": "Formato de hora inválido [HH:MM]",
            "hora_invalida": hora_agendamento
        }), 400

 
    return jsonify({
        "message": "Adicionando ao banco de dados...",
        "add_bd": bd.add_agendamento(data_recebida, nome_agendamento, hora_agendamento, descricao_agendamento, status_agendamento)
        }), 200


# ex_dict_verHorarioDisp = {
#     "data": "03/01",
#     "hora": "09:30"
# }

# @app.route('/ver_horario_disp', methods=['GET'])
# def veriricar_horarios_disponivel():
    
#     dados = request.get_json()
#     data_recebida = dados.get('data')
#     hora_recebida = dados.get('hora')

#     if not horario_permitido(hora_recebida):
#         return jsonify({
#             "error": "Horário inválido (horario deve terminar em [00 ou 30])",
#             "horario_invalido": hora_recebida
#         }), 400
    
#     resultado = bd.ver_horario_disp(data_recebida, hora_recebida)
#     bd.ver_horario_disp(data_recebida, hora_recebida)
#     return jsonify(resultado)

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

    






if __name__ == '__main__':
    app.run(app.run(debug=True, threaded=True, host='0.0.0.0', port=8000))
