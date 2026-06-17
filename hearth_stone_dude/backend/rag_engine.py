import json
import requests
from typing import List, Dict, Optional, Any
from pathlib import Path
from backend.config import Config


class KimiAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.moonshot.cn/v1"
        self.model = "moonshot-v1-8k"
        
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Optional[str]:
        """调用 Kimi AI 聊天接口"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            return None
            
        except Exception as e:
            print(f"Kimi AI API error: {e}")
            return None


class RAGEngine:
    def __init__(self, kimi_api_key: str):
        self.kimi_client = KimiAIClient(kimi_api_key)
        self.deck_documents: List[Dict[str, Any]] = []
        self._load_sample_documents()
        
    def _load_sample_documents(self):
        """加载示例卡组文档"""
        sample_decks = [
            {
                "id": "deck_001",
                "name": "奥秘法",
                "class": "法师",
                "description": "奥秘法是一套快攻法师卡组，依靠奥秘联动和法术直伤获胜",
                "core_cards": ["奥秘守护者", "法力浮龙", "烈焰风暴", "镜像实体", "法术反制"],
                "strategy": "1-3费铺场并挂奥秘，4费后配合法术打爆发",
                "counters": ["AOE清场", "沉默", "破坏奥秘"],
                "rhythm_points": ["1费下奥秘守护者，2费挂奥秘", "4费烈焰风暴清场+返场"]
            },
            {
                "id": "deck_002",
                "name": "海盗战",
                "class": "战士",
                "description": "海盗战是一套极致快攻战士卡组，依靠海盗随从和武器获胜",
                "core_cards": ["南海船工", "恩佐斯的大副", "血帆袭击者", "毁灭之锤", "升级"],
                "strategy": "1费下海盗，2费升级，持续给对手压力",
                "counters": ["AOE清场", "嘲讽链", "叠甲"],
                "rhythm_points": ["1费必须有海盗", "4费前打残对手"]
            },
            {
                "id": "deck_003",
                "name": "控制术",
                "class": "术士",
                "description": "控制术是一套后期制胜的控制术士卡组",
                "core_cards": ["暮光幼龙", "山岭巨人", "扭曲虚空", "虹吸灵魂"],
                "strategy": "前期解场，中期返场，后期制胜",
                "counters": ["快攻压制", "OTK爆发"],
                "rhythm_points": ["4费前要能苟活", "6费后开始返场"]
            }
        ]
        self.deck_documents = sample_decks
        
    def retrieve_similar_decks(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """简单的关键词匹配检索"""
        results = []
        query_lower = query.lower()
        
        for doc in self.deck_documents:
            score = 0
            text = f"{doc['name']} {doc['class']} {doc['description']} {' '.join(doc['core_cards'])}".lower()
            
            if query_lower in text:
                score += 2
            for card in doc['core_cards']:
                if card.lower() in query_lower:
                    score += 1
                    
            if score > 0:
                results.append({**doc, "score": score})
                
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def generate_deck_analysis(self, game_state: Dict[str, Any], deck_info: Dict[str, Any]) -> str:
        """使用 Kimi AI 生成卡组分析"""
        if not deck_info:
            return "无法识别对手卡组"
            
        context = self._build_context(game_state, deck_info)
        
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的炉石传说助手，擅长分析对手卡组和提供建议。"
            },
            {
                "role": "user",
                "content": f"""请分析当前炉石传说游戏局势并给出建议：

游戏状态：
{json.dumps(context, ensure_ascii=False, indent=2)}

请提供：
1. 对手卡组分析
2. 对手下一步可能的打法
3. 我的应对策略建议
4. 需要注意的关键卡牌"""
            }
        ]
        
        return self.kimi_client.chat_completion(messages) or "AI分析暂时不可用"
    
    def _build_context(self, game_state: Dict[str, Any], deck_info: Dict[str, Any]) -> Dict[str, Any]:
        """构建上下文数据"""
        return {
            "opponent_deck": deck_info.get("identified_deck"),
            "confidence": deck_info.get("confidence", 0),
            "opponent_class": deck_info.get("class"),
            "opponent_played_cards": deck_info.get("played_cards", []),
            "remaining_key_cards": deck_info.get("remaining_key_cards", []),
            "deck_strategy": deck_info.get("deck_info", {}).get("play_style"),
            "game_turn": game_state.get("game_state", {}).get("current_turn", 0)
        }
    
    def generate_play_suggestion(self, game_state: Dict[str, Any], hand_cards: List[str]) -> str:
        """生成出牌建议"""
        context = {
            "hand_cards": hand_cards,
            "game_turn": game_state.get("game_state", {}).get("current_turn", 0),
            "is_in_game": game_state.get("game_state", {}).get("is_in_game", False)
        }
        
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的炉石传说助手，擅长提供出牌建议。"
            },
            {
                "role": "user",
                "content": f"""我的手牌：{hand_cards}
当前回合：{context['game_turn']}

请给出简要的出牌建议（1-3句话）："""
            }
        ]
        
        return self.kimi_client.chat_completion(messages, temperature=0.6) or "建议根据场面灵活出牌"
