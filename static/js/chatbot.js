(function(){
  // ELEMENTOS
  const btn = document.getElementById('chatbot-toggle');
  const panel = document.getElementById('chatbot-panel');
  const msgs = document.getElementById('chatbot-messages');
  const input = document.getElementById('chatbot-text');
  const send = document.getElementById('chatbot-send');

  if(!btn || !panel) return;

  // TOGGLE PANEL
  btn.addEventListener('click', () => {
    const isVisible = panel.style.display === 'flex';
    panel.style.display = isVisible ? 'none' : 'flex';
    if(!isVisible) input?.focus();
  });

  // CERRAR CON X
  panel.querySelector('.btn-close')?.addEventListener('click', () => {
    panel.style.display = 'none';
  });

  // PUSH MENSAJE
  const pushMsg = (text, who='bot') => {
    const div = document.createElement('div');
    div.className = who === 'user' ? 'msg-user' : 'msg-bot';
    div.textContent = text;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
    return div;
  };

  // ENVIAR
  const ask = async () => {
    const text = (input.value || '').trim();
    if(!text) return;

    pushMsg(text, 'user');
    input.value = '';
    const thinking = pushMsg('🤔 Pensando...', 'bot');

    try {
      const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: text})
      });
      const data = await resp.json();
      
      thinking.className = 'msg-bot';
      thinking.innerHTML = data.reply ? 
        data.reply.replace(/\n/g, '<br>') : 
        '❌ Sin respuesta';
    } catch(e) {
      thinking.innerHTML = '🌐 Error de conexión';
    }
  };

  // EVENTOS
  send?.addEventListener('click', ask);
  input?.addEventListener('keydown', (e) => {
    if(e.key === 'Enter') ask();
  });

  // ESCAPE
  document.addEventListener('keydown', (e) => {
    if(e.key === 'Escape' && panel.style.display === 'flex') {
      panel.style.display = 'none';
    }
  });
})();