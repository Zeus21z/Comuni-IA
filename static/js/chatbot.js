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

  // PUSH MENSAJE (AHORA USA innerHTML PARA HTML)
  const pushMsg = (html, who = 'bot') => {
    const div = document.createElement('div');
    div.className = who === 'user' ? 'msg-user' : 'msg-bot';
    div.innerHTML = html;  // ← AQUÍ ESTÁ EL CAMBIO CLAVE
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
    return div;
  };

  // ENVIAR
  const ask = async () => {
    const text = (input.value || '').trim();
    if(!text) return;

    pushMsg(text.replace(/\n/g, '<br>'), 'user');
    input.value = '';
    const thinking = pushMsg('Pensando...', 'bot');

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
        'Sin respuesta';
    } catch(e) {
      thinking.innerHTML = 'Error de conexión';
    }
  };

  // EVENTOS
  send?.addEventListener('click', ask);
  input?.addEventListener('keydown', (e) => {
    if(e.key === 'Enter') ask();
  });

  // ESCAPE
  document.addEventListener('keypress', (e) => {
    if(e.key === 'Escape' && panel.style.display === 'flex') {
      panel.style.display = 'none';
    }
  });

  // MENSAJE DE BIENVENIDA CON PERSONALIDAD
  setTimeout(() => {
    pushMsg(`
      <div style="text-align:center; padding:12px; background:#e3f2fd; border-radius:12px; margin:8px 0;">
        <strong>¡Hola! Soy <span style="color:#1976d2">GuIA</span></strong><br>
        <small>Tu asistente de compras en Santa Cruz</small>
      </div>
      <div style="font-size:0.9em; color:#555;">
        Dime qué necesitas: <strong>laptop, comida, ropa...</strong><br>
        ¡Te lo encuentro al toque!
      </div>
    `, 'bot');
  }, 800);

})();