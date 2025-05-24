import os
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    SpeakWebSocketEvents,
    SpeakWSOptions,
)
from logger import logging
logger = logging.getLogger(__name__)


class DeepgramRTTTS:
    """
    Deepgram's Text-To-Speech Component
    """
    def __init__(self, cfg: dict = None, twilio_callback=None):
        self._api_key         = os.getenv("DEEPGRAM_API_KEY")
        self._cfg             = cfg                                             # Deepgram TTS configuration 
        self._validate_reqs()                                                    # Validate all required vars
        self.tts_connection   = None                                            # TTS connection obj
        self.options          = SpeakWSOptions(**self._cfg)                     # Text-2-Speech Options
        self.twilio_callback  = twilio_callback                                 # Twilio callback for sending speech 2 phone call
        self.words_per_second = 3.0                                             # Sec to wait till speech
        
    def _validate_reqs(self):
        """
        Validates all required vars/objs are not None.
        """
        if not self._api_key:
            raise ValueError(
                "DEEPGRAM_API_KEY environment variable not found!"
            )
        if not self._cfg:
            raise ValueError("TTS Provider configurations can't be None!")

    async def _on_binary_data(self, _, data, **kwargs):
        """
        Sends the audio data to twilio playback
        """
        if self.twilio_callback:
            await self.twilio_callback(data)

    # Methods
    async def init_tts(self):
        """
        Initialize the TTS client
        """
        config = DeepgramClientOptions(
            options={"keep_alive": "true", "speaker_playback": "false"},  
        )
        self.deepgram = DeepgramClient(api_key=self._api_key, config=config)
        self.tts_connection = self.deepgram.speak.asyncwebsocket.v("1")
        self.tts_connection.on(SpeakWebSocketEvents.AudioData, self._on_binary_data)
        
        if await self.tts_connection.start(self.options) is False:
            raise Exception("Failed to connect to Deepgram's TTS!")
        logger.info(f"Deepgram's TTS client established!")
            
    async def speak(self, text_chunk):
        """
        Sends text chunk/LLM response to TTS client
        """
        try:
            await self.tts_connection.send_text(text_chunk)
        except Exception as e:
            logger.error(e)
                
    async def flush_tts(self):
        """
        Generates audio speech immedieatly and clears the buffer
        """
        try:
            await self.tts_connection.flush()
        except Exception as e:
            logger.error(e)
        
    async def clear_tts(self):
        """
        Clear TTS audio buffer
        """
        try:
            await self.tts_connection.clear()
        except Exception as e:
            logger.error(e)
            
    async def stop_tts(self):
        """
        Stops the TTS client
        """
        try:
            await self.tts_connection.finish()   
        except Exception as e:
            logger.error(e)
        finally:
            logger.info(f"Deepgram TTS connection closed!")