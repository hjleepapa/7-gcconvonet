"""
Cartesia Streaming STT Service - Using Official SDK
Real-time speech-to-text using Cartesia's official SDK for proper authentication
"""

import os
import logging
import threading
from typing import Optional, Callable
from queue import Queue, Empty

logger = logging.getLogger(__name__)

try:
    from cartesia import Cartesia
    CARTESIA_SDK_AVAILABLE = True
except ImportError:
    CARTESIA_SDK_AVAILABLE = False
    logger.warning("Cartesia SDK not available")


class CartesiaStreamingSTT:
    """
    Real-time STT using Cartesia's official Python SDK
    SDK handles authentication, WebSocket management, and message parsing automatically
    """
    
    def __init__(
        self,
        session_id: str,
        on_partial: Optional[Callable[[str], None]] = None,
        on_final: Optional[Callable[[str], None]] = None,
        on_user_speech: Optional[Callable[[], None]] = None,
        language: str = "en"
    ):
        self.session_id = session_id
        self.on_partial = on_partial or (lambda x: None)
        self.on_final = on_final or (lambda x: None)
        self.on_user_speech = on_user_speech or (lambda: None)
        self.language = language
        
        # API configuration
        self.api_key = os.getenv('CARTESIA_API_KEY')
        
        # Streaming state
        self.is_running = False
        self.audio_queue: Queue = Queue()
        
        # Threading
        self.thread = None
        self.stop_event = threading.Event()
        self.ready_event = threading.Event()
        
    def start(self):
        """Start the streaming STT session"""
        if not self.api_key:
            logger.error("❌ Cartesia API key not set")
            return False
        
        logger.info(f"🎤 Starting Cartesia Streaming STT for session {self.session_id}")
        
        self.is_running = True
        self.stop_event.clear()
        
        # Start streaming thread
        self.thread = threading.Thread(target=self._run_streaming_loop, daemon=True)
        self.thread.start()
        
        # Wait for connection ready
        if not self.ready_event.wait(timeout=5.0):
            logger.warning("⚠️ Cartesia streaming connection timeout")
            return False
        
        logger.info("✅ Cartesia Streaming STT ready")
        return True
    
    def send_audio_chunk(self, audio_chunk: bytes):
        """
        Send audio chunk to streaming STT
        Audio should be PCM 16-bit LE, 16kHz or 48kHz
        
        Args:
            audio_chunk: Raw audio bytes
        """
        if not self.is_running:
            logger.warning("⚠️ Streaming STT not running, cannot send audio")
            return
        
        self.audio_queue.put(audio_chunk)
    
    def stop(self):
        """Stop the streaming STT session"""
        logger.info(f"🛑 Stopping Cartesia Streaming STT for session {self.session_id}")
        
        self.is_running = False
        self.stop_event.set()
        
        # Send stop signal
        self.audio_queue.put(None)
        
        # Wait for thread
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        
        logger.info("✅ Cartesia Streaming STT stopped")
    
    def _run_streaming_loop(self):
        """Main streaming loop using Cartesia SDK"""
        try:
            # Initialize Cartesia client (SDK handles auth from CARTESIA_API_KEY env var)
            client = Cartesia(api_key=self.api_key)
            logger.info("✅ Cartesia client initialized")
            
            # Use SDK's stream context manager for proper WebSocket handling
            with client.stream(
                model="ink-whisper",
                language=self.language,
                sample_rate=16000,  # Cartesia expects 16kHz
                encoding="pcm_s16le",
            ) as stream:
                logger.info("📤 Cartesia WebSocket stream opened")
                self.ready_event.set()  # Signal ready to caller
                
                # Stream audio from queue
                while self.is_running:
                    try:
                        # Get audio chunk with timeout
                        chunk = self.audio_queue.get(timeout=0.5)
                        
                        if chunk is None:  # Stop signal
                            logger.info("🛑 Stop signal received")
                            break
                        
                        # Send audio to stream
                        stream.write(chunk)
                        
                        # Read any available responses
                        try:
                            response = stream.read(timeout=0.1)
                            if response:
                                self._process_response(response)
                        except:
                            pass  # Timeout reading response, continue
                            
                    except Empty:
                        # No audio available, just continue
                        continue
                    except Exception as chunk_error:
                        logger.debug(f"📨 Chunk processing: {chunk_error}")
                
                logger.info("✅ Cartesia stream closed")
            
        except Exception as e:
            logger.error(f"❌ Streaming loop error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.ready_event.set()  # Unblock caller even on error
        finally:
            self.is_running = False
    
    def _process_response(self, response):
        """Process Cartesia streaming response"""
        try:
            if not response:
                return
            
            # SDK returns dict with 'type' and 'output' fields
            response_type = response.get("type")
            output = response.get("output")
            
            if response_type == "transcript":
                if output:
                    # Check if confirmed or interim
                    is_final = output.get("is_final", False)
                    text = output.get("transcript", "")
                    
                    if text:
                        if is_final:
                            logger.info(f"✅ Final: {text}")
                            self.on_final(text)
                        else:
                            logger.debug(f"🔤 Partial: {text}")
                            self.on_partial(text)
            
        except Exception as e:
            logger.debug(f"⚠️ Response processing: {e}")


# Global streaming sessions store
_cartesia_streaming_sessions = {}


def get_cartesia_streaming_session(
    session_id: str,
    on_partial: Optional[Callable[[str], None]] = None,
    on_final: Optional[Callable[[str], None]] = None,
    on_user_speech: Optional[Callable[[], None]] = None,
    language: str = "en"
) -> CartesiaStreamingSTT:
    """Get or create Cartesia streaming STT session"""
    
    if session_id not in _cartesia_streaming_sessions:
        session = CartesiaStreamingSTT(
            session_id=session_id,
            on_partial=on_partial,
            on_final=on_final,
            on_user_speech=on_user_speech,
            language=language
        )
        _cartesia_streaming_sessions[session_id] = session
    
    return _cartesia_streaming_sessions[session_id]


def remove_cartesia_streaming_session(session_id: str):
    """Remove and cleanup Cartesia streaming session"""
    if session_id in _cartesia_streaming_sessions:
        session = _cartesia_streaming_sessions[session_id]
        session.stop()
        del _cartesia_streaming_sessions[session_id]
        logger.info(f"🗑️ Removed Cartesia streaming session: {session_id}")
