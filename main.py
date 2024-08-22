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


def validar_cpf(cpf_enviado):
    
    nove_digitos = cpf_enviado[:9]
    contador_regressivo_1 = 10

    resultado_digito_1 = 0
    for digito in nove_digitos:
        resultado_digito_1 += int(digito) * contador_regressivo_1
        contador_regressivo_1 -= 1
    digito_1 = (resultado_digito_1 * 10) % 11
    digito_1 = digito_1 if digito_1 <= 9 else 0

    dez_digitos = nove_digitos + str(digito_1)
    contador_regressivo_2 = 11

    resultado_digito_2 = 0
    for digito in dez_digitos:
        resultado_digito_2 += int(digito) * contador_regressivo_2
        contador_regressivo_2 -= 1
    digito_2 = (resultado_digito_2 * 10) % 11
    digito_2 = digito_2 if digito_2 <= 9 else 0

    cpf_gerado_pelo_calculo = f'{nove_digitos}{digito_1}{digito_2}'

    if cpf_enviado_usuario == cpf_gerado_pelo_calculo:
        print(f'{cpf_enviado_usuario} é válido')
    else:
        print('CPF inválido')
    
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
        # Tenta converter a string para um objeto datetime com o formato HH:MM
        datetime.strptime(hora, '%H:%M')
        return True
    except ValueError:
        return False


ex_dict = {
    "nome_usuario": "lucas",
    "senha_usuario": "12312",
    "email_usuario": "lucas_sbn@outlook.com",
    "cpf_usuario": 11876787406,
    "tipo_usuario": "cliente" #cliente ou barbeiro
}


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



ex_dict_agendamento = {
    "data": "05/09",
    "nome": "Lucas",
    "hora": "12:00",
    "descricao": "Corte americano"
}

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
    
    print(func_corte_disp)
    status = func_corte_disp.get("status")
    print(status, primeira_data_recebida)
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
    
    if not validar_hora(hora_agendamento):
        return jsonify({
            "error": "Formato de hora inválido [HH:MM]",
            "hora_invalida": hora_agendamento
        }), 400

 
    return jsonify({
        "message": "Adicionando ao banco de dados...",
        "add_bd": bd.add_agendamento(data_recebida, nome_agendamento, hora_agendamento, descricao_agendamento, status_agendamento)
        }), 200




    






if __name__ == '__main__':
    app.run(app.run(debug=True, threaded=True, host='0.0.0.0', port=8000))