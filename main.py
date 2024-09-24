import bd
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import requests


# -> npm start
# -> session
# -> $2b$10$MfgziwWxF8msRGgA1z1E_OHJdeyUd9rO0bzhBc7PRaBzNjKjZutSm

app = Flask(__name__)
CORS(app)

def calcular_intervalo():
    hoje = datetime.now()
    inicio = hoje.replace(day=1)

    # Ajustar fim para incluir três meses, ao invés de dois
    if inicio.month == 11:  # Se for novembro, fim será em fevereiro do próximo ano
        fim = inicio.replace(year=inicio.year + 1, month=2, day=28)
    elif inicio.month == 12:  # Se for dezembro, fim será em março do próximo ano
        fim = inicio.replace(year=inicio.year + 1, month=3, day=31)
    else:
        # Adicionar 3 meses ao início
        fim = inicio.replace(month=(inicio.month % 12) + 3, day=1) - timedelta(days=1)

    return inicio.strftime("%d/%m/%Y"), fim.strftime("%d/%m/%Y")

def listar_domingos():
    inicio_str, fim_str = calcular_intervalo()
    inicio = datetime.strptime(inicio_str, "%d/%m/%Y")
    fim = datetime.strptime(fim_str, "%d/%m/%Y")
    dia_atual = inicio

    while dia_atual.weekday() != 6:
        dia_atual += timedelta(days=1)

    domingos = []
    while dia_atual <= fim:
        domingos.append(dia_atual.strftime("%d/%m"))
        dia_atual += timedelta(days=7)

    return domingos

lista_dias_domingo = listar_domingos()

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

    if primeira_data_recebida in lista_dias_domingo:
        return {
            "error": "Não é possível agendar no domingo"
        }

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
    # Obtém o parâmetro 'data' da URL (usando GET)
    data_recebida = request.args.get('data')

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

@app.route("/mudar_status", methods=['POST'])
def mudar_status():
    try:
        dados = request.get_json()
        param_hora = str(dados.get('hora'))
        param_status = str(dados.get('status'))
        param_data = str(dados.get('data'))

        if not validar_hora(param_hora):
            return jsonify({
                "error": "Formato de hora inválido [HH:MM]",
                "hora_invalida": param_hora
            }), 400

        if not validar_data(param_data):
            return jsonify({
                "error": "Formato de data inválido [DD/MM]",
                "data_invalida": param_data
            }), 400
        
        resultado = bd.resultado_horario(param_data)
        if param_hora in resultado:
            return jsonify({
                "message": "Este horario não está marcado",
                "status": 405
            }), 405
        
        if not horario_permitido(param_hora):
            return jsonify({
                "error": "Horário inválido",
                "horario_invalido": param_hora
            }), 403
        
        status_permitidos = ['P', 'C', 'F', 'I']
        if param_status.upper() not in status_permitidos:
            return {"status": 400, "message": "Status inválido"}, 400
        else:
            
            bd.att_status(param_status, param_data, param_hora)
            return {"status": 200, 
                    "message": "Status atualizado com sucesso"
                    }, 200
    
    except json.JSONDecodeError:
        return jsonify({
            "error": "Falha ao decodificar JSON. Verifique o formato dos dados."
        }), 400


@app.route('/falar_barbeiro', methods=["GET"])
def falar_barbeiro():
    try:
        dados = request.get_json()
        pergunta = str(dados.get("pergunta", ""))
        pergunta = pergunta.lower()
        url = 'http://localhost:21465/api/session/all-new-messages'
        response = requests.get(url)
        data_from_server_3 = response.json()

        print('Dados do Servidor 3:', data_from_server_3)
        horario = ["horario", "horário", "horarios", "horários"]
        preco = ["preço", "preco", "preços", "precos"]
        if any(word in pergunta for word in horario):
            return {"resposta": "Para ver os horário disponíveis, consute 'Ver horários disponíveis' e passe uma data "}, 200
        elif any(word in pergunta for word in preco):
            return {"resposta": "O corte custa R$25."}, 200
        else:
            return {"resposta": "Fale com o barbeiro. Numero: 998659687"}, 200
    except TypeError or AttributeError:
        return {"resposta": "ocorreu algum error durante o processo..."}
    
