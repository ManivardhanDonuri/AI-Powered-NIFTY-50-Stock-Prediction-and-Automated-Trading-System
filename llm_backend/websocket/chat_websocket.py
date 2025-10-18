
import json
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Dict, Set, Any, Optional

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError

from ..services.llm_service import LLMServiceManager, TradingContext
from ..services.trading_context_provider import TradingContextProvider
from ..database.chat_db import ChatDatabase, ChatMessage

class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None
    message_id: Optional[str] = None

class ConnectionManager:

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_sessions[user_id] = {
            'connected_at': datetime.now(),
            'last_activity': datetime.now(),
            'conversation_id': None,
            'typing': False
        }

        self.logger.info(f"WebSocket connected: {user_id}")

        await self.send_personal_message(user_id, {
            'type': 'connection_established',
            'data': {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'message': 'Connected to chat service'
            }
        })

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        if user_id in self.user_sessions:
            del self.user_sessions[user_id]

        self.logger.info(f"WebSocket disconnected: {user_id}")

    async def send_personal_message(self, user_id: str, message: Dict[str, Any]):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))

                if user_id in self.user_sessions:
                    self.user_sessions[user_id]['last_activity'] = datetime.now()

            except Exception as e:
                self.logger.error(f"Error sending message to {user_id}: {str(e)}")
                self.disconnect(user_id)

    async def broadcast_message(self, message: Dict[str, Any], exclude_user: Optional[str] = None):
        disconnected_users = []

        for user_id, websocket in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue

            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                self.logger.error(f"Error broadcasting to {user_id}: {str(e)}")
                disconnected_users.append(user_id)

        for user_id in disconnected_users:
            self.disconnect(user_id)

    def get_connected_users(self) -> Set[str]:
        return set(self.active_connections.keys())

    def is_user_connected(self, user_id: str) -> bool:
        return user_id in self.active_connections

    async def set_user_typing(self, user_id: str, typing: bool):
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['typing'] = typing
            self.user_sessions[user_id]['last_activity'] = datetime.now()

            conversation_id = self.user_sessions[user_id].get('conversation_id')
            if conversation_id:
                await self.broadcast_typing_status(user_id, conversation_id, typing)

    async def broadcast_typing_status(self, user_id: str, conversation_id: str, typing: bool):
        message = {
            'type': 'typing_status',
            'data': {
                'user_id': user_id,
                'conversation_id': conversation_id,
                'typing': typing,
                'timestamp': datetime.now().isoformat()
            }
        }

        await self.broadcast_message(message, exclude_user=user_id)

