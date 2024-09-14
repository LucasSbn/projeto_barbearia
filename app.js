const axios = require('axios');
const express = require('express');
const app = express();
const port = 3000;

// Função para testar a conexão com o servidor WPPConnect
async function testServerConnection() {
  try {
    const response = await axios.get('http://localhost:21465/api/session/all-new-messages', {
      headers: {
        'Authorization': 'Bearer $2b$10$MfgziwWxF8msRGgA1z1E_OHJdeyUd9rO0bzhBc7PRaBzNjKjZutSm' // Substitua pelo token real
      }
    });
    console.log('Servidor WPPConnect está ativo:', response.data);
  } catch (error) {
    console.error('Erro ao conectar ao servidor WPPConnect:', error.message);
  }
}

// Middleware para analisar o corpo da solicitação como JSON
app.use(express.json());

// Endpoint para enviar uma mensagem
app.post('/api/session/send-message', async (req, res) => {
  const messageData = req.body;
  console.log('Mensagem recebida:', messageData);

  // Dados da mensagem a ser enviada
  const dataToSend = {
    phone: messageData.phone || '5521999999999',
    isGroup: messageData.isGroup || false,
    isNewsletter: messageData.isNewsletter || false,
    message: messageData.message || 'Hi from WPPConnect'
  };

  console.log('Dados a serem enviados:', dataToSend);

  // Enviar os dados da mensagem para o servidor WPPConnect
  try {
    const response = await axios.post('http://localhost:21465/api/session/send-message', dataToSend, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $2b$10$MfgziwWxF8msRGgA1z1E_OHJdeyUd9rO0bzhBc7PRaBzNjKjZutSm' // Substitua pelo token real
      }
    });
    console.log('Resposta do servidor WPPConnect:', response.data);
    res.status(200).send('Mensagem enviada para o servidor WPPConnect');
  } catch (error) {
    console.error('Erro ao enviar para o servidor WPPConnect:', error.message);
    res.status(500).send('Erro ao enviar para o servidor WPPConnect');
  }
});

app.listen(port, () => {
  console.log(`Servidor ouvindo na porta ${port}`);
});