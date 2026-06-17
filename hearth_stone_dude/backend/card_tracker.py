from typing import Dict, List, Set, Any
from hearthstone.enums import Zone
from backend.game_state import GameState, CardInfo


class CardTracker:
    def __init__(self):
        self.game_state = GameState()
        self.played_cards: Dict[int, List[str]] = {}
        self.known_deck_cards: Dict[int, Set[str]] = {}

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

    def get_tracking_data(self) -> Dict[str, Any]:
        return {
            "game_state": self.game_state.to_dict(),
            "played_cards": self.played_cards,
            "opponent_played_cards": self.get_opponent_played_cards(),
            "opponent_hand_count": self.get_opponent_hand_count(),
            "opponent_deck_count": self.get_opponent_deck_count(),
            "friendly_hand": self.get_friendly_hand()
        }
