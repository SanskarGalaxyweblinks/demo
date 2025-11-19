# demo_backend/app/services/groq_client.py
from __future__ import annotations

import asyncio
import time
from typing import Dict, Any, Optional
from groq import Groq
from ..config import settings

class GroqClient:
    """
    Groq API client wrapper with rate limiting, error handling, and token usage tracking.
    """
    
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required but not found in environment")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.daily_token_usage = 0
        self.last_reset_date = time.strftime("%Y-%m-%d")
        self.request_count = 0
        
    def _reset_daily_counters_if_needed(self):
        """Reset daily counters if it's a new day"""
        current_date = time.strftime("%Y-%m-%d")
        if current_date != self.last_reset_date:
            self.daily_token_usage = 0
            self.request_count = 0
            self.last_reset_date = current_date
            print(f"[GROQ] Daily counters reset for {current_date}")
    
    def _check_token_limit(self) -> bool:
        """Check if daily token limit has been exceeded"""
        if not settings.GROQ_ENABLE_TOKEN_TRACKING:
            return True
            
        self._reset_daily_counters_if_needed()
        return self.daily_token_usage < settings.GROQ_DAILY_TOKEN_LIMIT
    
    def _update_token_usage(self, completion_response) -> int:
        """Update token usage tracking and return tokens used"""
        if not settings.GROQ_ENABLE_TOKEN_TRACKING:
            return 0
            
        try:
            usage = completion_response.usage
            tokens_used = usage.total_tokens if hasattr(usage, 'total_tokens') else 0
            self.daily_token_usage += tokens_used
            
            print(f"[GROQ] Tokens used: {tokens_used}, Daily total: {self.daily_token_usage}/{settings.GROQ_DAILY_TOKEN_LIMIT}")
            return tokens_used
        except AttributeError:
            print("[GROQ] Warning: Could not extract token usage from response")
            return 0
    
    async def chat_completion(
        self,
        messages: list[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a chat completion request to Groq API with error handling and rate limiting.
        """
        # Check token limits
        if not self._check_token_limit():
            raise Exception(f"Daily token limit ({settings.GROQ_DAILY_TOKEN_LIMIT}) exceeded")
        
        # Set defaults from config
        model = model or settings.GROQ_MODEL_EMAIL
        temperature = temperature if temperature is not None else settings.GROQ_TEMPERATURE
        max_tokens = max_tokens or settings.GROQ_MAX_TOKENS
        
        try:
            # Make the API call
            self.request_count += 1
            print(f"[GROQ] Making API request #{self.request_count} to model: {model}")
            
            completion_args = {
                "messages": messages,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            if response_format:
                completion_args["response_format"] = response_format
            
            completion = self.client.chat.completions.create(**completion_args)
            
            # Track token usage
            tokens_used = self._update_token_usage(completion)
            
            # Extract response content
            response_content = completion.choices[0].message.content
            
            return {
                "content": response_content,
                "tokens_used": tokens_used,
                "model": model,
                "success": True
            }
            
        except Exception as e:
            print(f"[GROQ] API Error: {str(e)}")
            return {
                "content": None,
                "error": str(e),
                "tokens_used": 0,
                "model": model,
                "success": False
            }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        self._reset_daily_counters_if_needed()
        
        return {
            "daily_token_usage": self.daily_token_usage,
            "daily_token_limit": settings.GROQ_DAILY_TOKEN_LIMIT,
            "requests_today": self.request_count,
            "last_reset_date": self.last_reset_date,
            "tokens_remaining": settings.GROQ_DAILY_TOKEN_LIMIT - self.daily_token_usage
        }

# Global instance
_groq_client_instance = None

def get_groq_client() -> GroqClient:
    """Get singleton Groq client instance"""
    global _groq_client_instance
    if _groq_client_instance is None:
        _groq_client_instance = GroqClient()
    return _groq_client_instance