#so vai funcionar se eu usar essa requisicao no postman (testar se está funcionando o bot)
@app.route('/send-message', methods=["POST"])
def enviar_mensagem():
    url = "http://localhost:21465/api/session/send-message"
    headers = {
        "Authorization": "Bearer $2b$10$MfgziwWxF8msRGgA1z1E_OHJdeyUd9rO0bzhBc7PRaBzNjKjZutSm",
        "Content-Type": "application/json"
    }
    data = {
        "phone": "558198659687",
        "isGroup": False,
        "isNewsletter": False,
        "message": "bot funcionando!"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code in [200, 201, 202, 203, 204, 205]:
        print('Requisição bem-sucedida')
        return {"status": "success", "message": "Mensagem enviada com sucesso"}, 200
    else:
        return {
            "status": "fail", 
            "message": f"Erro ao enviar mensagem. Código de status: {response.status_code}. Detalhes: {response.text}"
        }, response.status_code


# Conjunto para armazenar os números que já receberam resposta
numeros_respondidos = set()

def enviar_ordem(numero):
    api_url = "http://localhost:21465/api/session/send-list-message"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer $2b$10$MfgziwWxF8msRGgA1z1E_OHJdeyUd9rO0bzhBc7PRaBzNjKjZutSm"
    }
    payload = {
        "phone": numero,
        "isGroup": False,
        "description": "Desc for list",
        "buttonText": "Select a option",
        "sections": [
                {
                "title": "Section 1",
                "rows": [
                    {
                    "rowId": "my_custom_id",
                    "title": "Test 1"
                    },
                    {
                    "rowId": "2",
                    "title": "Test 2"
                    }
                ]
                }
            ]
}
    response = requests.post(api_url, json=payload, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")

    return response.status_code, response.text


def enviar_resposta(numero, mensagem):
    api_url = "http://localhost:21465/api/session/send-message"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer $2b$10$MfgziwWxF8msRGgA1z1E_OHJdeyUd9rO0bzhBc7PRaBzNjKjZutSm"
    }
    payload = {
        "phone": numero,
        "message": mensagem,
        "isGroup": False
    }
    response = requests.post(api_url, json=payload, headers=headers)
    return response.status_code



def processar_mensagem(data):
    try:
        bd.deletar_numeros_antigos()
        # Verifica se o evento é 'onmessage'
        evento = data.get('event')
        if evento == 'onmessage':
            print("Evento de mensagem recebido.")
            # Verifica se 'sender' e 'id' estão presentes e válidos
            sender = data.get('sender', {})
            numero = sender.get('id') or data.get('from')

            if not numero:
                print("Dados do remetente inválidos ou faltando.")
                return None  # Interrompe o processamento da mensagem se não houver remetente válido

            print(f"Processando mensagem do número: {numero}")

            if not data.get('isGroupMsg', False):

                # Verifica se o número já foi respondido
                if bd.verificar_numero_respondido(numero):
                    print(f"Mensagem já enviada para o número {numero}. Ignorando.")
                    return  # Não envia a mensagem novamente

                # Marca o número como respondido no banco de dados
                bd.marcar_numero_respondido(numero)

            # Verifica se é uma mensagem de grupo
            if data.get('isGroupMsg', False):
                print("Mensagem ignorada: é uma mensagem de grupo.")
                return  # Ignora a mensagem de grupo

            # Envia uma resposta simples
            resposta = "Olá! Como posso ajudar?"
            status_resposta = enviar_resposta(numero, resposta)

            print(f"Status de resposta enviada para {numero}: {status_resposta}")

            # Envia a ordem (lista de opções)
            status_ordem, resposta_ordem = enviar_ordem(numero)
            print(f"Status do envio da ordem: {status_ordem}, Resposta: {resposta_ordem}")
            
            return status_resposta  # Retorna o status da resposta original
        else:
            # Evento não reconhecido
            print(f"Evento '{evento}' não é uma mensagem ou não foi reconhecido.")
            return None
    except Exception as e:
        print(f"Erro ao processar a mensagem: {str(e)}")
        return 500
