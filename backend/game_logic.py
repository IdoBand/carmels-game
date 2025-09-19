#!/usr/bin/env python3

import time
from enum import Enum
from typing import Optional, Dict, Any, Callable

class GamePhase(Enum):
    """Game phases for the toddler counting game"""
    SETUP = "setup"
    GREETING = "greeting"
    WAITING_FOR_START = "waiting_for_start"
    COUNTING = "counting"
    CELEBRATION = "celebration"
    COMPLETED = "completed"

class GameLogic:
    """Manages the game state and flow for the toddler counting game"""

    def __init__(self, socketio_emit_func: Callable = None):
        self.emit = socketio_emit_func or (lambda *args, **kwargs: None)

        # Game state
        self.reset_game()

        # Game configuration
        self.MAX_NUMBER = 10
        self.GESTURE_TIMEOUT = 30.0  # seconds to wait for gesture
        self.CELEBRATION_DURATION = 3.0  # seconds for celebration

        # Event callbacks
        self.phase_change_callbacks = []

    def reset_game(self):
        """Reset game to initial state"""
        self.current_phase = GamePhase.SETUP
        self.current_number = 1
        self.numbers_completed = []
        self.start_time = None
        self.phase_start_time = None
        self.last_gesture_time = None
        self.current_detected_number = None
        self.attempts = 0
        self.max_attempts_per_number = 3

    def register_phase_change_callback(self, callback: Callable):
        """Register callback for phase changes"""
        self.phase_change_callbacks.append(callback)

    def _change_phase(self, new_phase: GamePhase, **data):
        """Internal method to change game phase"""
        old_phase = self.current_phase
        self.current_phase = new_phase
        self.phase_start_time = time.time()

        print(f"🎮 Game phase: {old_phase.value} → {new_phase.value}")

        # Prepare phase data
        phase_data = {
            'phase': new_phase.value,
            'old_phase': old_phase.value,
            'timestamp': self.phase_start_time,
            **data
        }

        # Emit to frontend
        self.emit('game_phase_changed', phase_data)

        # Call registered callbacks
        for callback in self.phase_change_callbacks:
            try:
                callback(phase_data)
            except Exception as e:
                print(f"❌ Error in phase change callback: {e}")

    def start_game(self) -> Dict[str, Any]:
        """Start a new game"""
        print("🎮 Starting new game")
        self.reset_game()
        self.start_time = time.time()
        self._change_phase(GamePhase.GREETING)

        return {
            'status': 'started',
            'phase': self.current_phase.value,
            'message': 'Welcome to the Counting Game!'
        }

    def begin_counting_phase(self) -> Dict[str, Any]:
        """Transition from greeting to counting phase"""
        if self.current_phase not in [GamePhase.GREETING, GamePhase.WAITING_FOR_START]:
            return {'status': 'error', 'message': 'Cannot start counting from current phase'}

        self.current_number = 1
        self.attempts = 0
        self._change_phase(
            GamePhase.COUNTING,
            current_number=self.current_number,
            total_numbers=self.MAX_NUMBER,
            instruction=f"Show me {self.current_number} finger{'s' if self.current_number > 1 else ''}!"
        )

        return {
            'status': 'counting_started',
            'current_number': self.current_number,
            'total_numbers': self.MAX_NUMBER
        }

    def process_gesture(self, detected_number: int, confidence: float = 0.0) -> Dict[str, Any]:
        """Process detected gesture based on current game phase"""
        self.current_detected_number = detected_number
        self.last_gesture_time = time.time()

        print(f"🤖 Processing gesture: {detected_number} (confidence: {confidence:.2f})")

        if self.current_phase == GamePhase.WAITING_FOR_START:
            return self._handle_start_gesture(detected_number)
        elif self.current_phase == GamePhase.COUNTING:
            return self._handle_counting_gesture(detected_number)
        else:
            # Gesture detected but not in an interactive phase
            return {
                'status': 'gesture_ignored',
                'detected_number': detected_number,
                'phase': self.current_phase.value
            }

    def _handle_start_gesture(self, detected_number: int) -> Dict[str, Any]:
        """Handle gesture when waiting for game start (looking for thumbs up or number 1)"""
        if detected_number == 1:  # Using "1" as start signal
            print("👍 Start gesture detected!")
            return self.begin_counting_phase()
        else:
            return {
                'status': 'wrong_start_gesture',
                'detected_number': detected_number,
                'expected': 1,
                'message': 'Show me 1 finger to start the game!'
            }

    def _handle_counting_gesture(self, detected_number: int) -> Dict[str, Any]:
        """Handle gesture during counting phase"""
        if detected_number == self.current_number:
            # Correct number detected!
            return self._handle_correct_number()
        else:
            # Wrong number
            return self._handle_wrong_number(detected_number)

    def _handle_correct_number(self) -> Dict[str, Any]:
        """Handle correct number detection"""
        self.numbers_completed.append(self.current_number)
        self.attempts = 0

        print(f"✅ Correct! Number {self.current_number} completed")

        # Emit success event immediately
        self.emit('number_success', {
            'number': self.current_number,
            'completed_numbers': len(self.numbers_completed),
            'total_numbers': self.MAX_NUMBER
        })

        if self.current_number >= self.MAX_NUMBER:
            # Game completed!
            return self._complete_game()
        else:
            # Move to next number
            return self._advance_to_next_number()

    def _handle_wrong_number(self, detected_number: int) -> Dict[str, Any]:
        """Handle wrong number detection"""
        self.attempts += 1

        print(f"❌ Wrong number: {detected_number}, expected: {self.current_number} (attempt {self.attempts})")

        response = {
            'status': 'wrong_number',
            'detected_number': detected_number,
            'expected_number': self.current_number,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts_per_number
        }

        if self.attempts >= self.max_attempts_per_number:
            # Too many attempts, provide hint or move on
            response['message'] = f"Try again! Show me {self.current_number} finger{'s' if self.current_number > 1 else ''}."
            response['hint'] = True
        else:
            response['message'] = f"Not quite! I need {self.current_number} finger{'s' if self.current_number > 1 else ''}."

        return response

    def _advance_to_next_number(self) -> Dict[str, Any]:
        """Move to the next number in the sequence"""
        self.current_number += 1

        print(f"➡️  Advancing to number {self.current_number}")

        # Emit next number event
        self.emit('next_number', {
            'number': self.current_number,
            'total_numbers': self.MAX_NUMBER,
            'instruction': f"Show me {self.current_number} finger{'s' if self.current_number > 1 else ''}!"
        })

        return {
            'status': 'next_number',
            'current_number': self.current_number,
            'completed_count': len(self.numbers_completed),
            'total_numbers': self.MAX_NUMBER
        }

    def _complete_game(self) -> Dict[str, Any]:
        """Complete the game and start celebration"""
        completion_time = time.time() - self.start_time

        print(f"🎉 Game completed! Time: {completion_time:.1f}s")

        self._change_phase(
            GamePhase.CELEBRATION,
            completion_time=completion_time,
            numbers_completed=self.MAX_NUMBER
        )

        return {
            'status': 'game_completed',
            'completion_time': completion_time,
            'numbers_completed': self.MAX_NUMBER
        }

    def handle_no_gesture(self) -> Dict[str, Any]:
        """Handle when no gesture is detected"""
        if self.current_phase in [GamePhase.WAITING_FOR_START, GamePhase.COUNTING]:
            return {
                'status': 'no_gesture',
                'phase': self.current_phase.value,
                'current_number': self.current_number if self.current_phase == GamePhase.COUNTING else None
            }
        return {'status': 'no_gesture_ignored'}

    def get_current_state(self) -> Dict[str, Any]:
        """Get current game state"""
        return {
            'phase': self.current_phase.value,
            'current_number': self.current_number,
            'numbers_completed': self.numbers_completed,
            'total_numbers': self.MAX_NUMBER,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts_per_number,
            'start_time': self.start_time,
            'last_gesture_time': self.last_gesture_time,
            'current_detected_number': self.current_detected_number
        }

    def get_instruction_message(self) -> str:
        """Get current instruction message based on game state"""
        if self.current_phase == GamePhase.GREETING:
            return "Hi! I'm ready to help you count!"
        elif self.current_phase == GamePhase.WAITING_FOR_START:
            return "Show me 1 finger to start counting!"
        elif self.current_phase == GamePhase.COUNTING:
            return f"Show me {self.current_number} finger{'s' if self.current_number > 1 else ''}!"
        elif self.current_phase == GamePhase.CELEBRATION:
            return "Wow! You counted to 10! Amazing job! 🎉"
        elif self.current_phase == GamePhase.COMPLETED:
            return "Great job! Want to play again?"
        else:
            return "Getting ready..."

    def restart_game(self) -> Dict[str, Any]:
        """Restart the game"""
        print("🔄 Restarting game")
        return self.start_game()

# Test/Demo functions
def demo_game_logic():
    """Demonstrate game logic flow"""
    print("🧪 Demo: Game Logic Flow")
    print("=" * 40)

    def mock_emit(event, data):
        print(f"📡 EMIT: {event} -> {data}")

    game = GameLogic(mock_emit)

    # Start game
    result = game.start_game()
    print(f"Start: {result}")

    # Wait for start (wrong gesture)
    game._change_phase(GamePhase.WAITING_FOR_START)
    result = game.process_gesture(3)
    print(f"Wrong start: {result}")

    # Correct start
    result = game.process_gesture(1)
    print(f"Correct start: {result}")

    # Count through numbers (demonstrate correct and wrong answers)
    for i in range(1, 6):  # Test first 5 numbers
        print(f"\n--- Testing number {i} ---")

        # Wrong answer first
        if i > 1:
            wrong_result = game.process_gesture(i - 1)
            print(f"Wrong ({i-1}): {wrong_result}")

        # Correct answer
        correct_result = game.process_gesture(i)
        print(f"Correct ({i}): {correct_result}")

if __name__ == '__main__':
    demo_game_logic()