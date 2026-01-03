
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
        elif message_type == 'ai_prediction_request':
            await self.handle_ai_prediction_request(user_id, message)
        elif message_type == 'ai_recommendation_request':
            await self.handle_ai_recommendation_request(user_id, message)
        elif message_type == 'ai_risk_analysis_request':
            await self.handle_ai_risk_analysis_request(user_id, message)
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

    async def handle_ai_prediction_request(self, user_id: str, message: WebSocketMessage):
        """Handle real-time AI prediction requests via WebSocket."""
        try:
            from ..ai_trading.engines.prediction_engine import PredictionEngine
            
            data = message.data
            symbol = data.get('symbol')
            timeframes = data.get('timeframes', ["1d", "3d", "7d", "30d"])
            
            if not symbol:
                await self.send_error(user_id, "Symbol is required for prediction")
                return
            
            # Send processing notification
            await self.connection_manager.send_personal_message(user_id, {
                'type': 'ai_processing',
                'data': {
                    'request_type': 'prediction',
                    'symbol': symbol,
                    'status': 'processing'
                }
            })
            
            # Generate prediction
            prediction_engine = PredictionEngine()
            prediction_result = await prediction_engine.generate_predictions(symbol, timeframes)
            
            # Send result
            await self.connection_manager.send_personal_message(user_id, {
                'type': 'ai_prediction_result',
                'data': {
                    'symbol': prediction_result.symbol,
                    'predictions': prediction_result.predictions,
                    'confidence_score': prediction_result.confidence_score,
                    'model_ensemble': prediction_result.model_ensemble,
                    'timestamp': prediction_result.timestamp.isoformat()
                }
            })
            
        except Exception as e:
            self.logger.error(f"Error handling AI prediction request: {str(e)}")
            await self.send_error(user_id, f"Prediction request failed: {str(e)}")

    async def handle_ai_recommendation_request(self, user_id: str, message: WebSocketMessage):
        """Handle real-time AI recommendation requests via WebSocket."""
        try:
            from ..ai_trading.engines.prediction_engine import PredictionEngine
            from ..ai_trading.engines.recommendation_engine import RecommendationEngine
            from ..ai_trading.engines.risk_analyzer import RiskAnalyzer
            from ..ai_trading.data_models import RiskAssessment
            
            data = message.data
            symbol = data.get('symbol')
            portfolio = data.get('portfolio', {})
            
            if not symbol:
                await self.send_error(user_id, "Symbol is required for recommendation")
                return
            
            # Send processing notification
            await self.connection_manager.send_personal_message(user_id, {
                'type': 'ai_processing',
                'data': {
                    'request_type': 'recommendation',
                    'symbol': symbol,
                    'status': 'processing'
                }
            })
            
            # Generate components
            prediction_engine = PredictionEngine()
            recommendation_engine = RecommendationEngine()
            risk_analyzer = RiskAnalyzer()
            
            # Get prediction and risk analysis
            prediction_result = await prediction_engine.generate_predictions(symbol)
            risk_metrics = await risk_analyzer.calculate_risk_metrics(symbol, portfolio)
            
            risk_assessment = RiskAssessment(
                risk_metrics=risk_metrics,
                portfolio_impact=0.1,
                risk_score=50.0,
                risk_factors=["volatility", "beta"],
                mitigation_strategies=["diversification"],
                timestamp=datetime.now()
            )
            
            # Generate recommendation
            recommendation = await recommendation_engine.generate_recommendation(
                symbol, prediction_result, risk_assessment
            )
            
            # Send result
            await self.connection_manager.send_personal_message(user_id, {
                'type': 'ai_recommendation_result',
                'data': {
                    'symbol': recommendation.symbol,
                    'action': recommendation.action,
                    'confidence': recommendation.confidence,
                    'target_price': recommendation.target_price,
                    'stop_loss': recommendation.stop_loss,
                    'rationale': recommendation.rationale,
                    'risk_reward_ratio': recommendation.risk_reward_ratio,
                    'timestamp': recommendation.timestamp.isoformat()
                }
            })
            
        except Exception as e:
            self.logger.error(f"Error handling AI recommendation request: {str(e)}")
            await self.send_error(user_id, f"Recommendation request failed: {str(e)}")

    async def handle_ai_risk_analysis_request(self, user_id: str, message: WebSocketMessage):
        """Handle real-time AI risk analysis requests via WebSocket."""
        try:
            from ..ai_trading.engines.risk_analyzer import RiskAnalyzer
            
            data = message.data
            portfolio = data.get('portfolio', {})
            symbol = data.get('symbol')
            
            if not portfolio:
                await self.send_error(user_id, "Portfolio data is required for risk analysis")
                return
            
            # Send processing notification
            await self.connection_manager.send_personal_message(user_id, {
                'type': 'ai_processing',
                'data': {
                    'request_type': 'risk_analysis',
                    'status': 'processing'
                }
            })
            
            # Perform risk analysis
            risk_analyzer = RiskAnalyzer()
            
            result = {}
            
            # Individual stock risk if symbol provided
            if symbol:
                risk_metrics = await risk_analyzer.calculate_risk_metrics(symbol, portfolio)
                risk_alerts = await risk_analyzer.generate_risk_alerts(risk_metrics)
                
                result['individual_risk'] = {
                    'symbol': risk_metrics.symbol,
                    'volatility': risk_metrics.volatility,
                    'beta': risk_metrics.beta,
                    'var_1d': risk_metrics.var_1d,
                    'sharpe_ratio': risk_metrics.sharpe_ratio,
                    'risk_alerts': [
                        {
                            'type': alert.alert_type,
                            'severity': alert.severity,
                            'message': alert.message
                        }
                        for alert in risk_alerts
                    ]
                }
            
            # Portfolio risk analysis
            portfolio_risk = await risk_analyzer.assess_portfolio_risk(portfolio)
            
            result['portfolio_risk'] = {
                'overall_risk_score': portfolio_risk.overall_risk_score,
                'concentration_risk': portfolio_risk.concentration_risk,
                'sector_exposure': portfolio_risk.sector_exposure,
                'risk_alerts': [
                    {
                        'type': alert.alert_type,
                        'severity': alert.severity,
                        'message': alert.message
                    }
                    for alert in portfolio_risk.risk_alerts
                ]
            }
            
            # Send result
            await self.connection_manager.send_personal_message(user_id, {
                'type': 'ai_risk_analysis_result',
                'data': result
            })
            
        except Exception as e:
            self.logger.error(f"Error handling AI risk analysis request: {str(e)}")
            await self.send_error(user_id, f"Risk analysis request failed: {str(e)}")

    async def broadcast_ai_market_alert(self, alert_data: Dict[str, Any]):
        """Broadcast AI-generated market alerts to all connected users."""
        message = {
            'type': 'ai_market_alert',
            'data': {
                **alert_data,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        await self.connection_manager.broadcast_message(message)

    async def send_ai_recommendation_update(self, user_id: str, recommendation_data: Dict[str, Any]):
        """Send AI recommendation updates to specific user."""
        message = {
            'type': 'ai_recommendation_update',
            'data': {
                **recommendation_data,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        await self.connection_manager.send_personal_message(user_id, message)