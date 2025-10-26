"""
Event Bus для слабой связанности модулей
"""
from typing import Callable, Dict, List
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """Простая реализация Event Bus"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def on(self, event_name: str):
        """Декоратор для подписки на событие"""
        def decorator(func: Callable):
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            self._subscribers[event_name].append(func)
            logger.info(f"Subscribed {func.__name__} to event '{event_name}'")
            return func
        return decorator
    
    def emit(self, event_name: str, data: dict = None):
        """Публикация события"""
        if event_name not in self._subscribers:
            logger.debug(f"No subscribers for event '{event_name}'")
            return
        
        logger.info(f"Emitting event '{event_name}' with data: {data}")
        
        for subscriber in self._subscribers[event_name]:
            try:
                subscriber(data or {})
            except Exception as e:
                logger.error(f"Error in subscriber {subscriber.__name__}: {e}")


# Глобальный экземпляр event bus
event_bus = EventBus()
