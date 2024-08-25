import mysql.connector
import bcrypt
from datetime import datetime, timedelta

def client_user(name_user, pass_user, mail_user, type_user, cpf_user=None):
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='0511',
            database='bd_barbearia'
        )
        cursor = conexao.cursor()
        
        comando = f'SELECT * FROM tb_usuario'
        cursor.execute(comando)
        cursor.fetchall()


        hash_senha = bcrypt.hashpw(pass_user.encode('utf-8'), bcrypt.gensalt())

        if cpf_user:
            comando = '''
                INSERT INTO tb_usuario (nome_usuario, senha_usuario, email_usuario, tipo_usuario, cpf_usuario)
                VALUES (%s, %s, %s, %s, %s)
            '''
            parametros = (name_user, hash_senha, mail_user, type_user, cpf_user)
        else:
            comando = '''
                INSERT INTO tb_usuario (nome_usuario, senha_usuario, email_usuario, tipo_usuario)
                VALUES (%s, %s, %s, %s)
            '''
            parametros = (name_user, hash_senha, mail_user, type_user)
        
        cursor.execute(comando, parametros)
        conexao.commit()
        
    except mysql.connector.Error as err:
        return f"Erro: {err}"
    
    finally:
        cursor.close()
        conexao.close()

    
    return "Dados inseridos com sucesso"

def chamar_id(data_agendamento, hora_agendamento):
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='0511',
            database='bd_barbearia'
        )
        cursor = conexao.cursor()

        comando = f'SELECT id FROM tb_agendamento WHERE data = "{data_agendamento}" AND hora = "{hora_agendamento}"'
        cursor.execute(comando)
        resultado = cursor.fetchall()
        resultado = resultado[0][0]

    except mysql.connector.errors.ProgrammingError as e:
        return {
            "message": "o horario deve ser em formato de [HH:MM]",
        }, 403
    
    finally:
        cursor.close()
        conexao.close

    
    if resultado:
        return resultado
    else: 
        return {
            "message": "agendamento não encontrado"
        }, 400

# print(chamar_id('andre das novinha', '23:00'))

def add_agendamento(data_agendamento, nome_agendamento, hora_agendamento, descricao_agendamento, status_agendamento):
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='0511',
            database='bd_barbearia'
        )
        cursor = conexao.cursor()

        comando = f'SELECT * FROM tb_agendamento'
        cursor.execute(comando)
        cursor.fetchall()

        parametros = (data_agendamento, nome_agendamento, hora_agendamento, descricao_agendamento, status_agendamento)

        comando = '''
            INSERT INTO tb_agendamento (data, nome, hora, descricao, status)
            VALUES (%s, %s, %s, %s, %s)
        '''
        cursor.execute(comando, parametros)
        conexao.commit()

        # chamar_id(nome_agendamento, hora_agendamento)


    except mysql.connector.Error as err:
        return f"Erro: {err}"
    
    finally:
        cursor.close()
        conexao.close()

    return {
        "message": "Dados inseridos com sucesso!",
        "id": f"o id deste corte é: {chamar_id(data_agendamento, hora_agendamento)}"
    }, 200

def verificar_horarios_disponivel(param_hora, param_date):
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='0511',
        database='bd_barbearia'
    )
    cursor = conexao.cursor()

    comando_select_agendamentos = """
        SELECT DATE_FORMAT(data, '%d/%m') AS data_formatada, 
               DATE_FORMAT(hora, '%H:%i') AS horario 
        FROM tb_agendamento;
    """
    cursor.execute(comando_select_agendamentos)
    resultados = cursor.fetchall()

    agendamentos = [(data, hora) for data, hora in resultados]

    for data, hora in agendamentos:
        if param_date == data and param_hora == hora:
            return {"status": 400}

    return {"status": 200}

horarios = [
    '08:00', '08:40', '09:20', '10:00', '10:40', '11:20', '12:00', '12:40', '13:20',
    '14:00', '14:40', '15:20', '16:00', '16:40', '17:20', '18:00', '18:40', '19:20',
    '20:00', '20:40', '21:20', '21:40'
    ]

def ver_horarios_disponiveis(param_data):
    try:
        ano_atual = datetime.now().year
        data_formatada = datetime.strptime(f"{param_data}/{ano_atual}", '%d/%m/%Y').strftime('%Y-%m-%d')

        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='0511',
            database='bd_barbearia'
        )
        cursor = conexao.cursor()

        query = "SELECT hora FROM tb_agendamento WHERE data = %s"
        cursor.execute(query, (data_formatada,))
        resultados = cursor.fetchall()

        horarios_ocupados = []
        for (hora,) in resultados:
            if isinstance(hora, timedelta):
                total_seconds = int(hora.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                hora_str = f"{hours:02}:{minutes:02}"
            else:
                hora_str = str(hora)
            horarios_ocupados.append(hora_str)

        horarios_totais = [
        '08:00', '08:40', '09:20', '10:00', '10:40', '11:20', '12:00', '12:40', '13:20',
        '14:00', '14:40', '15:20', '16:00', '16:40', '17:20', '18:00', '18:40', '19:20',
        '20:00', '20:40', '21:20', '22:00'
        ]

        horarios_disponiveis = [horario for horario in horarios_totais if horario not in horarios_ocupados]
        
        return {
            "data": param_data,
            "horarios_disponiveis": horarios_disponiveis
        }

    except mysql.connector.Error as err:
        return f"Erro: {err}"
    
    finally:
        cursor.close()
        conexao.close()




def deletar_por_id(id_agendamento):
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='0511',
            database='bd_barbearia'
        )
        cursor = conexao.cursor()

        comando_verificar = 'SELECT id FROM tb_agendamento WHERE id = %s'
        cursor.execute(comando_verificar, (id_agendamento,))
        resultado = cursor.fetchone()

        if resultado:
            query_deletar = 'DELETE FROM tb_agendamento WHERE id = %s'
            cursor.execute(query_deletar, (id_agendamento,))
            conexao.commit()
            return {"status": 200, "message": "Agendamento deletado com sucesso"}, 200
        else:
            return {"status": 404, "message": "Agendamento não encontrado"}, 404

    except mysql.connector.Error as err:
        return {"status": 500, "message": f"Erro: {err}"}, 500
    finally:
        cursor.close()
        conexao.close()


mes_atual = datetime.now().month
print(mes_atual)