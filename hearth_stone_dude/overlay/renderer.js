const statusEl = document.getElementById('status');
const gameStatusEl = document.getElementById('game-status');
const opponentSection = document.getElementById('opponent-section');
const friendlySection = document.getElementById('friendly-section');
const opponentHandEl = document.getElementById('opponent-hand');
const opponentDeckEl = document.getElementById('opponent-deck');
const opponentPlayedEl = document.getElementById('opponent-played');
const friendlyHandEl = document.getElementById('friendly-hand');

let ws;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function connect() {
  ws = new WebSocket('ws://localhost:8000/ws');
  
  ws.onopen = () => {
    console.log('Connected to server');
    statusEl.textContent = '已连接';
    statusEl.className = 'status connected';
    reconnectAttempts = 0;
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateUI(data);
  };
  
  ws.onclose = () => {
    console.log('Disconnected from server');
    statusEl.textContent = '已断开';
    statusEl.className = 'status disconnected';
    
    if (reconnectAttempts < maxReconnectAttempts) {
      reconnectAttempts++;
      console.log(`Reconnecting... (${reconnectAttempts}/${maxReconnectAttempts})`);
      setTimeout(connect, 2000);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
}

function updateUI(data) {
  if (!data.game_state || !data.game_state.is_in_game) {
    gameStatusEl.style.display = 'block';
    opponentSection.style.display = 'none';
    friendlySection.style.display = 'none';
    return;
  }
  
  gameStatusEl.style.display = 'none';
  opponentSection.style.display = 'block';
  friendlySection.style.display = 'block';
  
  opponentHandEl.textContent = data.opponent_hand_count || 0;
  opponentDeckEl.textContent = data.opponent_deck_count || 0;
  
  updateCardList(opponentPlayedEl, data.opponent_played_cards || []);
  updateCardList(friendlyHandEl, data.friendly_hand || []);
}

function updateCardList(container, cards) {
  container.innerHTML = '';
  cards.forEach(cardId => {
    const tag = document.createElement('span');
    tag.className = 'card-tag';
    tag.textContent = cardId;
    container.appendChild(tag);
  });
}

connect();
