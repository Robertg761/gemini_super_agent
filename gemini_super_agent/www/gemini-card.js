class GeminiCard extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this._conversationId = config.conversation_id || "default";
    this._maxMessages = config.max_messages || 10;
    this._messages = [];
  }

  connectedCallback() {
    this.innerHTML = `
      <ha-card header="Gemini Super Agent">
        <div class="card-content">
          <div id="conversation" class="conversation"></div>
          <div class="input-container">
            <ha-textfield
              id="user-input"
              label="Ask something..."
              outlined
            ></ha-textfield>
            <mwc-button id="send-button">Send</mwc-button>
          </div>
        </div>
      </ha-card>
    `;

    this._conversationDiv = this.querySelector("#conversation");
    this._userInput = this.querySelector("#user-input");
    this._sendButton = this.querySelector("#send-button");

    this._sendButton.addEventListener("click", () => this._sendMessage());
    this._userInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") this._sendMessage();
    });

    // Listen for responses
    this._hassConnection = new EventSource("/api/stream");
    this._hassConnection.addEventListener("message", (event) => {
      const data = JSON.parse(event.data);
      if (data.event_type === "gemini_super_agent_response" && 
          data.data.conversation_id === this._conversationId) {
        this._addMessage("assistant", data.data.response);
      }
    });
  }

  _sendMessage() {
    const text = this._userInput.value.trim();
    if (!text) return;

    this._addMessage("user", text);
    this._userInput.value = "";

    this._hass.callService("gemini_super_agent", "process_request", {
      text: text,
      conversation_id: this._conversationId
    });
  }

  _addMessage(role, text) {
    this._messages.push({ role, text });
    if (this._messages.length > this._maxMessages) {
      this._messages.shift();
    }

    this._updateConversation();
  }

  _updateConversation() {
    this._conversationDiv.innerHTML = this._messages.map(msg => `
      <div class="message ${msg.role}">
        <div class="message-content">${this._formatMessage(msg.text)}</div>
      </div>
    `).join("");
    this._conversationDiv.scrollTop = this._conversationDiv.scrollHeight;
  }

  _formatMessage(text) {
    // Simple formatting for code blocks
    return text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  }

  get hass() {
    return this._hass;
  }

  set hass(hass) {
    this._hass = hass;
  }
}

customElements.define("gemini-card", GeminiCard);