## TECHNICAL SETUP PHASE, Game has not started yet. 
- user navigates to localhost:5000
- user clicks on select camera
- BE searches for available cameras, backend passes data to the FE, FE presents available cameras to the user
- user selects a camera and clicks on "Start"

## USER SETUP PHASE, Game has not started yet.
- wait till live video is being displayed in the FE
- play "hi_ready_to_play.mp3"
- after "hi_ready_to_play.mp3" finished playing, wait 2 seconds and play "show_me_your_fingers.mp3"
- user should show his hand, wait till at least 1 hand is visible in the video (any hand detection from MediaPipe) in order to start game.
- only after verifying one hand, play "lets_start_counting.mp3".

## START GAME
- starting with number 1:
  1. **Play number audio immediately** when starting each number (play correct mp3 from dir \frontend\assets\audio\numbers)
  2. **Show the number** on the bottom right corner using the existing overlay
  3. **Wait 15 seconds** for user to show the correct number using her hand
  4. **If no correct gesture after 15 seconds**, replay the current number mp3 and continue waiting until correct gesture is shown
- when the user gestures the number correctly with her hand, randomly play one of the files from \frontend\assets\audio\positive_feedback. all 3 files can be loaded to an array and the randomness can occur by accessing with a random index depending on the array size.
- move on to the next number up until 5 and repeat the above steps. when the user gestures 5 correctly the game is over.


