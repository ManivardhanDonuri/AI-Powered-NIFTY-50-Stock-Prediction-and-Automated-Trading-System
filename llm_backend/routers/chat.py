
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from ..services.llm_service import LLMServiceManager, TradingContext
from ..services.trading_context_provider import TradingContextProvider
from ..database.chat_db import ChatDatabase, ChatMessage, Conversation

router = APIRouter()

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    context_type: str = Field(default="general", description="Type of context to use")

class ChatMessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    content: str
    timestamp: datetime
    response_time: float
    cached: bool
    confidence: float

class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    messages: List[Dict[str, Any]]
    total_messages: int
    created_at: datetime
    updated_at: datetime

class QuickActionSuggestion(BaseModel):
    id: str
    text: str
    category: str
    description: str

class QuickActionsResponse(BaseModel):
    suggestions: List[QuickActionSuggestion]
    context_type: str

class ContextUpdateRequest(BaseModel):
    context_data: Dict[str, Any]
    context_type: str = "general"

def get_llm_service(request: Request) -> LLMServiceManager:
    if not hasattr(request.app.state, 'llm_service'):
        raise HTTPException(status_code=500, detail="LLM service not initialized")
    return request.app.state.llm_service

def get_context_provider(request: Request) -> TradingContextProvider:
    if not hasattr(request.app.state, 'context_provider'):
        raise HTTPException(status_code=500, detail="Context provider not initialized")
    return request.app.state.context_provider

