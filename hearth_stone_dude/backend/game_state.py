import sys
from pathlib import Path
from typing import Optional, Dict, List, Any
from hearthstone.enums import GameTag, Zone

sys.path.insert(0, str(Path(__file__).parent.parent / "python-hslog"))
from hslog.export import EntityTreeExporter, FriendlyPlayerExporter


class CardInfo:
    def __init__(self, card_id: str, entity_id: int):
        self.card_id = card_id
        self.entity_id = entity_id
        self.zone: Optional[Zone] = None
        self.controller: Optional[int] = None
        self.zone_position: Optional[int] = None
        self.attack: Optional[int] = None
        self.health: Optional[int] = None
        self.cost: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "card_id": self.card_id,
            "entity_id": self.entity_id,
            "zone": str(self.zone) if self.zone else None,
            "controller": self.controller,
            "zone_position": self.zone_position,
            "attack": self.attack,
            "health": self.health,
            "cost": self.cost
        }


class PlayerInfo:
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.name: Optional[str] = None
        self.hero_entity_id: Optional[int] = None
        self.hero_card_id: Optional[str] = None
        self.mana_crystals = 0
        self.available_mana = 0
        self.overload_locked = 0


class GameState:
    def __init__(self):
        self.players: Dict[int, PlayerInfo] = {}
        self.cards: Dict[int, CardInfo] = {}
        self.friendly_player_id: Optional[int] = None
        self.current_turn = 0
        self.is_in_game = False

    def update_from_packet_tree(self, packet_tree):
        try:
            entity_exporter = EntityTreeExporter(packet_tree)
            entity_exporter.export()
            game = entity_exporter.game

            if not game:
                return

            self.players.clear()
            self.cards.clear()

            for player in game.players:
                player_info = PlayerInfo(player.player_id)
                player_info.name = player.name
                player_info.hero_entity_id = player.initial_hero_entity_id
                self.players[player.player_id] = player_info

            friendly_exporter = FriendlyPlayerExporter(packet_tree)
            friendly_player = friendly_exporter.export()
            if friendly_player:
                self.friendly_player_id = friendly_player

            for entity_id, entity in game.entities.items():
                if hasattr(entity, 'card_id') and entity.card_id:
                    card_info = CardInfo(entity.card_id, entity_id)
                    card_info.zone = entity.tags.get(GameTag.ZONE)
                    card_info.controller = entity.tags.get(GameTag.CONTROLLER)
                    card_info.zone_position = entity.tags.get(GameTag.ZONE_POSITION)
                    card_info.attack = entity.tags.get(GameTag.ATK)
                    card_info.health = entity.tags.get(GameTag.HEALTH)
                    card_info.cost = entity.tags.get(GameTag.COST)
                    self.cards[entity_id] = card_info

                    if entity_id in [p.hero_entity_id for p in self.players.values()]:
                        for player_info in self.players.values():
                            if player_info.hero_entity_id == entity_id:
                                player_info.hero_card_id = entity.card_id

            self.current_turn = game.tags.get(GameTag.TURN, 0)
            self.is_in_game = True

        except Exception as e:
            print(f"Error updating game state: {e}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "players": {pid: {
                "name": p.name,
                "player_id": p.player_id,
                "hero_card_id": p.hero_card_id
            } for pid, p in self.players.items()},
            "cards": {eid: c.to_dict() for eid, c in self.cards.items()},
            "friendly_player_id": self.friendly_player_id,
            "current_turn": self.current_turn,
            "is_in_game": self.is_in_game
        }

    def get_hand_cards(self, player_id: int) -> List[CardInfo]:
        return [c for c in self.cards.values() if c.controller == player_id and c.zone == Zone.HAND]

    def get_deck_cards(self, player_id: int) -> List[CardInfo]:
        return [c for c in self.cards.values() if c.controller == player_id and c.zone == Zone.DECK]

    def get_play_cards(self, player_id: int) -> List[CardInfo]:
        return [c for c in self.cards.values() if c.controller == player_id and c.zone == Zone.PLAY]

    def get_graveyard_cards(self, player_id: int) -> List[CardInfo]:
        return [c for c in self.cards.values() if c.controller == player_id and c.zone == Zone.GRAVEYARD]
