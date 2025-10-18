
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent / 'llm_backend'))

try:
    from llm_backend.services.llm_service import LLMServiceManager, TradingContext
    from llm_backend.services.trading_context_provider import TradingContextProvider
    from llm_backend.config import get_settings
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

class AINotificationEnhancer:

    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)

        self.llm_service = None
        self.context_provider = None

        if LLM_AVAILABLE:
            try:
                settings = get_settings()
                self.llm_service = LLMServiceManager(settings)
                self.context_provider = TradingContextProvider(config_file)
                self.logger.info("AI notification enhancer initialized with LLM service")
            except Exception as e:
                self.logger.error(f"Failed to initialize LLM service: {str(e)}")
                # Don't modify the global LLM_AVAILABLE here

        if not LLM_AVAILABLE:
            self.logger.warning("LLM service not available, using fallback enhancement")

    async def enhance_signal_notification(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:

        try:
            if not self.llm_service:
                return self._fallback_signal_enhancement(signal_data)

            context_data = self.context_provider.aggregate_context('signals')
            trading_context = TradingContext(
                portfolio=context_data.get('portfolio', {}),
                market=context_data.get('market', {}),
                signals=[signal_data],
                performance=context_data.get('performance', {}),
                sentiment={},
                timestamp=datetime.now()
            )

            llm_response = await self.llm_service.process_query(query, trading_context)

            enhanced_data = {
                'original_signal': signal_data,
                'ai_explanation': llm_response.content,
                'confidence': llm_response.confidence,
                'key_points': self._extract_key_points(llm_response.content),
                'risk_factors': self._extract_risk_factors(llm_response.content),
                'action_items': self._extract_action_items(llm_response.content),
                'enhanced_at': datetime.now().isoformat(),
                'cached': llm_response.cached,
                'response_time': llm_response.response_time
            }

            self.logger.info(f"Enhanced signal notification for {signal_data['symbol']}")
            return enhanced_data

        except Exception as e:
            self.logger.error(f"Error enhancing signal notification: {str(e)}")
            return self._fallback_signal_enhancement(signal_data)

    async def generate_risk_alert(self, risk_data: Dict[str, Any]) -> Dict[str, Any]:

        try:
            if not self.llm_service:
                return self._fallback_risk_alert(risk_data)

            context_data = self.context_provider.aggregate_context('portfolio')
            trading_context = TradingContext(
                portfolio=context_data.get('portfolio', {}),
                market=context_data.get('market', {}),
                signals=[],
                performance=context_data.get('performance', {}),
                sentiment={},
                timestamp=datetime.now()
            )

            llm_response = await self.llm_service.process_query(query, trading_context)

            enhanced_data = {
                'original_risk': risk_data,
                'ai_alert': llm_response.content,
                'confidence': llm_response.confidence,
                'immediate_actions': self._extract_immediate_actions(llm_response.content),
                'impact_assessment': self._extract_impact_assessment(llm_response.content),
                'monitoring_points': self._extract_monitoring_points(llm_response.content),
                'enhanced_at': datetime.now().isoformat(),
                'cached': llm_response.cached
            }

            self.logger.info(f"Generated AI risk alert for {risk_data['type']}")
            return enhanced_data

        except Exception as e:
            self.logger.error(f"Error generating risk alert: {str(e)}")
            return self._fallback_risk_alert(risk_data)

    async def create_market_update(self, market_data: Dict[str, Any]) -> Dict[str, Any]:

        try:
            if not self.llm_service:
                return self._fallback_market_update(market_data)

            context_data = self.context_provider.aggregate_context('market')
            trading_context = TradingContext(
                portfolio=context_data.get('portfolio', {}),
                market=context_data.get('market', {}),
                signals=[],
                performance=context_data.get('performance', {}),
                sentiment={},
                timestamp=datetime.now()
            )

            llm_response = await self.llm_service.process_query(query, trading_context)

            enhanced_data = {
                'original_event': market_data,
                'ai_update': llm_response.content,
                'confidence': llm_response.confidence,
                'sector_impact': self._extract_sector_impact(llm_response.content),
                'opportunities': self._extract_opportunities(llm_response.content),
                'key_levels': self._extract_key_levels(llm_response.content),
                'timeline': self._extract_timeline(llm_response.content),
                'enhanced_at': datetime.now().isoformat(),
                'cached': llm_response.cached
            }

            self.logger.info(f"Created AI market update for {market_data['event']}")
            return enhanced_data

        except Exception as e:
            self.logger.error(f"Error creating market update: {str(e)}")
            return self._fallback_market_update(market_data)

    def format_for_platform(self, enhanced_data: Dict[str, Any], platform: str) -> str:

        try:
            if 'ai_explanation' in enhanced_data:
                return self._format_signal_for_platform(enhanced_data, platform)
            elif 'ai_alert' in enhanced_data:
                return self._format_alert_for_platform(enhanced_data, platform)
            elif 'ai_update' in enhanced_data:
                return self._format_update_for_platform(enhanced_data, platform)
            else:
                return "Enhanced notification content not available"

        except Exception as e:
            self.logger.error(f"Error formatting for {platform}: {str(e)}")
            return "Error formatting enhanced notification"

    def _format_signal_for_platform(self, enhanced_data: Dict[str, Any], platform: str) -> str:
        signal = enhanced_data['original_signal']
        explanation = enhanced_data['ai_explanation']

        if platform == 'telegram':
            header = f"🚨 *{signal['type']} Signal: {signal['symbol']}*\n"
            header += f"💰 Price: {signal['price']} | 📊 Confidence: {signal['confidence']:.1%}\n\n"

            content = header + explanation

            if enhanced_data.get('key_points'):
                content += "\n\n📋 *Key Points:*\n"
                for point in enhanced_data['key_points'][:3]:
                    content += f"• {point}\n"

            return content[:4000]

        elif platform == 'whatsapp':
            header = f"🚨 {signal['type']} Signal: {signal['symbol']}\n"
            header += f"💰 {signal['price']} | 📊 {signal['confidence']:.1%}\n\n"

            content = header + explanation

            return content[:1600]

        return explanation

    def _format_alert_for_platform(self, enhanced_data: Dict[str, Any], platform: str) -> str:
        risk = enhanced_data['original_risk']
        alert = enhanced_data['ai_alert']

        if platform == 'telegram':
            header = f"⚠️ *Risk Alert: {risk['type']}*\n"
            header += f"🔴 Severity: {risk['severity'].upper()}\n\n"

            content = header + alert

            if enhanced_data.get('immediate_actions'):
                content += "\n\n🎯 *Immediate Actions:*\n"
                for action in enhanced_data['immediate_actions'][:2]:
                    content += f"• {action}\n"

            return content[:4000]

        elif platform == 'whatsapp':
            header = f"⚠️ Risk Alert: {risk['type']}\n"
            header += f"🔴 {risk['severity'].upper()} SEVERITY\n\n"

            content = header + alert
            return content[:1600]

        return alert

    def _format_update_for_platform(self, enhanced_data: Dict[str, Any], platform: str) -> str:
        event = enhanced_data['original_event']
        update = enhanced_data['ai_update']

        if platform == 'telegram':
            header = f"📈 *Market Update*\n"
            header += f"📰 {event['event']}\n"
            header += f"📊 Impact: {event['impact'].upper()}\n\n"

            content = header + update

            if enhanced_data.get('opportunities'):
                content += "\n\n💡 *Opportunities:*\n"
                for opp in enhanced_data['opportunities'][:2]:
                    content += f"• {opp}\n"

            return content[:4000]

        elif platform == 'whatsapp':
            header = f"📈 Market Update\n"
            header += f"📰 {event['event']}\n"
            header += f"📊 {event['impact'].upper()} Impact\n\n"

            content = header + update
            return content[:1600]

        return update

    def _fallback_signal_enhancement(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'original_signal': signal_data,
            'ai_explanation': f"Trading signal generated for {signal_data['symbol']} with {signal_data['confidence']:.1%} confidence. {signal_data.get('reason', 'Technical analysis indicates this opportunity.')}",
            'confidence': 0.5,
            'key_points': [f"{signal_data['type']} signal detected", f"Confidence level: {signal_data['confidence']:.1%}"],
            'enhanced_at': datetime.now().isoformat(),
            'fallback': True
        }

    def _fallback_risk_alert(self, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'original_risk': risk_data,
            'ai_alert': f"Risk alert: {risk_data['type']} detected with {risk_data['severity']} severity. Please review your positions and consider appropriate risk management measures.",
            'confidence': 0.5,
            'immediate_actions': ["Review portfolio positions", "Consider risk management"],
            'enhanced_at': datetime.now().isoformat(),
            'fallback': True
        }

    def _fallback_market_update(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'original_event': market_data,
            'ai_update': f"Market event: {market_data['event']} with {market_data['impact']} impact expected. Monitor your positions and market conditions closely.",
            'confidence': 0.5,
            'opportunities': ["Monitor market conditions", "Review position sizing"],
            'enhanced_at': datetime.now().isoformat(),
            'fallback': True
        }

    def _extract_key_points(self, content: str) -> List[str]:
        points = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                clean_point = line.lstrip('•-*123456789. ').strip()
                if clean_point and len(clean_point) > 10:
                    points.append(clean_point)

        return points[:5]

    def _extract_risk_factors(self, content: str) -> List[str]:
        return self._extract_section_items(content, ['risk', 'caution', 'watch'])

    def _extract_action_items(self, content: str) -> List[str]:
        return self._extract_section_items(content, ['action', 'consider', 'recommend'])

    def _extract_immediate_actions(self, content: str) -> List[str]:
        return self._extract_section_items(content, ['immediate', 'urgent', 'now'])

    def _extract_impact_assessment(self, content: str) -> str:
        lines = content.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['impact', 'effect', 'consequence']):
                return line.strip()
        return "Impact assessment not available"

    def _extract_monitoring_points(self, content: str) -> List[str]:
        return self._extract_section_items(content, ['monitor', 'watch', 'track'])

    def _extract_sector_impact(self, content: str) -> List[str]:
        return self._extract_section_items(content, ['sector', 'industry', 'segment'])

    def _extract_opportunities(self, content: str) -> List[str]:
        return self._extract_section_items(content, ['opportunity', 'chance', 'potential'])

    def _extract_key_levels(self, content: str) -> List[str]:
        return self._extract_section_items(content, ['level', 'support', 'resistance'])

    def _extract_timeline(self, content: str) -> str:
        lines = content.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['timeline', 'time', 'duration', 'expect']):
                return line.strip()
        return "Timeline not specified"

    def _extract_section_items(self, content: str, keywords: List[str]) -> List[str]:
        items = []
        lines = content.split('\n')
        in_section = False

        for line in lines:
            line = line.strip()

            if any(keyword in line.lower() for keyword in keywords):
                in_section = True
                if line.startswith(('•', '-', '*')):
                    clean_item = line.lstrip('•-* ').strip()
                    if clean_item:
                        items.append(clean_item)
                continue

            if in_section and line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                clean_item = line.lstrip('•-*123456789. ').strip()
                if clean_item:
                    items.append(clean_item)
            elif in_section and not line:
                continue
            elif in_section and line and not line.startswith(' '):
                in_section = False

        return items[:3]

    async def shutdown(self):
        if self.llm_service:
            await self.llm_service.shutdown()
        self.logger.info("AI notification enhancer shutdown complete")