chat_db = ChatDatabase()

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    llm_service: LLMServiceManager = Depends(get_llm_service),
    context_provider: TradingContextProvider = Depends(get_context_provider)
):
    try:
        start_time = datetime.now()

        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            await chat_db.create_conversation(conversation_id)

        user_message_id = str(uuid.uuid4())
        user_message = ChatMessage(
            id=user_message_id,
            conversation_id=conversation_id,
            content=request.message,
            message_type="user",
            timestamp=start_time
        )
        await chat_db.store_message(user_message)

        context_data = context_provider.aggregate_context(request.context_type)
        trading_context = TradingContext(
            portfolio=context_data.get('portfolio', {}),
            market=context_data.get('market', {}),
            signals=context_data.get('signals', []),
            performance=context_data.get('performance', {}),
            sentiment=context_data.get('sentiment', {}),
            timestamp=start_time
        )

        llm_response = await llm_service.process_query(request.message, trading_context)

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
                'token_usage': {
                    'prompt_tokens': llm_response.token_usage.prompt_tokens,
                    'completion_tokens': llm_response.token_usage.completion_tokens,
                    'total_tokens': llm_response.token_usage.total_tokens
                }
            }
        )
        await chat_db.store_message(ai_message)

        await chat_db.update_conversation_timestamp(conversation_id)

        return ChatMessageResponse(
            message_id=ai_message_id,
            conversation_id=conversation_id,
            content=llm_response.content,
            timestamp=llm_response.timestamp,
            response_time=llm_response.response_time,
            cached=llm_response.cached,
            confidence=llm_response.confidence
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.get("/history/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0
):
    try:
        conversation = await chat_db.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = await chat_db.get_conversation_messages(conversation_id, limit, offset)

        formatted_messages = []
        for msg in messages:
            formatted_msg = {
                'id': msg.id,
                'content': msg.content,
                'message_type': msg.message_type,
                'timestamp': msg.timestamp.isoformat(),
                'metadata': msg.metadata or {}
            }
            formatted_messages.append(formatted_msg)

        total_messages = await chat_db.get_message_count(conversation_id)

        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=formatted_messages,
            total_messages=total_messages,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")

@router.get("/conversations")
async def list_conversations(limit: int = 20, offset: int = 0):
    try:
        conversations = await chat_db.list_conversations(limit, offset)

        formatted_conversations = []
        for conv in conversations:
            last_message = await chat_db.get_last_message(conv.id)

            formatted_conv = {
                'id': conv.id,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'message_count': await chat_db.get_message_count(conv.id),
                'last_message': {
                    'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                    'timestamp': last_message.timestamp.isoformat(),
                    'message_type': last_message.message_type
                } if last_message else None
            }
            formatted_conversations.append(formatted_conv)

        return {
            'conversations': formatted_conversations,
            'total': len(formatted_conversations)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing conversations: {str(e)}")

@router.post("/context", status_code=200)
async def update_context(
    request: ContextUpdateRequest,
    context_provider: TradingContextProvider = Depends(get_context_provider)
):
    try:
        context_provider.update_context_from_trading_system(request.context_data)

        return {
            'status': 'success',
            'message': 'Context updated successfully',
            'context_type': request.context_type,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating context: {str(e)}")

@router.get("/suggestions", response_model=QuickActionsResponse)
async def get_quick_action_suggestions(
    context_type: str = "general",
    context_provider: TradingContextProvider = Depends(get_context_provider)
):
    try:
        context_data = context_provider.aggregate_context(context_type)

        suggestions = []

        general_suggestions = [
            QuickActionSuggestion(
                id="portfolio_summary",
                text="How is my portfolio performing?",
                category="portfolio",
                description="Get an overview of your current portfolio performance"
            ),
            QuickActionSuggestion(
                id="market_outlook",
                text="What's the current market outlook?",
                category="market",
                description="Get insights on current market conditions and trends"
            ),
            QuickActionSuggestion(
                id="recent_signals",
                text="Explain my recent trading signals",
                category="signals",
                description="Get explanations for recent buy/sell signals"
            ),
            QuickActionSuggestion(
                id="risk_assessment",
                text="What are my current risk exposures?",
                category="risk",
                description="Analyze your portfolio's risk profile"
            )
        ]

        if context_type == "portfolio":
            portfolio_suggestions = [
                QuickActionSuggestion(
                    id="diversification",
                    text="How well diversified is my portfolio?",
                    category="portfolio",
                    description="Analyze portfolio diversification across sectors"
                ),
                QuickActionSuggestion(
                    id="performance_attribution",
                    text="What's driving my portfolio performance?",
                    category="portfolio",
                    description="Identify key contributors to returns"
                )
            ]
            suggestions.extend(portfolio_suggestions)

        elif context_type == "signals":
            signal_suggestions = [
                QuickActionSuggestion(
                    id="signal_confidence",
                    text="How confident should I be in recent signals?",
                    category="signals",
                    description="Assess the reliability of recent trading signals"
                ),
                QuickActionSuggestion(
                    id="signal_timing",
                    text="Is this a good time to act on signals?",
                    category="signals",
                    description="Evaluate market timing for signal execution"
                )
            ]
            suggestions.extend(signal_suggestions)

        elif context_type == "market":
            market_suggestions = [
                QuickActionSuggestion(
                    id="sector_analysis",
                    text="Which sectors are performing well?",
                    category="market",
                    description="Analyze sector performance and trends"
                ),
                QuickActionSuggestion(
                    id="volatility_analysis",
                    text="How volatile is the current market?",
                    category="market",
                    description="Assess current market volatility levels"
                )
            ]
            suggestions.extend(market_suggestions)

        suggestions.extend(general_suggestions)

        return QuickActionsResponse(
            suggestions=suggestions[:8],
            context_type=context_type
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting suggestions: {str(e)}")

@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    try:
        conversation = await chat_db.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        await chat_db.delete_conversation(conversation_id)

        return {
            'status': 'success',
            'message': f'Conversation {conversation_id} deleted successfully'
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")

@router.post("/conversation/{conversation_id}/clear")
async def clear_conversation(conversation_id: str):
    try:
        conversation = await chat_db.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        await chat_db.clear_conversation_messages(conversation_id)

        return {
            'status': 'success',
            'message': f'Conversation {conversation_id} cleared successfully'
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing conversation: {str(e)}")

@router.get("/stats")
async def get_chat_statistics():
    try:
        stats = await chat_db.get_statistics()

        return {
            'total_conversations': stats.get('total_conversations', 0),
            'total_messages': stats.get('total_messages', 0),
            'messages_today': stats.get('messages_today', 0),
            'active_conversations': stats.get('active_conversations', 0),
            'average_messages_per_conversation': stats.get('avg_messages_per_conversation', 0),
            'last_updated': datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")