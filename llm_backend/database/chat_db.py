
import sqlite3
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

@dataclass
class ChatMessage:
    id: str
    conversation_id: str
    content: str
    message_type: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Conversation:
    id: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class ChatDatabase:

    def __init__(self, db_path: str = "llm_chat.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()

        asyncio.create_task(self._initialize_db())

    async def _initialize_db(self):
        async with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                conn.commit()
                conn.close()

                self.logger.info("Chat database initialized successfully")

            except Exception as e:
                self.logger.error(f"Error initializing database: {str(e)}")
                raise

    async def _execute_query(self, query: str, params: tuple = (), fetch: bool = False):
        async with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(query, params)

                if fetch:
                    result = cursor.fetchall()
                    conn.close()
                    return result
                else:
                    conn.commit()
                    conn.close()
                    return cursor.rowcount

            except Exception as e:
                self.logger.error(f"Database query error: {str(e)}")
                if 'conn' in locals():
                    conn.close()
                raise

    async def create_conversation(self, conversation_id: str, metadata: Optional[Dict[str, Any]] = None):
        metadata_json = json.dumps(metadata) if metadata else None

        await self._execute_query(query, (conversation_id, metadata_json))
        self.logger.info(f"Created conversation: {conversation_id}")

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:

        result = await self._execute_query(query, (conversation_id,), fetch=True)

        if result:
            row = result[0]
            metadata = json.loads(row['metadata']) if row['metadata'] else None

            return Conversation(
                id=row['id'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                metadata=metadata
            )

        return None

    async def list_conversations(self, limit: int = 20, offset: int = 0) -> List[Conversation]:

        result = await self._execute_query(query, (limit, offset), fetch=True)

        conversations = []
        for row in result:
            metadata = json.loads(row['metadata']) if row['metadata'] else None

            conversation = Conversation(
                id=row['id'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                metadata=metadata
            )
            conversations.append(conversation)

        return conversations

    async def update_conversation_timestamp(self, conversation_id: str):

        await self._execute_query(query, (conversation_id,))

    async def delete_conversation(self, conversation_id: str):
        await self._execute_query(
            'DELETE FROM messages WHERE conversation_id = ?',
            (conversation_id,)
        )

        await self._execute_query(
            'DELETE FROM conversations WHERE id = ?',
            (conversation_id,)
        )

        self.logger.info(f"Deleted conversation: {conversation_id}")

    async def store_message(self, message: ChatMessage):
        metadata_json = json.dumps(message.metadata) if message.metadata else None

        await self._execute_query(query, (
            message.id,
            message.conversation_id,
            message.content,
            message.message_type,
            message.timestamp.isoformat(),
            metadata_json
        ))

    async def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatMessage]:

        result = await self._execute_query(query, (conversation_id, limit, offset), fetch=True)

        messages = []
        for row in result:
            metadata = json.loads(row['metadata']) if row['metadata'] else None

            message = ChatMessage(
                id=row['id'],
                conversation_id=row['conversation_id'],
                content=row['content'],
                message_type=row['message_type'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                metadata=metadata
            )
            messages.append(message)

        return messages

    async def get_last_message(self, conversation_id: str) -> Optional[ChatMessage]:

        result = await self._execute_query(query, (conversation_id,), fetch=True)

        if result:
            row = result[0]
            metadata = json.loads(row['metadata']) if row['metadata'] else None

            return ChatMessage(
                id=row['id'],
                conversation_id=row['conversation_id'],
                content=row['content'],
                message_type=row['message_type'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                metadata=metadata
            )

        return None

    async def get_message_count(self, conversation_id: str) -> int:
        query = 'SELECT COUNT(*) as count FROM messages WHERE conversation_id = ?'
        result = await self._execute_query(query, (conversation_id,), fetch=True)
        return result[0]['count'] if result else 0

    async def clear_conversation_messages(self, conversation_id: str):
        query = 'DELETE FROM messages WHERE conversation_id = ?'
        await self._execute_query(query, (conversation_id,))

        await self.update_conversation_timestamp(conversation_id)

        self.logger.info(f"Cleared messages for conversation: {conversation_id}")

    async def get_statistics(self) -> Dict[str, Any]:
        stats = {}

        result = await self._execute_query(
            'SELECT COUNT(*) as count FROM conversations',
            fetch=True
        )
        stats['total_conversations'] = result[0]['count'] if result else 0

        result = await self._execute_query(
            'SELECT COUNT(*) as count FROM messages',
            fetch=True
        )
        stats['total_messages'] = result[0]['count'] if result else 0

        today = datetime.now().date()
        result = await self._execute_query(
            'SELECT COUNT(*) as count FROM messages WHERE DATE(timestamp) = ?',
            (today.isoformat(),),
            fetch=True
        )
        stats['messages_today'] = result[0]['count'] if result else 0

        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        result = await self._execute_query(
            (week_ago,),
            fetch=True
        )
        stats['active_conversations'] = result[0]['count'] if result else 0

        if stats['total_conversations'] > 0:
            stats['avg_messages_per_conversation'] = round(
                stats['total_messages'] / stats['total_conversations'], 2
            )
        else:
            stats['avg_messages_per_conversation'] = 0

        return stats

    async def cleanup_old_data(self, days_to_keep: int = 90):
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()

        result = await self._execute_query(
            'DELETE FROM messages WHERE timestamp < ?',
            (cutoff_date,)
        )
        messages_deleted = result

        result = await self._execute_query(
        )
        conversations_deleted = result

        self.logger.info(
            f"Cleanup completed: {messages_deleted} messages and "
            f"{conversations_deleted} conversations deleted"
        )

        return {
            'messages_deleted': messages_deleted,
            'conversations_deleted': conversations_deleted
        }