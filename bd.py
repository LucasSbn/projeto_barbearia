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

def cortes_executados_dia(param_data):
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='0511',
            database='bd_barbearia'
        )
        cursor = conexao.cursor()

        comando = """
        SELECT DATE_FORMAT(data, "%d/%m") AS data_formatada, status 
        FROM tb_agendamento
        WHERE status = 'F' AND DATE_FORMAT(data, "%d/%m") = %s;
        """

        query_verificar_horario = ...

        cursor.execute(comando, (param_data,))
        resultado = cursor.fetchall()

        return len(resultado)

    finally:
        cursor.close()
        conexao.close()

def resultado_horario(param_data):       
    resultado = ver_horarios_disponiveis(param_data)
    if isinstance(resultado, dict):
        horario_disponivel = resultado.get("horarios_disponiveis", [])
        return horario_disponivel
    

# colocar a funcao  como uma variavel e depois dar o nome da variavel.get() e puxar o que eu desejo
def att_status(status, param_data, param_hora):
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='0511',
            database='bd_barbearia'
            )
        cursor = conexao.cursor()
        
        param_data = param_data.replace('/', '-')
        ano_atual = datetime.now().year
        data_completa = f'{ano_atual}-{param_data}'
        data_sql = datetime.strptime(data_completa, '%Y-%d-%m').strftime('%Y-%m-%d')

        query = """ UPDATE tb_agendamento SET status = %s 
                    WHERE data = %s AND HORA = %s
                """
        cursor.execute(query, (status.upper(), data_sql, param_hora))
        conexao.commit()
        return {
            "sucesso": True,
            "status": 200
        }
    finally:
        cursor.close()
        conexao.close()
        
        
exemplo_dict = {
    'nome': 'Lucas',
    'idade': 30,
    'cidade': 'São Paulo',
    'profissao': 'Desenvolvedor',
    'ativo': True
}

def verificar_numero_respondido(numero):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="0511",
        database="bd_barbearia"
    )
    cursor = conn.cursor()
    
    query = "SELECT COUNT(*) FROM mensagens_respondidas WHERE numero = %s"
    cursor.execute(query, (numero,))
    resultado = cursor.fetchone()
    
    conn.close()
    
    return resultado[0] > 0  # Retorna True se o número já estiver no banco

def marcar_numero_respondido(numero):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='0511',
            database='bd_barbearia'
        )
        cursor = conn.cursor()
        data_resposta = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        modulo_atual = "1"
        
        query = "INSERT INTO mensagens_respondidas (numero, data_resposta, modulo_atual) VALUES (%s, %s, %s)"
        print(f"Inserindo número {numero}, data {data_resposta} e modulo atual {modulo_atual} no banco de dados.")
        cursor.execute(query, (numero, data_resposta, modulo_atual))
        conn.commit()

        print(f"Número {numero} foi inserido com sucesso no banco de dados.")
        
        conn.close()
    except mysql.connector.Error as err:
        print(f"Erro ao inserir no banco de dados: {str(err)}")
    except Exception as e:
        print(f"Erro inesperado ao salvar o número no banco: {str(e)}")


def remover_numero_inativo():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='0511',
            database='bd_barbearia'
        )
        cursor = conn.cursor()
        limite_tempo = datetime.now() - timedelta(minutes=1)
        
        query = "DELETE FROM mensagens_respondidas WHERE data_resposta < %s"
        cursor.execute(query, (limite_tempo.strftime('%Y-%m-%d %H:%M:%S'),))
        conn.commit()

        print(f"Números inativos foram removidos do banco de dados.")
        
        conn.close()
    except mysql.connector.Error as err:
        print(f"Erro ao remover números inativos no banco de dados: {str(err)}")
    except Exception as e:
        print(f"Erro inesperado ao remover números inativos no banco: {str(e)}")

# Para usar a função remover_numero_inativo, você pode chamá-la em um intervalo específico ou em momentos apropriados no seu código.

def obter_modulo_por_numero(numero):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="0511",
        database="bd_barbearia"
    )
    cursor = conn.cursor()

    query = "SELECT modulo_atual FROM mensagens_respondidas WHERE numero = %s"
    cursor.execute(query, (numero,))
    resultado = cursor.fetchone()
    
    conn.close()
    
    # Verifica se o resultado foi encontrado e retorna o modulo_atual
    if resultado:
        modulo_atual = resultado[0]
        return modulo_atual
    else:
        return None  # Caso não encontre o número na tabela

# Exemplo de uso
numero = '558197100205@c.us'
modulo_numero = obter_modulo_por_numero(numero)
print(modulo_numero)




def deletar_numeros_antigos():
    try:
        conn = mysql.connector.connect(
            host="localhost",  # Altere conforme sua configuração
            user="root",
            password="0511",
            database="bd_barbearia"
        )
        cursor = conn.cursor()
        
        # Calcula o tempo limite de 5 minutos atrás
        tempo_limite = datetime.now() - timedelta(minutes=1)
        tempo_limite_str = tempo_limite.strftime('%Y-%m-%d %H:%M:%S')
        
        # Deleta registros onde data_resposta é menor que o tempo limite
        query = "DELETE FROM mensagens_respondidas WHERE data_resposta < %s"
        cursor.execute(query, (tempo_limite_str,))
        
        # Commit para confirmar as alterações
        conn.commit()
        
        # Imprime a quantidade de registros deletados
        print(f"Números antigos deletados: {cursor.rowcount}")
        
        conn.close()

    except mysql.connector.Error as err:
        print(f"Erro ao deletar no banco de dados: {str(err)}")
    except Exception as e:
        print(f"Erro inesperado ao deletar no banco: {str(e)}")
