import { useState } from 'react';
import DOMPurify from 'dompurify';
import { marked } from 'marked';
import { sendChatMessage } from '../services/chatService';
import { useAuth } from '../context/AuthContext';

export function renderMarkdownSafe(markdownText) {
  const html = marked.parse(markdownText || '');
  return DOMPurify.sanitize(html);
}

export function ChatUI() {
  const { user } = useAuth();
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([
    { user: 'system', assistant: '**Welcome** to the scheme assistant.' }
  ]);
  const [error, setError] = useState('');

  async function onSend() {
    if (!message.trim()) return;
    const nextHistory = messages.flatMap((entry) => [
      { role: 'user', content: entry.user },
      { role: 'assistant', content: entry.assistant }
    ]);

    try {
      const response = await sendChatMessage({
        message,
        history: nextHistory,
        userId: user?.id || null
      });
      const reply = response.reply || '';
      setMessages((current) => [...current, { user: message, assistant: reply }]);
      setMessage('');
      setError('');
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="card">
      <h2>ChatUI</h2>
      <div data-testid="chat-log">
        {messages.map((entry, idx) => (
          <div key={idx}>
            <p><strong>You:</strong> {entry.user}</p>
            <div
              data-testid="assistant-reply"
              dangerouslySetInnerHTML={{ __html: renderMarkdownSafe(entry.assistant) }}
            />
          </div>
        ))}
      </div>
      {error ? <p className="error">{error}</p> : null}
      <div className="row">
        <input
          data-testid="chat-input"
          placeholder="Ask about schemes"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              onSend();
            }
          }}
        />
        <button data-testid="chat-send" onClick={onSend}>Send</button>
      </div>
    </section>
  );
}
