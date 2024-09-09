const fs = require('fs');
const wppconnect = require('@wppconnect-team/wppconnect');

const AUTHORIZED_USER_ID = '558198659687@c.us'; // ID do usuário autorizado
const axios = require('axios');


wppconnect
  .create({
    session: 'meu_celular',
    catchQR: (base64Qr, asciiQR) => {
      console.log(asciiQR); // Opcional: log do QR no terminal
      const matches = base64Qr.match(/^data:([A-Za-z-+\/]+);base64,(.+)$/);
      if (matches && matches.length === 3) {
        const response = {
          type: matches[1],
          data: Buffer.from(matches[2], 'base64')
        };

        fs.writeFile('out.png', response.data, 'binary', (err) => {
          if (err) {
            console.log(err);
          }
        });
      } else {
        console.error('Invalid QR data');
      }
    },
    logQR: false,
  })
  .then((client) => start(client))
  .catch((error) => console.error('Erro ao iniciar WPPConnect: ', error));

  async function obterHorariosDisponiveis(data) {
    const token = '415a85b9c3fc0af8bf051c9a77ee8ab4';
  
    try {
        const response = await axios.get('http://127.0.0.1:8000/ver_horarios_disponiveis', 
        {
            headers: {
                'Authorization': token,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            params: {
                data: data
            }
        });
  
        console.log('Resposta da API:', response.data);
        return response.data;
    } catch (error) {
        console.error('Erro ao obter horários disponíveis:', error);
    }
  }

  function start(client) {
      console.log('Cliente WPPConnect iniciado com sucesso!');
      
      obterHorariosDisponiveis('20/06').then((dados) => {
          if (dados) {
              // Converte o objeto para uma string JSON
              const jsonString = JSON.stringify(dados);
              
              // Converte a string JSON de volta para um objeto
              const dadosObj = JSON.parse(jsonString);
              
              // Constrói a mensagem iterando sobre o objeto
              let mensagem = 'Horários disponíveis:\n';
              if (dadosObj.data) {
                  mensagem += `Data: ${dadosObj.data}\n\n`;
              }
              if (Array.isArray(dadosObj.horarios_disponiveis)) {
                  mensagem += dadosObj.horarios_disponiveis.map(horario => `- ${horario}`).join('\n');
              } else {
                  console.error('Formato inesperado para horários_disponiveis:', dadosObj.horarios_disponiveis);
                  mensagem += 'Formato inesperado para horários disponíveis.';
              }
              
              console.log('Enviando mensagem:', mensagem);
              
              client.sendText(AUTHORIZED_USER_ID, mensagem)
                  .then(() => console.log('Mensagem enviada com sucesso!'))
                  .catch((error) => console.error('Erro ao enviar mensagem:', error));
          } else {
              console.log('Nenhum dado disponível para enviar.');
          }
      }).catch((error) => console.error('Erro ao obter horários disponíveis:', error));
  }