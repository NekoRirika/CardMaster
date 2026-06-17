from typing import Dict, List, Set, Any, Optional
from hearthstone.enums import Zone
from backend.game_state import GameState, CardInfo
from backend.deck_analyzer import DeckAnalyzer
from backend.rag_engine import RAGEngine
from backend.config import Config


class CardTracker:
    def __init__(self):
        self.game_state = GameState()
        self.played_cards: Dict[int, List[str]] = {}
        self.known_deck_cards: Dict[int, Set[str]] = {}
        
        # Phase 2: AI 组件
        self.deck_analyzer = DeckAnalyzer()
        self.deck_analyzer.load_sample_decks()
        
        self.rag_engine: Optional[RAGEngine] = None
        if Config.ENABLE_AI:
            try:
                self.rag_engine = RAGEngine(Config.KIMI_API_KEY)
            except Exception as e:
                print(f"AI 初始化失败: {e}")
        
        # 事件状态
        self.last_card_play_count = 0
        self.last_analyzed_turn = 0
        self.cached_ai_analysis: Optional[Dict[str, Any]] = None
        
    def update(self, packet_tree):
        old_state = self.game_state.to_dict()
        self.game_state.update_from_packet_tree(packet_tree)
        new_state = self.game_state.to_dict()
        self._detect_card_changes(old_state, new_state)
        
    def _detect_card_changes(self, old_state: Dict[str, Any], new_state: Dict[str, Any]):
        old_cards = old_state.get("cards", {})
        new_cards = new_state.get("cards", {})
        
        for entity_id, new_card in new_cards.items():
            old_card = old_cards.get(str(entity_id))
            if old_card:
                old_zone = old_card.get("zone")
                new_zone = new_card.get("zone")
                controller = new_card.get("controller")
                
                if old_zone != new_zone and controller:
                    if old_zone == str(Zone.HAND) and new_zone == str(Zone.PLAY):
                        self._on_card_played(controller, new_card.get("card_id"))
    
    def _on_card_played(self, player_id: int, card_id: str):
        if player_id not in self.played_cards:
            self.played_cards[player_id] = []
        self.played_cards[player_id].append(card_id)
        
    def get_opponent_played_cards(self) -> List[str]:
        if not self.game_state.friendly_player_id:
            return []
        
        opponent_id = None
        for pid in self.game_state.players:
            if pid != self.game_state.friendly_player_id:
                opponent_id = pid
                break
        
        return self.played_cards.get(opponent_id, []) if opponent_id else []
    
    def get_opponent_hand_count(self) -> int:
        if not self.game_state.friendly_player_id:
            return 0
        
        opponent_id = None
        for pid in self.game_state.players:
            if pid != self.game_state.friendly_player_id:
                opponent_id = pid
                break
        
        if not opponent_id:
            return 0
        
        return len(self.game_state.get_hand_cards(opponent_id))
    
    def get_opponent_deck_count(self) -> int:
        if not self.game_state.friendly_player_id:
            return 0
        
        opponent_id = None
        for pid in self.game_state.players:
            if pid != self.game_state.friendly_player_id:
                opponent_id = pid
                break
        
        if not opponent_id:
            return 0
        
        return len(self.game_state.get_deck_cards(opponent_id))
    
    def get_friendly_hand(self) -> List[str]:
        if not self.game_state.friendly_player_id:
            return []
        hand_cards = self.game_state.get_hand_cards(self.game_state.friendly_player_id)
        return [c.card_id for c in hand_cards]
    
    def get_opponent_class(self) -> Optional[str]:
        """获取对手职业"""
        if not self.game_state.friendly_player_id:
            return None
        
        for player_id, player in self.game_state.players.items():
            if player_id != self.game_state.friendly_player_id:
                return player.get("hero_card_id")
        return None
    
    def analyze_opponent_deck(self) -> Dict[str, Any]:
        """分析对手卡组"""
        opponent_class = self.get_opponent_class()
        played_cards = self.get_opponent_played_cards()
        
        return self.deck_analyzer.analyze_opponent_deck(opponent_class, played_cards)
    
    def get_ai_suggestion(self) -> Optional[Dict[str, Any]]:
        """获取 AI 建议"""
        if not self.rag_engine or not Config.ENABLE_AI:
            return None
        
        try:
            current_turn = self.game_state.current_turn
            tracking_data = self.get_tracking_data()
            deck_analysis = self.analyze_opponent_deck()
            
            # 事件驱动触发：对手出新牌 或 回合变化
            opponent_cards_count = len(self.get_opponent_played_cards())
            
            if opponent_cards_count > self.last_card_play_count or current_turn > self.last_analyzed_turn:
                self.last_card_play_count = opponent_cards_count
                self.last_analyzed_turn = current_turn
                
                deck_analysis_text = self.rag_engine.generate_deck_analysis(
                    tracking_data, deck_analysis
                )
                
                play_suggestion = self.rag_engine.generate_play_suggestion(
                    tracking_data, self.get_friendly_hand()
                )
                
                self.cached_ai_analysis = {
                    "deck_analysis": deck_analysis,
                    "ai_deck_analysis": deck_analysis_text,
                    "play_suggestion": play_suggestion,
                    "last_updated": current_turn
                }
            
            return self.cached_ai_analysis
            
        except Exception as e:
            print(f"AI 建议生成失败: {e}")
            return None
    
    def get_tracking_data(self) -> Dict[str, Any]:
        tracking_data = {
            "game_state": self.game_state.to_dict(),
            "played_cards": self.played_cards,
            "opponent_played_cards": self.get_opponent_played_cards(),
            "opponent_hand_count": self.get_opponent_hand_count(),
            "opponent_deck_count": self.get_opponent_deck_count(),
            "friendly_hand": self.get_friendly_hand()
        }
        
        # Phase 2: 添加 AI 分析数据
        if Config.ENABLE_AI:
            ai_data = self.get_ai_suggestion()
            if ai_data:
                tracking_data["ai_analysis"] = ai_data
        
        return tracking_data
