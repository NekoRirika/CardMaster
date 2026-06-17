const statusEl = document.getElementById('status');
const gameStatusEl = document.getElementById('game-status');
const opponentSection = document.getElementById('opponent-section');
const friendlySection = document.getElementById('friendly-section');
const opponentHandEl = document.getElementById('opponent-hand');
const opponentDeckEl = document.getElementById('opponent-deck');
const opponentPlayedEl = document.getElementById('opponent-played');
const friendlyHandEl = document.getElementById('friendly-hand');

// AI 元素
const aiSection = document.getElementById('ai-section');
const deckIdentification = document.getElementById('deck-identification');
const deckNameEl = document.getElementById('deck-name');
const deckConfidenceEl = document.getElementById('deck-confidence');
const deckDescEl = document.getElementById('deck-desc');
const remainingCards = document.getElementById('remaining-cards');
const remainingCardList = document.getElementById('remaining-card-list');
const aiAnalysis = document.getElementById('ai-analysis');
const aiAnalysisText = document.getElementById('ai-analysis-text');
const playSuggestion = document.getElementById('play-suggestion');
const suggestionText = document.getElementById('suggestion-text');

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
    aiSection.style.display = 'none';
    return;
  }
  
  gameStatusEl.style.display = 'none';
  opponentSection.style.display = 'block';
  friendlySection.style.display = 'block';
  
  opponentHandEl.textContent = data.opponent_hand_count || 0;
  opponentDeckEl.textContent = data.opponent_deck_count || 0;
  
  updateCardList(opponentPlayedEl, data.opponent_played_cards || []);
  updateCardList(friendlyHandEl, data.friendly_hand || []);
  
  // 更新 AI 分析
  updateAISection(data);
}

function updateAISection(data) {
  const aiData = data.ai_analysis;
  
  if (!aiData) {
    aiSection.style.display = 'none';
    return;
  }
  
  aiSection.style.display = 'block';
  
  // 卡组识别
  const deckAnalysis = aiData.deck_analysis;
  if (deckAnalysis && deckAnalysis.identified_deck) {
    deckIdentification.style.display = 'block';
    deckNameEl.textContent = deckAnalysis.identified_deck;
    deckConfidenceEl.textContent = `(${(deckAnalysis.confidence * 100).toFixed(0)}%)`;
    
    const deckInfo = deckAnalysis.deck_info || {};
    deckDescEl.textContent = deckInfo.description || '';
  } else {
    deckIdentification.style.display = 'none';
  }
  
  // 剩余关键卡牌
  if (deckAnalysis && deckAnalysis.remaining_key_cards && deckAnalysis.remaining_key_cards.length > 0) {
    remainingCards.style.display = 'block';
    updateCardList(remainingCardList, deckAnalysis.remaining_key_cards);
  } else {
    remainingCards.style.display = 'none';
  }
  
  // AI 局势分析
  if (aiData.ai_deck_analysis) {
    aiAnalysis.style.display = 'block';
    aiAnalysisText.textContent = aiData.ai_deck_analysis;
  } else {
    aiAnalysis.style.display = 'none';
  }
  
  // 出牌建议
  if (aiData.play_suggestion) {
    playSuggestion.style.display = 'block';
    suggestionText.textContent = aiData.play_suggestion;
  } else {
    playSuggestion.style.display = 'none';
  }
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