modulo_1 = "/webhook/modulo-1"
@app.route(modulo_1, methods=['POST'])
def webhook():
    try:
        data = request.json
        if data.get('event') == 'onmessage':
            print(f"Dados recebidos no webhook: {data}")  # Para debug
            ...

        status = processar_mensagem(data)

        # Se o status for None, o evento não foi processado
        if status is None:
            return jsonify({'status': 'Evento ignorado'}), 200

        return jsonify({'status': 'Mensagem processada com sucesso'}), status or 200

    except KeyError as e:
        print(e)
        return jsonify({'status': 'Chave ausente no corpo da requisição', 'error': str(e)}), 400
    except Exception as e:
        print(e)
        return jsonify({'status': 'Erro ao processar a mensagem', 'error': str(e)}), 500



    
    '''
            {
                "event":"onmessage",
                "session":"session",
                "id":"false_558196701767@c.us_3AB4EB53229F1DCC4A7B",
                "viewed":false,
                "body":"Jajajs",
                "type":"chat",
                "t":1726872632,
                "notifyName":"Gilvando Xavier",
                "from":"558196701767@c.us",
                "to":"558198659687@c.us",
                "ack":1,
                "invis":false,
                "isNewMsg":true,
                "star":false,
                "kicNotified":false,
                "recvFresh":true,
                "isFromTemplate":false,
                "pollInvalidated":false,
                "isSentCagPollCreation":false,
                "latestEditMsgKey":"None",
                "latestEditSenderTimestampMs":"None",
                "mentionedJidList":[
                    
                ],
                "groupMentions":[
                    
                ],
                "isEventCanceled":false,
                "eventInvalidated":false,
                "isVcardOverMmsDocument":false,
                "isForwarded":false,
                "hasReaction":false,
                "messageSecret":{
                    "0":140,
                    "1":132,
                    "2":197,
                    "3":39,
                    "4":85,
                    "5":14,
                    "6":40,
                    "7":218,
                    "8":26,
                    "9":26,
                    "10":32,
                    "11":127,
                    "12":63,
                    "13":143,
                    "14":239,
                    "15":117,
                    "16":237,
                    "17":179,
                    "18":92,
                    "19":73,
                    "20":226,
                    "21":10,
                    "22":243,
                    "23":226,
                    "24":218,
                    "25":190,
                    "26":110,
                    "27":72,
                    "28":57,
                    "29":161,
                    "30":222,
                    "31":16
                },
                "productHeaderImageRejected":false,
                "lastPlaybackProgress":0,
                "isDynamicReplyButtonsMsg":false,
                "isCarouselCard":false,
                "parentMsgId":"None",
                "isMdHistoryMsg":false,
                "stickerSentTs":0,
                "isAvatar":false,
                "lastUpdateFromServerTs":0,
                "invokedBotWid":"None",
                "bizBotType":"None",
                "botResponseTargetId":"None",
                "botPluginType":"None",
                "botPluginReferenceIndex":"None",
                "botPluginSearchProvider":"None",
                "botPluginSearchUrl":"None",
                "botPluginSearchQuery":"None",
                "botPluginMaybeParent":false,
                "botReelPluginThumbnailCdnUrl":"None",
                "botMsgBodyType":"None",
                "requiresDirectConnection":"None",
                "bizContentPlaceholderType":"None",
                "hostedBizEncStateMismatch":false,
                "senderOrRecipientAccountTypeHosted":false,
                "placeholderCreatedWhenAccountIsHosted":false,
                "chatId":"558196701767@c.us",
                "fromMe":false,
                "sender":{
                    "id":"558196701767@c.us",
                    "name":"Gil",
                    "shortName":"Gil",
                    "pushname":"Gilvando Xavier",
                    "type":"in",
                    "isBusiness":false,
                    "isEnterprise":false,
                    "isSmb":false,
                    "isContactSyncCompleted":1,
                    "textStatusLastUpdateTime":-1,
                    "syncToAddressbook":true,
                    "formattedName":"Gil",
                    "isMe":false,
                    "isMyContact":true,
                    "isPSA":false,
                    "isUser":true,
                    "isWAContact":true,
                    "profilePicThumbObj":{
                        "id":"558196701767@c.us"
                    },
                    "msgs":"None"
                },
                "timestamp":1726872632,
                "content":"Jajajs",
                "isGroupMsg":false,
                "mediaData":{
                    
                }
                }
    '''



if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0', port=8000)



'''
conversas_ativas = {id: modulo_que_parou}
modulo = [
    {
       "modulo": 1,
       "id": numero,
       "proximo_modulo" : 2,  
    }
]
'''

                # data2 = {
                #     "phone": f"{celular}",
                #     "isGroup": False,
                #     "description": "ATENDIMENTO AO CLIENTE",
                #     "buttonText": "Escolha o que você deseja fazer",
                #     "sections": [
                #         {
                #         "title": "O QUE VOCÊ QUER?",
                #         "rows": [
                #             {
                #             "rowId": "1",
                #             "title": "Prosseguir com o atendimento.",
                #             "description": "Marcar cortes / Editar Horário / Apagar agendamento / Ver Cortes do dia"
                #             },
                #             {
                #             "rowId": "2",
                #             "title": "Falar com Bruno",
                #             "description": "Desejo resolver algo pessoal com bruno."
                #             }
                #         ]
                #         }
                #     ]
                #     }
                
                # requests.post(url3, headers=headers, data=json.dumps(data2))