const fs = require('fs');
const wppconnect = require('@wppconnect-team/wppconnect');

const AUTHORIZED_USER_ID = '558198659687@c.us'; // ID do usuário autorizado

wppconnect
  .create({
    session: 'sessionName',
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

  function start(client) {
    client.onMessage((message) => {
      console.log(message.from, "////", AUTHORIZED_USER_ID)
      if (message.from === AUTHORIZED_USER_ID) {
        // Verifica se a mensagem é de texto
        if (message.body) {
          console.log('Mensagem recebida: ', message.body);

          // Verifica se o corpo da mensagem contém 'pix'
          if (message.body.toLowerCase().includes('pix')) {
            client
              .sendText(message.from, 'Manda a chave, vou te mandar 200')
              .then((result) => {
                console.log('Resultado: ', result); // Sucesso
              })
              .catch((erro) => {
                console.error('Erro ao enviar: ', erro); // Erro
              });
          }
        } else {
          // Resposta se não for texto
          client
            .sendText(message.from, 'Sua mensagem não foi do tipo texto')
            .then((result) => {
              console.log('Resultado: ', result); // Sucesso
            })
            .catch((erro) => {
              console.error('Erro ao enviar: ', erro); // Erro
            });
        }
      } else {
        client
          .sendText(message.from, 'Você não está autorizado a enviar mensagens para este bot.')
          .then((result) => {
            console.log('Resultado ao enviar mensagem a usuário não autorizado: ', result); // Mostra o resultado da operação
          })
          .catch((erro) => {
            console.error('Erro ao enviar mensagem a usuário não autorizado: ', erro); // Mostra o erro
          });
      }
    });
  }
