import os
import time
import json
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, Any
import asyncio
import openai
from .tools import hangup_call
from logger import logging
logger = logging.getLogger(__name__)


GOOGLE_OPENAI_COMPATIBLE_API = "https://generativelanguage.googleapis.com/v1beta/openai/"

GPTMessageRole = Enum("MessageRole", ["system", "user", "assistant", "function"])

@dataclass
class GPTMessage:
    role: GPTMessageRole
    content: str

    def to_api(self):
        return {"role": self.role.name, "content": self.content}
    

def call_function(name, args):
    """
    LLM helper for calling the tools
    """
        
    if name == "hangup_call":
        return hangup_call()

class OpenAILLM:
    """
    Generaic LLM client for OpenAI & Google Gemini
    """
    def __init__(self, 
        provider: str, model_name: str, cfg: Dict[str, Any], 
        tts_callback: Callable = None, tts_flush_callback: Callable = None, 
        tools = None
    ) -> None:
        self._api_key            = self._get_api_key(provider)
        self._base_url           = self._get_base_url(provider)
        self._model_name         = model_name
        self._cfg                = cfg
        self._validate_reqs()
        self._client             = openai.AsyncOpenAI(                          # Initialize OpenAI/Google client
            api_key=self._api_key, 
            base_url=self._base_url
        )
        self.st_history          = []                                           # Short term history[Call messages]
        self.tools               = tools                                        # LLM tools
        self._tts_callback       = tts_callback                                 # TTS callbacks for passing chunks to TTS
        self._tts_flush_callback = tts_flush_callback                           # Flush the TTS text-buffer
        self._producing_response = False                                        # Flags for managing agent while callee speaking
        self._needs_interrupt    = False
        self.words_per_second    = 3.0                                          # Sec to wait till TTS process                                                                  

    def _get_api_key(self, provider: str) -> str:
        """
        Get API key by LLM provider
        """
        if provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif provider == "google":
            return os.getenv("GEMINI_API_KEY")
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _get_base_url(self, provider: str) -> str:
        """
        Get LLM endpoint by LLM provider
        """
        if provider == "google":
            return GOOGLE_OPENAI_COMPATIBLE_API
        return None

    def _validate_reqs(self) -> None:
        checks = [
            (self._api_key, "API key can't be None."),
            (self._model_name, "Model name can't be None."),
            (self._cfg, "Configurations can't be None."),
        ]
        for value, message in checks:
            if value is None:
                raise ValueError(message)

    def _add_msg_to_history(self, role:str, content:str) -> None:
        """Keeps conversations in history"""
        message = {"role": role, "content": content}
        self.st_history.append(message)

    def _update_prompt(self, prompt: str) -> None:
        """Update the system prompt"""
        self.st_history.append(GPTMessage(GPTMessageRole.system, prompt).to_api())

    async def get_llm_response(self, user_msg: str):
        """Get the LLM response for a user message."""
        
        if user_msg:
            self._add_msg_to_history("user", user_msg)

        self._producing_response = True
        complete_response = []
        function_calls = {}

        try:
            chat_stream = await asyncio.wait_for(
                self._client.chat.completions.create(
                    model=self._model_name,
                    n=1,
                    stream=True,
                    messages=self.st_history,
                    tools=self.tools,
                    tool_choice="auto"
                ),
                timeout=10,
            )
        except (asyncio.TimeoutError, Exception) as e:
            msg = "Sorry, it seems there’s an issue with the call. Could you please repeat what you were saying?"
            complete_response.append(msg)
            await self._tts_callback(msg)
            logger.error(e)
        
        else:        
            async for chunk in chat_stream:
                if self._needs_interrupt:
                    self._needs_interrupt = False
                    complete_response.append(" ... < INTERUPTION >")
                    break

                delta = chunk.choices[0].delta

                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        index = tool_call.index
                        if index not in function_calls:
                            function_calls[index] = tool_call
                        else:
                            function_calls[index].function.arguments += tool_call.function.arguments
                elif delta.content:
                    complete_response.append(delta.content)
                    if self._tts_callback:
                        await self._tts_callback(delta.content)

        if complete_response:
            await self._tts_flush_callback()

        if function_calls:
            for index, call in function_calls.items():
                try:
                    arguments = json.loads(call.function.arguments)
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode arguments for function {function_name}")
                    continue
                
                function_name = call.function.name
                if function_name == "hangup_call":
                    result = call_function(function_name, arguments)
                    self.st_history.append({
                        "role": "assistant",
                        "tool_calls": [{
                            "id": call.id or f"call_RzfkBpJgzeR0S242qfvjadNe",
                            "type": "function",
                            "function": {
                                "name": function_name,
                                "arguments": {},
                            }
                        }]
                    })
                    self.st_history.append({
                        "role": "tool",
                        "tool_call_id": call.id or f"call_RzfkBpJgzeR0S242qfvjadNe",
                        "content": str(result)
                    })
                    
                    t_words = len("".join(complete_response).split())
                    duration  = t_words / self.words_per_second
                    await asyncio.sleep(duration + 1)
                    return "end call!"

                result = call_function(function_name, arguments)
                self.st_history.append({
                    "role": "assistant",
                    "tool_calls": [{
                        "id": call.id or f"call_RzfkBpJgzeR0S242qfvjadNe",
                        "type": "function",
                        "function": {
                            "name": function_name,
                            "arguments": call.function.arguments,
                        }
                    }]
                })
                self.st_history.append({
                    "role": "tool",
                    "tool_call_id": call.id or f"call_RzfkBpJgzeR0S242qfvjadNe",
                    "content": str(result)
                })

            return await self.get_llm_response("")

        else:
            self._add_msg_to_history("assistant", "".join(complete_response))

        self._producing_response = False
        return "".join(complete_response)

    async def interrupt(self):
        """Interrupt a currently streaming response (if there is one)."""
        if self._producing_response:
            self._needs_interrupt = True

async def process_llm_results(chatgpt_result):
    """Process the results of a LLM call and yield them as a stream of messages."""
    full_response = ""
    async for result in chatgpt_result:
        full_response += result
    logger.info(f"agentFinalSpeech: {full_response}")
    return full_response


def structure_call_summary(call_history):
    summary = "####################\n"
    for response in call_history:
        summary+=f"{response['role']} : {response.get('content',response.get('tool_calls',None))} \n"
    summary += "\n####################"
    return summary