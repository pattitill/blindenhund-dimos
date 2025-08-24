from dimos.skills.skills import AbstractSkill
from dimos.stream.audio.pipelines import tts
from dimos.stream.audio.node_output import SounddeviceAudioOutput
from pydantic import Field
from reactivex import Subject
from typing import Optional, Any, List
import time
import threading
import queue
from dimos.utils.logging_config import setup_logger

logger = setup_logger("dimos.skills.speak")

# Global lock to prevent multiple simultaneous audio playbacks
_audio_device_lock = threading.RLock()

# Global queue for sequential audio processing
_audio_queue = queue.Queue()
_queue_processor_thread = None
_queue_running = False


def _process_audio_queue():
    """Background thread to process audio requests sequentially"""
    global _queue_running
    
    while _queue_running:
        try:
            # Get the next queued audio task with a timeout
            task = _audio_queue.get(timeout=1.0)
            if task is None:  # Sentinel value to stop the thread
                break
                
            # Execute the task (which is a function to be called)
            task()
            _audio_queue.task_done()
            
        except queue.Empty:
            # No tasks in queue, just continue waiting
            continue
        except Exception as e:
            logger.error(f"Error in audio queue processor: {e}")
            # Continue processing other tasks


def start_audio_queue_processor():
    """Start the background thread for processing audio requests"""
    global _queue_processor_thread, _queue_running
    
    if _queue_processor_thread is None or not _queue_processor_thread.is_alive():
        _queue_running = True
        _queue_processor_thread = threading.Thread(
            target=_process_audio_queue, 
            daemon=True,
            name="AudioQueueProcessor"
        )
        _queue_processor_thread.start()
        logger.info("Started audio queue processor thread")


# Start the queue processor when module is imported
start_audio_queue_processor()

class Speak(AbstractSkill):
    """Speak text out loud to humans nearby or to other robots."""

    text: str = Field(..., description="Text to speak")

    def __init__(self, tts_node: Optional[Any] = None, **data):
        super().__init__(**data)
        self._tts_node = tts_node
        self._audio_complete = threading.Event()
        self._subscription = None
        self._subscriptions: List = []  # Track all subscriptions

    def __call__(self):
        if not self._tts_node:
            logger.error("No TTS node provided to Speak skill")
            return "Error: No TTS node available"
        
        # Create a result queue to get the result back from the audio thread
        result_queue = queue.Queue(1)
        
        # Define the speech task to run in the audio queue
        def speak_task():
            try:
                # Using a lock to ensure exclusive access to audio device
                with _audio_device_lock:
                    text_subject = Subject()
                    self._audio_complete.clear()
                    self._subscriptions = []
                    
                    # This function will be called when audio processing is complete
                    def on_complete():
                        logger.info(f"TTS audio playback completed for: {self.text}")
                        self._audio_complete.set()
                        
                    # This function will be called if there's an error
                    def on_error(error):
                        logger.error(f"Error in TTS processing: {error}")
                        self._audio_complete.set()
                    
                    # Connect the Subject to the TTS node and keep the subscription
                    self._tts_node.consume_text(text_subject)
                    
                    # Subscribe to the audio output to know when it's done
                    self._subscription = self._tts_node.emit_text().subscribe(
                        on_next=lambda text: logger.debug(f"TTS processing: {text}"),
                        on_completed=on_complete,
                        on_error=on_error
                    )
                    self._subscriptions.append(self._subscription)
                    
                    # Emit the text to the Subject
                    text_subject.on_next(self.text)
                    text_subject.on_completed()  # Signal that we're done sending text
                    
                    # Wait for audio playback to complete with a timeout
                    # Using a dynamic timeout based on text length
                    timeout = max(5, len(self.text) * 0.1)
                    logger.debug(f"Waiting for TTS completion with timeout {timeout:.1f}s")
                    
                    if not self._audio_complete.wait(timeout=timeout):
                        logger.warning(f"TTS timeout reached for: {self.text}")
                    else:
                        # Add a small delay after audio completes to ensure buffers are fully flushed
                        time.sleep(0.3)
                    
                    # Clean up all subscriptions
                    for sub in self._subscriptions:
                        if sub:
                            sub.dispose()
                    self._subscriptions = []
                    
                    # Successfully completed
                    result_queue.put(f"Spoke: {self.text} successfully")
            except Exception as e:
                logger.error(f"Error in speak task: {e}")
                result_queue.put(f"Error speaking text: {str(e)}")
        
        # Add our speech task to the global queue for sequential processing
        display_text = self.text[:50] + '...' if len(self.text) > 50 else self.text
        logger.info(f"Queueing speech task: '{display_text}'")
        _audio_queue.put(speak_task)
        
        # Wait for the result with a timeout
        try:
            # Use a longer timeout than the audio playback itself
            text_len_timeout = len(self.text) * 0.15  # 150ms per character
            max_timeout = max(10, text_len_timeout)  # At least 10 seconds
            
            return result_queue.get(timeout=max_timeout)
        except queue.Empty:
            logger.error("Timed out waiting for speech task to complete")
            return f"Error: Timed out while speaking: {self.text}"