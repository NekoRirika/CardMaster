from typing import Dict, List, Set, Optional, Tuple
from collections import Counter
from hearthstone.enums import GameTag, CardType, Zone


class DeckAnalyzer:
    def __init__(self):
        self.deck_database: Dict[str, dict] = {}

    def load_deck(self, deck_name: str, deck_data: dict):
        """加载一个卡组到数据库中"""
        self.deck_database[deck_name] = deck_data

    def load_sample_decks(self):
        """加载示例卡组数据"""
        sample_decks = {
            "奥秘法": {
                "class": "Mage",
                "description": "依靠奥秘和法术爆发的快攻法师",
                "core_cards": ["Secretkeeper", "Mana Wyrm", "Flamewaker", "Arcane Missiles"],
                "key_cards": ["Mirror Entity", "Counterspell", "Flame Strike"],
                "play_style": "快攻",
                "weaknesses": ["AOE", "清场"],
                "rhythm": "1-3费抢血，4费后爆发"
            },
            "海盗战": {
                "class": "Warrior",
                "description": "依靠海盗随从铺场的快攻战士",
                "core_cards": ["Southsea Deckhand", "N'Zoth's First Mate", "Bloodsail Raider"],
                "key_cards": ["Frothing Berserker", "Death's Bite", "Upgrade"],
                "play_style": "快攻",
                "weaknesses": ["AOE", "嘲讽"],
                "rhythm": "1费海盗，2费升级，持续抢血"
            },
            "控制术": {
                "class": "Warlock",
                "description": "通过解场和持续吸血来控制场面的术士",
                "core_cards": ["Twilight Drake", "Mountain Giant", "Shadow Bolt"],
                "key_cards": ["Twisting Nether", "Siphon Soul", "Lord Jaraxxus"],
                "play_style": "控制",
                "weaknesses": ["快攻", "OTK"],
                "rhythm": "前期解场，中期返场，后期制胜"
            },
            "中速猎": {
                "class": "Hunter",
                "description": "依靠野兽和直伤的中速猎人",
                "core_cards": ["Animal Companion", "Houndmaster", "Scavenging Hyena"],
                "key_cards": ["Kill Command", "Unleash the Hounds", "Highmane"],
                "play_style": "中速",
                "weaknesses": ["清场", "嘲讽链"],
                "rhythm": "2费生物，4费发力，持续施压"
            }
        }

        for name, data in sample_decks.items():
            self.load_deck(name, data)

    def match_deck(self, player_class: Optional[str], played_cards: List[str]) -> Tuple[Optional[str], float, dict]:
        """根据已出卡牌匹配最可能的卡组"""
        if not played_cards:
            return None, 0.0, {}

        best_match = None
        best_score = 0.0
        best_deck = {}

        for deck_name, deck_data in self.deck_database.items():
            if player_class and deck_data.get("class") != player_class:
                continue

            score = self._calculate_match_score(played_cards, deck_data)
            
            if score > best_score:
                best_score = score
                best_match = deck_name
                best_deck = deck_data

        return best_match, best_score, best_deck

    def _calculate_match_score(self, played_cards: List[str], deck_data: dict) -> float:
        """计算卡组匹配分数"""
        core_cards = deck_data.get("core_cards", [])
        key_cards = deck_data.get("key_cards", [])
        
        played_set = set(played_cards)
        core_set = set(core_cards)
        key_set = set(key_cards)
        
        core_matches = len(played_set & core_set)
        key_matches = len(played_set & key_set)
        
        max_possible = len(core_cards) + len(key_cards)
        if max_possible == 0:
            return 0.0
        
        score = (core_matches * 2 + key_matches) / max_possible
        return min(score, 1.0)

    def analyze_opponent_deck(self, player_class: Optional[str], played_cards: List[str]) -> dict:
        """分析对手卡组并返回详细信息"""
        deck_name, confidence, deck_data = self.match_deck(player_class, played_cards)
        
        return {
            "identified_deck": deck_name,
            "confidence": confidence,
            "class": player_class,
            "deck_info": deck_data,
            "played_cards": played_cards,
            "remaining_key_cards": self._get_remaining_key_cards(deck_data, played_cards)
        }

    def _get_remaining_key_cards(self, deck_data: dict, played_cards: List[str]) -> List[str]:
        """获取卡组中尚未打出的关键卡牌"""
        if not deck_data:
            return []
        
        all_key_cards = deck_data.get("core_cards", []) + deck_data.get("key_cards", [])
        played_set = set(played_cards)
        return [card for card in all_key_cards if card not in played_set]
