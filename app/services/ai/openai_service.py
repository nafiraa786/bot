from openai import AsyncOpenAI
from app.core.config import settings
from typing import List, Dict, Any, Optional
import json

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def get_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.7
    ) -> str:
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=temperature
        )
        return response.choices[0].message.content

    async def get_embeddings(self, text: str) -> List[float]:
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    async def summarize_conversation(self, history: str) -> str:
        prompt = f"Summarize the following conversation history concisely, preserving key facts, names, and preferences:\n\n{history}"
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content

    async def generate_tags(self, text: str) -> List[str]:
        prompt = f"Generate 3-5 short tags (one word each) describing the topics in this text. Return as JSON list of strings.\nText: {text}"
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a tagging assistant. Output JSON only."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return data.get("tags", [])

    async def analyze_sentiment_and_safety(self, text: str) -> Dict[str, Any]:
        prompt = (
            "Analyze the following text for safety and emotion. "
            "Return a JSON object with: "
            "1. 'is_safe' (boolean), "
            "2. 'requires_approval' (boolean - True if emotional, financial, conflict, or promises), "
            "3. 'reason' (string), "
            "4. 'detected_emotion' (string). "
            f"Text: {text}"
        )
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a moderation and sentiment analyzer. Output JSON only."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    async def transcribe_audio(self, file_path: str) -> str:
        with open(file_path, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text

    async def analyze_image(self, image_url: str, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content

ai_service = AIService()
