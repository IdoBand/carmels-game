import logging
from typing import Callable, List, Optional

class EventHandler:
    def __init__(self):
        self.handlers: List[Callable[[int], None]] = []
        self.current_gesture = None
        self.gesture_stability_count = 0
        self.stability_threshold = 3

    def register_handler(self, handler: Callable[[int], None]):
        if handler not in self.handlers:
            self.handlers.append(handler)
            logging.info(f"Handler registered: {handler.__name__}")

    def unregister_handler(self, handler: Callable[[int], None]):
        if handler in self.handlers:
            self.handlers.remove(handler)
            logging.info(f"Handler unregistered: {handler.__name__}")

    def process_gesture(self, detected_number: Optional[int]):
        if detected_number == self.current_gesture:
            self.gesture_stability_count += 1
        else:
            self.gesture_stability_count = 1
            self.current_gesture = detected_number

        if (self.gesture_stability_count >= self.stability_threshold and
            self.current_gesture is not None):
            self._invoke_handlers(self.current_gesture)
            self.gesture_stability_count = 0

    def _invoke_handlers(self, number: int):
        for handler in self.handlers:
            try:
                handler(number)
            except Exception as e:
                logging.error(f"Error in handler {handler.__name__}: {e}")

    def clear_handlers(self):
        self.handlers.clear()
        logging.info("All handlers cleared")