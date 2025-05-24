import json
import asyncio
import random
import base64
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from stt import DeepgramSTT
from llm.openai_llm import (OpenAILLM)
from tts.deepgram_tts import DeepgramRTTTS
from llm.tools import schema
from configs.va import *
from logger import logging
logger = logging.getLogger(__name__)


class VoiceAgent:
    def __init__(self, database, cache_db):
        self.websocket:WebSocket                                   
        self.stt_client            = None                          
        self.llm_client            = None                          
        self.tts_client            = None                         
        self.structured_groq       = None                          
        self.stream_sid            = None
        self.call_sid              = None
        self.initial_greeting_sent = False
        self.speak_agent_first     = True
        self.interuption_msg       = ["Okay!. . ", "Alright!. . "]
        self.database              = database
        self.cache_db              = cache_db
        self.cache_store           = None
        self.call_logs             = None

    def update_websocket(self, websocket: WebSocket):
        """
        Update with twilio websocket
        """
        self.websocket = websocket

    async def send_audio_to_twilio(self, audio_data):
        """
        Sends agent audio data to twilio websocket
        """
        try:
            audio_payload = base64.b64encode(audio_data).decode('utf-8')
            audio_message = {
                "event": "media", 
                "streamSid": self.stream_sid, 
                "media": {
                    "payload": audio_payload
                }
            }
            await self.websocket.send_json(audio_message)
        except Exception as e:
            logger.error(e)

    async def clear_twilio_buffer(self):
        """
        Clear twilio audio buffer
        """
        try:
            ws_message = {
                "event": "clear",
                "streamSid": self.stream_sid,
            }
            await self.websocket.send_json(ws_message)
        except Exception as e:
            logger.error(e)

    async def interupt_agent(self):
        """
        Interrupt agent(LLM, TTS & clear twilio buffer)
        """
        await asyncio.gather(
            asyncio.create_task(self.llm_client.interrupt()),
            asyncio.create_task(self.tts_client.clear_tts()),
            asyncio.create_task(self.clear_twilio_buffer())
        )
        await self.tts_client.speak(random.choice(self.interuption_msg))
        await self.tts_client.flush_tts()

    async def process_stt_result(self, text):
        """
        Sends callee speach(Text) to LLM -> TTS -> Twilio
        """
        if text:
            full_response = await self.llm_client.get_llm_response(text)
            if "end call!" in full_response:
                try:
                    asyncio.create_task(self.terminate_call())
                    return                
                except Exception as e:
                    logger.error(e)

    async def initialize(self):
        """
        Initialize agent components(STT, LLM, TTS)
        """
        self.tts_client = DeepgramRTTTS(
            provider_cfg    = TTS_CONFIGURATION, 
            twilio_callback = self.send_audio_to_twilio
        )
        await self.tts_client.init_tts()

        tools = [
            schema['check_availability'], 
            schema['book_appointment'], 
            schema['hangup_call']
        ]
        self.llm_client = OpenAILLM(
            provider=PROVIDER, 
            model_name=MODEL, 
            cfg=LLM_CONFIGURATION, 
            tts_callback=self.tts_client.speak, 
            tts_flush_callback=self.tts_client.flush_tts,
            tools=tools
        )
        
        self.stt_client = DeepgramSTT(
            cfg=STT_CONFIGURATION, 
            llm_callback=self.process_stt_result, 
            irpt_callback=self.interupt_agent
        )
        await self.stt_client.init_client()

    async def send_initial_message(self, msg:str):
        """
        Sends initial(user greeting) audio message to twilio
        """
        if not self.initial_greeting_sent and self.speak_agent_first:
            self.llm_client.add_msg_to_history("assistant", msg)
            try:
                await self.tts_client.speak(msg)
                await self.tts_client.flush_tts()
                self.initial_greeting_sent = True
                logger.debug(f"initialMessage: {msg}")
            except Exception as e:
                logger.error(e)

    async def receive_from_twilio(self):
        """
        Recieves audio packets from twilio and sends agents speech back
        
        This is main block of agent which is responsible for 
        taking the data from twilio, processing, and sending back agent speech to twilio.
        """
        try:
            async for message in self.websocket.iter_text():
                data = json.loads(message)
                
                # This event is fired by Twilio on start of call
                if data['event'] == 'start':
                    self.stream_sid  = data['start']['streamSid']
                    self.call_sid    = data['start']['callSid']
                    self.cache_store = self.cache_db.json().get(f"call:{self.call_sid}")
                    if self.cache_store:
                        prompt = self.cache_store.get("prompt")
                        init_msg = self.cache_store.get("init_msg")
                        self.llm_client.update_prompt(prompt)
                        if not self.initial_greeting_sent:
                            await self.send_initial_message(msg=init_msg)
                            self.initial_greeting_sent = True
                    else:
                        logger.error(
                            f"Error: cache not found for callSid {self.call_sid}"
                        )
                        await self.websocket.close(code=1002)
                        return
                    
                # This event is fired by Twilio to sends the audio packets
                elif data['event'] == 'media':
                    audio_payload = data['media']['payload']
                    audio_bytes = base64.b64decode(audio_payload)
                    try:
                        await self.stt_client.transcribe_audio(audio_bytes)
                    except Exception as e:
                        logger.error(f"Error during STT transcription: {e}")
                    
                # This event is fired by Twilio 
                # when user/callee ends/hangup the call
                elif data['event'] == 'stop':
                    await self.terminate_call()
                    return 
        except WebSocketDisconnect as e:
            logger.error(f"Error occured in TwilioWSHandler: {e}")
            try:
                await self.stt_client.stop_client()
                await self.tts_client.stop_tts()
            except Exception as e:
                logger.error(f"Error occured in TwilioWSHandler: {e}")
        
    async def run(self):
        """
        Run/Entry point of Agent
        """
        await self.receive_from_twilio()

    async def terminate_call(self):
        """
        Logs the call data in database & closes the agent components connection 
        """
        try:
            if self.websocket:
                await self.stt_client.stop_client()
                await self.tts_client.stop_tts()
                await self.websocket.close(code=1000)
        except Exception as e:
            logger.error(e)
            
        logger.info("Connection with Twilio closed.")