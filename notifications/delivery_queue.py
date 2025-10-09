"""
Message delivery queue with priority handling and retry logic

Manages queuing, delivery, and retry of notification messages across platforms.
"""

import queue
import threading
import time
import json
import pickle
import os
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from .base_service import NotificationMessage
from .logger import get_notification_logger

class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class QueuedMessage:
    """Message with queuing metadata."""
    message: NotificationMessage
    priority: MessagePriority
    queued_at: datetime
    scheduled_for: datetime
    retry_count: int = 0
    last_attempt: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def __lt__(self, other):
        """Compare messages for priority queue ordering."""
        if self.priority.value != other.priority.value:
            return self.priority.value > other.priority.value  # Higher priority first
        return self.scheduled_for < other.scheduled_for  # Earlier scheduled first

class DeliveryQueue:
    """Message delivery queue with priority handling and retry logic."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize delivery queue."""
        self.config = config
        self.logger = get_notification_logger('delivery_queue')
        
        # Queue configuration
        self.max_queue_size = config.get('queue_size', 100)
        self.batch_size = config.get('batch_size', 5)
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 5)  # Base delay in seconds
        self.persistence_file = config.get('persistence_file', 'message_queue.pkl')
        
        # Initialize queues
        self.message_queue = queue.PriorityQueue(maxsize=self.max_queue_size)
        self.dead_letter_queue = []
        self.processing_queue = {}  # Messages currently being processed
        
        # Threading
        self.is_running = False
        self.worker_thread = None
        self.queue_lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'messages_queued': 0,
            'messages_delivered': 0,
            'messages_failed': 0,
            'messages_retried': 0,
            'queue_overflows': 0
        }
        
        # Service registry
        self.services = {}
        
        # Load persisted messages
        self._load_persisted_messages()
        
        self.logger.info("Delivery queue initialized")
    
    def register_service(self, service_name: str, service_callback: Callable):
        """
        Register a notification service for message delivery.
        
        Args:
            service_name: Name of the service (e.g., 'telegram', 'whatsapp')
            service_callback: Callback function to send messages
        """
        self.services[service_name] = service_callback
        self.logger.info(f"Registered service: {service_name}")
    
    def enqueue_message(
        self, 
        message: NotificationMessage, 
        priority: str = 'normal',
        delay_seconds: int = 0
    ) -> bool:
        """
        Add a message to the delivery queue.
        
        Args:
            message: Message to queue
            priority: Message priority ('low', 'normal', 'high', 'urgent')
            delay_seconds: Delay before delivery (for scheduling)
            
        Returns:
            bool: True if message was queued successfully
        """
        try:
            # Convert priority string to enum
            priority_map = {
                'low': MessagePriority.LOW,
                'normal': MessagePriority.NORMAL,
                'high': MessagePriority.HIGH,
                'urgent': MessagePriority.URGENT
            }
            priority_enum = priority_map.get(priority.lower(), MessagePriority.NORMAL)
            
            # Calculate scheduled delivery time
            scheduled_for = datetime.now() + timedelta(seconds=delay_seconds)
            
            # Create queued message
            queued_message = QueuedMessage(
                message=message,
                priority=priority_enum,
                queued_at=datetime.now(),
                scheduled_for=scheduled_for
            )
            
            # Check queue capacity
            if self.message_queue.full():
                self.logger.warning("Message queue is full, dropping oldest low-priority message")
                self._drop_low_priority_message()
                self.stats['queue_overflows'] += 1
            
            # Add to queue
            self.message_queue.put(queued_message, block=False)
            self.stats['messages_queued'] += 1
            
            self.logger.info(f"Message queued: {message.message_id} (priority: {priority})")
            
            # Persist queue state
            self._persist_messages()
            
            return True
            
        except queue.Full:
            self.logger.error(f"Failed to queue message {message.message_id}: Queue full")
            self.stats['queue_overflows'] += 1
            return False
        except Exception as e:
            self.logger.error(f"Error queuing message {message.message_id}: {str(e)}")
            return False
    
    def start_processing(self):
        """Start the message processing worker thread."""
        if self.is_running:
            self.logger.warning("Queue processing already running")
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        
        self.logger.info("Message queue processing started")
    
    def stop_processing(self):
        """Stop the message processing worker thread."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        
        # Persist remaining messages
        self._persist_messages()
        
        self.logger.info("Message queue processing stopped")
    
    def _process_queue(self):
        """Main queue processing loop."""
        self.logger.info("Queue processing worker started")
        
        while self.is_running:
            try:
                # Process batch of messages
                messages_processed = self._process_batch()
                
                if messages_processed == 0:
                    # No messages to process, sleep briefly
                    time.sleep(1)
                else:
                    # Brief pause between batches
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Error in queue processing: {str(e)}")
                time.sleep(5)  # Wait before retrying
        
        self.logger.info("Queue processing worker stopped")
    
    def _process_batch(self) -> int:
        """
        Process a batch of messages from the queue.
        
        Returns:
            int: Number of messages processed
        """
        messages_to_process = []
        current_time = datetime.now()
        
        # Collect messages ready for processing
        for _ in range(self.batch_size):
            try:
                if self.message_queue.empty():
                    break
                
                queued_message = self.message_queue.get(block=False)
                
                # Check if message is scheduled for future delivery
                if queued_message.scheduled_for > current_time:
                    # Put it back in queue for later
                    self.message_queue.put(queued_message)
                    break
                
                messages_to_process.append(queued_message)
                
            except queue.Empty:
                break
        
        # Process collected messages
        for queued_message in messages_to_process:
            self._process_single_message(queued_message)
        
        return len(messages_to_process)
    
    def _process_single_message(self, queued_message: QueuedMessage):
        """
        Process a single message.
        
        Args:
            queued_message: Message to process
        """
        message = queued_message.message
        
        try:
            # Add to processing queue
            with self.queue_lock:
                self.processing_queue[message.message_id] = queued_message
            
            # Get service for this platform
            service_callback = self.services.get(message.platform)
            if not service_callback:
                self.logger.error(f"No service registered for platform: {message.platform}")
                self._handle_failed_delivery(queued_message, "No service registered")
                return
            
            # Attempt delivery
            queued_message.last_attempt = datetime.now()
            success = service_callback(message)
            
            if success:
                self.logger.info(f"Message delivered successfully: {message.message_id}")
                self.stats['messages_delivered'] += 1
            else:
                self.logger.warning(f"Message delivery failed: {message.message_id}")
                self._handle_failed_delivery(queued_message, "Service returned failure")
            
        except Exception as e:
            self.logger.error(f"Exception processing message {message.message_id}: {str(e)}")
            self._handle_failed_delivery(queued_message, str(e))
        
        finally:
            # Remove from processing queue
            with self.queue_lock:
                self.processing_queue.pop(message.message_id, None)
    
    def _handle_failed_delivery(self, queued_message: QueuedMessage, error_message: str):
        """
        Handle failed message delivery with retry logic.
        
        Args:
            queued_message: Failed message
            error_message: Error description
        """
        queued_message.retry_count += 1
        queued_message.error_message = error_message
        
        if queued_message.retry_count <= self.max_retries:
            # Calculate retry delay with exponential backoff
            delay = self.retry_delay * (2 ** (queued_message.retry_count - 1))
            queued_message.scheduled_for = datetime.now() + timedelta(seconds=delay)
            
            # Re-queue for retry
            try:
                self.message_queue.put(queued_message, block=False)
                self.stats['messages_retried'] += 1
                self.logger.info(f"Message re-queued for retry {queued_message.retry_count}: {queued_message.message.message_id}")
            except queue.Full:
                self.logger.error(f"Failed to re-queue message for retry: {queued_message.message.message_id}")
                self._move_to_dead_letter_queue(queued_message)
        else:
            # Max retries exceeded, move to dead letter queue
            self.logger.error(f"Max retries exceeded for message: {queued_message.message.message_id}")
            self._move_to_dead_letter_queue(queued_message)
    
    def _move_to_dead_letter_queue(self, queued_message: QueuedMessage):
        """Move message to dead letter queue."""
        self.dead_letter_queue.append(queued_message)
        self.stats['messages_failed'] += 1
        
        # Limit dead letter queue size
        if len(self.dead_letter_queue) > 100:
            self.dead_letter_queue.pop(0)  # Remove oldest
        
        self.logger.error(f"Message moved to dead letter queue: {queued_message.message.message_id}")
    
    def _drop_low_priority_message(self):
        """Drop the oldest low-priority message to make room."""
        temp_messages = []
        dropped = False
        
        # Extract all messages and find low priority ones to drop
        while not self.message_queue.empty():
            try:
                msg = self.message_queue.get(block=False)
                if not dropped and msg.priority == MessagePriority.LOW:
                    self.logger.warning(f"Dropping low priority message: {msg.message.message_id}")
                    dropped = True
                else:
                    temp_messages.append(msg)
            except queue.Empty:
                break
        
        # Put remaining messages back
        for msg in temp_messages:
            try:
                self.message_queue.put(msg, block=False)
            except queue.Full:
                break
    
    def _persist_messages(self):
        """Persist current queue state to disk."""
        try:
            # Collect all messages from queue
            messages_to_persist = []
            temp_messages = []
            
            while not self.message_queue.empty():
                try:
                    msg = self.message_queue.get(block=False)
                    messages_to_persist.append(msg)
                    temp_messages.append(msg)
                except queue.Empty:
                    break
            
            # Put messages back in queue
            for msg in temp_messages:
                try:
                    self.message_queue.put(msg, block=False)
                except queue.Full:
                    break
            
            # Add processing messages
            with self.queue_lock:
                messages_to_persist.extend(self.processing_queue.values())
            
            # Save to file
            if messages_to_persist:
                with open(self.persistence_file, 'wb') as f:
                    pickle.dump(messages_to_persist, f)
                    
        except Exception as e:
            self.logger.error(f"Error persisting messages: {str(e)}")
    
    def _load_persisted_messages(self):
        """Load persisted messages from disk."""
        try:
            if os.path.exists(self.persistence_file):
                with open(self.persistence_file, 'rb') as f:
                    persisted_messages = pickle.load(f)
                
                # Re-queue persisted messages
                for queued_message in persisted_messages:
                    try:
                        self.message_queue.put(queued_message, block=False)
                    except queue.Full:
                        self.logger.warning("Queue full while loading persisted messages")
                        break
                
                self.logger.info(f"Loaded {len(persisted_messages)} persisted messages")
                
                # Clean up persistence file
                os.remove(self.persistence_file)
                
        except Exception as e:
            self.logger.error(f"Error loading persisted messages: {str(e)}")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current queue status and statistics.
        
        Returns:
            dict: Queue status information
        """
        with self.queue_lock:
            processing_count = len(self.processing_queue)
        
        return {
            'queue_size': self.message_queue.qsize(),
            'processing_count': processing_count,
            'dead_letter_count': len(self.dead_letter_queue),
            'is_running': self.is_running,
            'statistics': self.stats.copy(),
            'registered_services': list(self.services.keys())
        }
    
    def get_dead_letter_messages(self) -> List[QueuedMessage]:
        """Get messages from dead letter queue."""
        return self.dead_letter_queue.copy()
    
    def retry_dead_letter_message(self, message_id: str) -> bool:
        """
        Retry a message from the dead letter queue.
        
        Args:
            message_id: ID of message to retry
            
        Returns:
            bool: True if message was re-queued successfully
        """
        for i, queued_message in enumerate(self.dead_letter_queue):
            if queued_message.message.message_id == message_id:
                # Reset retry count and re-queue
                queued_message.retry_count = 0
                queued_message.scheduled_for = datetime.now()
                
                try:
                    self.message_queue.put(queued_message, block=False)
                    self.dead_letter_queue.pop(i)
                    self.logger.info(f"Dead letter message re-queued: {message_id}")
                    return True
                except queue.Full:
                    self.logger.error(f"Failed to re-queue dead letter message: {message_id}")
                    return False
        
        self.logger.warning(f"Dead letter message not found: {message_id}")
        return False
    
    def clear_dead_letter_queue(self):
        """Clear all messages from dead letter queue."""
        count = len(self.dead_letter_queue)
        self.dead_letter_queue.clear()
        self.logger.info(f"Cleared {count} messages from dead letter queue")