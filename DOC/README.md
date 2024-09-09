# Projeto Barbearia

## Descrição

Este projeto é um sistema de agendamento para uma barbearia, desenvolvido em Python utilizando Flask e MySQL. O sistema permite que os clientes agendem horários para cortes de cabelo, e os funcionários podem gerenciar esses agendamentos, verificando os horários disponíveis e o número de cortes realizados em um dia específico.

## Funcionalidades

- Marcar horários para cortes de cabelo.
- Verificar horários disponíveis em uma data específica.
- Deletar agendamentos por ID.
- Visualizar o número de cortes realizados em um dia específico.

## Instalação

1. Clone o repositório:

   `git clone https://github.com/LucasSbn/projeto_barbearia.git`

2. Navegue até o diretório do projeto:

   `cd projeto_barbearia`

3. Instale as dependências: Certifique-se de que o Python está instalado em sua máquina e execute:

   `pip install -r requirements.txt`

4. Configuração do banco de dados:

   - Certifique-se de ter o MySQL instalado e configurado.
   - Crie um banco de dados para o sistema.
   - Atualize as configurações de conexão no arquivo `bd.py`.

5. Executando o servidor: Após instalar as dependências e configurar o banco de dados, execute o seguinte comando para iniciar o servidor Flask:

   `python main.py`

   O servidor será iniciado no localhost na porta 8000.

## Uso

- Para agendar um horário, utilize a rota `POST /agendar`, enviando a data e hora desejadas.
- Para deletar um agendamento, utilize a rota `DELETE /deletar_agendamento`, enviando um JSON com o campo `id_agendamento`.
- Para verificar os horários disponíveis de um dia específico, utilize a rota `GET /horarios_disponiveis`, enviando a data.
- Para obter o número de cortes realizados em um dia, utilize a rota `POST /cortes_do_dia`, passando a data.

## Exemplos

- Agendar um horário:

  **Rota:** `POST /agendar`
  
  **Corpo da requisição (exemplo):**
  
      
      {
          "data": "15/09",
          "hora": "14:00"
      }


- Verificar horários disponíveis:

  **Rota:** `GET /horarios_disponiveis`
  
  **Parâmetros:**
  
      {
          "data": "15/09"
      }

- Deletar um agendamento:

  **Rota:** `DELETE /deletar_agendamento`

  **Corpo da requisição:**

  ```json
  {
      "id_agendamento": "123"  // Substitua "123" pelo ID do agendamento que deseja excluir.
  }

- Obter o número de cortes do dia:

  **Rota:** `POST /cortes_do_dia`

  **Corpo da requisição:**

  ```json
  {
      "data": "15/09"
  }


## Licença

Este projeto está licenciado sob a [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).
