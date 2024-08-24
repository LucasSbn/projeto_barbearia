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
        # if parametros():
        comando = '''
            INSERT INTO tb_agendamento (data, nome, hora, descricao, status)
            VALUES (%s, %s, %s, %s, %s)
        '''
        cursor.execute(comando, parametros)
        conexao.commit()


    except mysql.connector.Error as err:
        return f"Erro: {err}"
    
    finally:
        cursor.close()
        conexao.close()

    return "Dados inseridos com sucesso!"

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


# funcao para ver horario disponivel\
# primeiro, verificar o horário disponível

#lista para fazer a verificacao
horarios = [f"{hora}:{minuto:02d}" for hora in range(8, 22) for minuto in (0, 30)]
horarios.pop()

def ver_horario_disp(param_data, param_hora):
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='0511',
            database='bd_barbearia'
        )
        cursor = conexao.cursor()
    

        query = "SELECT data, hora FROM tb_agendamento"

        cursor.execute(query)

        resultados = cursor.fetchall()

        formatted_results = []
        for data, hora in resultados:
            data_str = data.strftime('%d/%m')
            if isinstance(hora, timedelta):
                total_seconds = int(hora.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                hora_str = f"{hours:02}:{minutes:02}"
            else:
                hora_str = str(hora)
                  
            formatted_results.append(f"{data_str} - {hora_str}")
        
        for list_horario in formatted_results:
            if list_horario in horarios:
                horarios.remove(list_horario)


        param_concatenado = f'{param_data} - {param_hora}'
        
        if param_concatenado in formatted_results:
            return {"status": 400, "message": "Horário indisponível"}
        else:
            return {"status": 200, "message": "Horário disponível"}
        


    except mysql.connector.Error as err:
        return f"Erro: {err}"
    
    finally:
        cursor.close()
        conexao.close()
        