class ChatWebSocketHandler:

    def __init__(
        self,
        llm_service: LLMServiceManager,
        context_provider: TradingContextProvider,
        chat_db: ChatDatabase
    ):
        self.llm_service = llm_service
        self.context_provider = context_provider
        self.chat_db = chat_db
        self.connection_manager = ConnectionManager()
        self.logger = logging.getLogger(__name__)

        self.typing_tasks: Dict[str, asyncio.Task] = {}

    async def handle_websocket(self, websocket: WebSocket, user_id: str):
        await self.connection_manager.connect(websocket, user_id)

        try:
            while True:
                data = await websocket.receive_text()

                try:
                    message_data = json.loads(data)
                    ws_message = WebSocketMessage(**message_data)

                    await self.handle_message(user_id, ws_message)

                except ValidationError as e:
                    await self.send_error(user_id, f"Invalid message format: {str(e)}")
                except json.JSONDecodeError:
                    await self.send_error(user_id, "Invalid JSON format")
                except Exception as e:
                    self.logger.error(f"Error handling message from {user_id}: {str(e)}")
                    await self.send_error(user_id, "Internal server error")

        except WebSocketDisconnect:
            self.connection_manager.disconnect(user_id)
        except Exception as e:
            self.logger.error(f"WebSocket error for {user_id}: {str(e)}")
            self.connection_manager.disconnect(user_id)

    async def handle_message(self, user_id: str, message: WebSocketMessage):
        message_type = message.type

        if message_type == 'chat_message':
            await self.handle_chat_message(user_id, message)
        elif message_type == 'typing_start':
            await self.handle_typing_start(user_id, message)
        elif message_type == 'typing_stop':
            await self.handle_typing_stop(user_id, message)
        elif message_type == 'ping':
            await self.handle_ping(user_id, message)
        elif message_type == 'join_conversation':
            await self.handle_join_conversation(user_id, message)
        elif message_type == 'context_update':
            await self.handle_context_update(user_id, message)
        else:
            await self.send_error(user_id, f"Unknown message type: {message_type}")

    async def handle_chat_message(self, user_id: str, message: WebSocketMessage):
        try:
            data = message.data
            content = data.get('content', '').strip()
            conversation_id = data.get('conversation_id')
            context_type = data.get('context_type', 'general')

            if not content:
                await self.send_error(user_id, "Message content cannot be empty")
                return

            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                await self.chat_db.create_conversation(conversation_id)

            user_message_id = str(uuid.uuid4())

            user_message = ChatMessage(
                id=user_message_id,
                conversation_id=conversation_id,
                content=content,
                message_type="user",
                timestamp=datetime.now()
            )
            await self.chat_db.store_message(user_message)

            await self.connection_manager.send_personal_message(user_id, {
                'type': 'message_received',
                'data': {
                    'message_id': user_message_id,
                    'conversation_id': conversation_id,
                    'status': 'received'
                }
            })

            await self.connection_manager.send_personal_message(user_id, {
                'type': 'ai_typing',
                'data': {
                    'conversation_id': conversation_id,
                    'typing': True
                }
            })

            context_data = self.context_provider.aggregate_context(context_type)
            trading_context = TradingContext(
                portfolio=context_data.get('portfolio', {}),
                market=context_data.get('market', {}),
                signals=context_data.get('signals', []),
                performance=context_data.get('performance', {}),
                sentiment=context_data.get('sentiment', {}),
                timestamp=datetime.now()
            )

            llm_response = await self.llm_service.process_query(content, trading_context)

            ai_message_id = str(uuid.uuid4())
            ai_message = ChatMessage(
                id=ai_message_id,
                conversation_id=conversation_id,
                content=llm_response.content,
                message_type="assistant",
                timestamp=llm_response.timestamp,
                metadata={
                    'confidence': llm_response.confidence,
                    'cached': llm_response.cached,
                    'response_time': llm_response.response_time,
                    'token_usage': {
                        'prompt_tokens': llm_response.token_usage.prompt_tokens,
                        'completion_tokens': llm_response.token_usage.completion_tokens,
                        'total_tokens': llm_response.token_usage.total_tokens
                    }
                }
            )
            await self.chat_db.store_message(ai_message)

            await self.chat_db.update_conversation_timestamp(conversation_id)

            await self.connection_manager.send_personal_message(user_id, {
                'type': 'ai_typing',
                'data': {
                    'conversation_id': conversation_id,
                    'typing': False
                }
            })

            await self.connection_manager.send_personal_message(user_id, {
                'type': 'chat_response',
                'data': {
                    'message_id': ai_message_id,
                    'conversation_id': conversation_id,
                    'content': llm_response.content,
                    'timestamp': llm_response.timestamp.isoformat(),
                    'confidence': llm_response.confidence,
                    'cached': llm_response.cached,
                    'response_time': llm_response.response_time
                }
            })

        except Exception as e:
            self.logger.error(f"Error handling chat message: {str(e)}")
            await self.send_error(user_id, "Failed to process message")

    async def handle_typing_start(self, user_id: str, message: WebSocketMessage):
        conversation_id = message.data.get('conversation_id')

        if conversation_id:
            if user_id in self.typing_tasks:
                self.typing_tasks[user_id].cancel()

            await self.connection_manager.set_user_typing(user_id, True)

            self.typing_tasks[user_id] = asyncio.create_task(
                self._typing_timeout(user_id, conversation_id)
            )

    async def handle_typing_stop(self, user_id: str, message: WebSocketMessage):
        conversation_id = message.data.get('conversation_id')

        if conversation_id:
            if user_id in self.typing_tasks:
                self.typing_tasks[user_id].cancel()
                del self.typing_tasks[user_id]

            await self.connection_manager.set_user_typing(user_id, False)

    async def _typing_timeout(self, user_id: str, conversation_id: str):
        try:
            await asyncio.sleep(5)
            await self.connection_manager.set_user_typing(user_id, False)

            if user_id in self.typing_tasks:
                del self.typing_tasks[user_id]

        except asyncio.CancelledError:
            pass

    async def handle_ping(self, user_id: str, message: WebSocketMessage):
        await self.connection_manager.send_personal_message(user_id, {
            'type': 'pong',
            'data': {
                'timestamp': datetime.now().isoformat(),
                'original_timestamp': message.data.get('timestamp')
            }
        })

    async def handle_join_conversation(self, user_id: str, message: WebSocketMessage):
        conversation_id = message.data.get('conversation_id')

        if conversation_id:
            if user_id in self.connection_manager.user_sessions:
                self.connection_manager.user_sessions[user_id]['conversation_id'] = conversation_id

            await self.connection_manager.send_personal_message(user_id, {
                'type': 'conversation_joined',
                'data': {
                    'conversation_id': conversation_id,
                    'timestamp': datetime.now().isoformat()
                }
            })

    async def handle_context_update(self, user_id: str, message: WebSocketMessage):
        try:
            context_data = message.data.get('context_data', {})
            context_type = message.data.get('context_type', 'general')

            self.context_provider.update_context_from_trading_system(context_data)

            await self.connection_manager.send_personal_message(user_id, {
                'type': 'context_updated',
                'data': {
                    'context_type': context_type,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                }
            })

        except Exception as e:
            await self.send_error(user_id, f"Failed to update context: {str(e)}")

    async def send_error(self, user_id: str, error_message: str):
        await self.connection_manager.send_personal_message(user_id, {
            'type': 'error',
            'data': {
                'message': error_message,
                'timestamp': datetime.now().isoformat()
            }
        })

    async def broadcast_market_update(self, update_data: Dict[str, Any]):
        message = {
            'type': 'market_update',
            'data': {
                **update_data,
                'timestamp': datetime.now().isoformat()
            }
        }

        await self.connection_manager.broadcast_message(message)

    async def send_system_notification(self, user_id: str, notification: Dict[str, Any]):
        message = {
            'type': 'system_notification',
            'data': {
                **notification,
                'timestamp': datetime.now().isoformat()
            }
        }

        await self.connection_manager.send_personal_message(user_id, message)

    def get_connection_stats(self) -> Dict[str, Any]:
        connected_users = self.connection_manager.get_connected_users()

        return {
            'total_connections': len(connected_users),
            'connected_users': list(connected_users),
            'active_typing_sessions': len(self.typing_tasks),
            'timestamp': datetime.now().isoformat()
        }