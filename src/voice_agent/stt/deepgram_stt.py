import os
import asyncio
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    DeepgramClientOptions
)
from src.logger import logging
logger = logging.getLogger(__name__)


class TranscriptCollector:
    """
    User's interim speech collector & 
    Accumaltes all interim transcriptions when user utterence end
    """
    
    def __init__(self):
        self.transcript_chunks = []
        
    def add_transcript_chunk(self, chunk):
        self.transcript_chunks.append(chunk)
        
    def get_full_transcript(self):
        return ' '.join(self.transcript_chunks)
    
    def reset_transcript(self):
        self.transcript_chunks = []
        
        
class DeepgramSTT:
    """Deepgram's Speech-To-Text"""
    
    def __init__(self, cfg:dict = None, llm_callback = None, 
        irpt_callback = None
    ):
        self._api_key = os.getenv("DEEPGRAM_API_KEY")
        self._cfg     = cfg                                                   # Deepgram STT configs
        self.validate_reqs()                                                  # Validate all required vars/objs
        self.stt_connection       = None                                      # STT connection
        self.options              = LiveOptions(**self._cfg)                  # STT configurations
        self.keepalive_task       = None                                      # STT connection keep alive message sender/5sec
        self.transcript_collector = TranscriptCollector()                     # Interim transcription collector/pool 
        self.llm_callback         = llm_callback                              # LLM callback
        self.irpt_callback        = irpt_callback                             # STT Interuption callback
        self.interuption_flag     = True     

    # STT WS Event handlers 
    async def _on_speech_started(self, _, speech_started, **kwargs):
        pass

    async def _on_message(self, _, result, **kawrgs):
        """
        Add the interim transcription into TranscriptCollector
        """
        transcription = result.channel.alternatives[0].transcript
        if len(transcription) == 0:
            return            
        
        # try:
        if self.interuption_flag:
            await self.irpt_callback()
            self.interuption_flag = False
                
        if result.is_final:
            self.transcript_collector.add_transcript_chunk(transcription)

    async def _on_utterance_end(self, _, utterance_end, **kwargs):
        """
        Aggregate & sends the full transcription to LLM callback
        """
        full_transcription = self.transcript_collector.get_full_transcript()
        
        if self.llm_callback and full_transcription:
            self.transcript_collector.reset_transcript()
            self.interuption_flag = True
            await self.llm_callback(full_transcription)

    # Methods
    async def init_client(self):
        """
        Initialize the STT ws connection with Deepgram
        """
        
        config = DeepgramClientOptions(
            options={"keepalive": "true", 'auto_flush_reply_delta': 8}
        )
        self.client = DeepgramClient(self._api_key, config)
        self.stt_connection = self.client.listen.asyncwebsocket.v("1")
        self.stt_connection.on(
            LiveTranscriptionEvents.SpeechStarted, self._on_speech_started
        )
        self.stt_connection.on(
            LiveTranscriptionEvents.Transcript, self._on_message
        )
        self.stt_connection.on(
            LiveTranscriptionEvents.UtteranceEnd, self._on_utterance_end
        )
        if not await self.stt_connection.start(self.options):
            raise Exception("Failed to connect to Deepgram's STT!")
        
        async def send_keepalive():
            """
            Sends keepAlive msg to WS(/5 sec)
            """
            try:
                while self.stt_connection:
                    await self.stt_connection.keep_alive()
                    await asyncio.sleep(5)
            except (asyncio.CancelledError, Exception) as e:
                logger.error(e)

        self.keepalive_task = asyncio.create_task(send_keepalive())

    async def transcribe_audio(self, audio_chunk):
        """
        Send an audio chunk to STT
        """
        try:
            await self.stt_connection.send(audio_chunk)
        except AttributeError:
            pass
        except Exception as e:
            logger.error(e)

    async def flush_client(self):
        """
        Flush the STT websocket connection
        (Transcribe all sent audio chunks in one go)
        """
        try:
            await self.stt_connection.finalize()
        except Exception as e:
            logger.error(e)

    async def stop_client(self):
        """
        Stop the STT client and close the websocket connection
        """
        if self.keepalive_task:
            self.keepalive_task.cancel()
            try:
                await self.keepalive_task
            except asyncio.CancelledError:
                logger.error("Keepalive task was successfully cancelled.")
            except Exception as e:
                logger.error(e)

        if self.stt_connection:
            try:
                await self.stt_connection.finish()
            except Exception as e:
                logger.error(e)
        
        self.keepalive_task = None
        self.stt_connection = None
        logger.info("Deepgram STT connection closed!")

    def validate_reqs(self):
        """
        Validates all required vars/objs are not None.
        """
        if not self._api_key:
            raise ValueError("DEEPGRAM_API_KEY environment variable not found!")
        if not self._cfg:
            raise ValueError("Deepgram STT configurations can't be None!")