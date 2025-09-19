# Audio Assets for Toddler Counting Game

This folder contains audio files for the counting game. The audio system has fallback to speech synthesis if files are not available.

## Folder Structure

### `/numbers/`
Voice recordings for numbers 1-5 (currently available):
- `one.mp3` - "One"
- `two.mp3` - "Two"
- `three.mp3` - "Three"
- `four.mp3` - "Four"
- `five.mp3` - "Five"

### `/greetings/`
Welcome and greeting messages:
- `hi_ready_to_play.mp3` - Initial greeting message

### `/instructions/`
Game instruction audio:
- `show_me_your_fingers.mp3` - Basic instruction to show fingers
- `lets_start_counting.mp3` - Instruction to begin counting

### `/positive_feedback/`
Encouraging responses for correct answers:
- `correct.mp3` - Simple positive confirmation
- `eze_yofi.mp3` - Hebrew positive feedback ("Eze Yofi" - "How beautiful/great")
- `great_kol_hakavod.mp3` - Hebrew encouragement ("Great, Kol Hakavod" - "Great, well done")

### `/encouragement/`
Motivational responses for incorrect attempts:
- `try_again.mp3` - Gentle encouragement to try again
- `try_again_c.mp3` - Alternative version of try again message

## Audio Specifications

- **Format**: MP3
- **Quality**: Various (user-recorded)
- **Language**: Mixed English and Hebrew
- **Voice**: Child-friendly, warm, encouraging tone
- **Duration**: 1-4 seconds per phrase

## Fallback Behavior

If audio files are missing, the system automatically uses Web Speech Synthesis API as a fallback, so the game will still work without any audio files.