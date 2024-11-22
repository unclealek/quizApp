# quizApp
# Real-Time Quiz Application

A real-time multiplayer quiz application built with Python, using socket programming for client-server communication and Flet for the user interface.

## Features

- **Real-time Quiz Taking**
  - Multiple players can take the quiz simultaneously
  - 10-second timer per question
  - Immediate feedback on answers
  - Score tracking and final results

- **Server Dashboard**
  - Real-time display of quiz results
  - Shows player names, scores, and completion times
  - Scrollable history of all quiz attempts
  - Clean, tabular layout

- **Client Interface**
  - Welcome screen with name input
  - Multiple-choice questions with timer
  - Color-coded timer (blue/red for urgency)
  - Final score display

## Technical Architecture

### Server (`quiz_server.py`)
- Socket server handling multiple client connections
- Question management and scoring logic
- Real-time results dashboard using Flet
- JSON-based communication protocol

### Client (`quiz_client.py`)
- Socket client for server communication
- Flet-based user interface
- Timer management
- Answer submission and score display

## Requirements

- Python 3.x
- Flet >= 0.9.0
- Socket library (built-in)
- JSON library (built-in)
- Threading library (built-in)

## Installation

1. Clone the repository or download the files
2. Create a virtual environment (recommended):
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On macOS/Linux
   # or
   myenv\Scripts\activate  # On Windows
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the server:
   ```bash
   python quiz_server.py
   ```
   This will open the server dashboard window.

2. Start one or more clients:
   ```bash
   python quiz_client.py
   ```
   Each client will open in a new window.

## How to Play

1. **Start the Client**
   - Enter your name in the welcome screen
   - Click "Start Quiz" to begin

2. **Taking the Quiz**
   - Read each question carefully
   - You have 10 seconds to answer each question
   - Click on your chosen answer
   - See immediate feedback on your answer
   - Your score updates after each question

3. **Timer System**
   - 10 seconds per question
   - Timer shows in blue initially
   - Changes to red in final seconds
   - Question auto-submits when time runs out

4. **Completing the Quiz**
   - See your final score
   - Results appear on server dashboard
   - Close the window to exit

## Server Dashboard

The server dashboard displays:
- Player Names
- Scores (as fractions, e.g., 3/4)
- Completion Times
- Scrollable history of all attempts

## Project Structure

```
socketio/
├── README.md
├── requirements.txt
├── quiz_server.py
├── quiz_client.py
└── templates/
    └── index.html
```

## Communication Protocol

The application uses JSON messages for client-server communication:

### Client to Server:
```json
{
    "type": "name",
    "name": "player_name"
}

{
    "type": "answer",
    "answer": "selected_answer"
}

{
    "type": "timeout"
}
```

### Server to Client:
```json
{
    "type": "welcome",
    "message": "Welcome message"
}

{
    "type": "question",
    "data": {
        "question": "Question text",
        "options": ["Option1", "Option2", "Option3", "Option4"],
        "correct_answer": "Correct option"
    },
    "time_limit": 10
}

{
    "type": "result",
    "correct": true/false,
    "message": "Result message",
    "score": current_score
}
```

## Error Handling

- Connection failures
- Timeout handling
- Invalid JSON messages
- Client disconnections

## Future Improvements

1. Add more questions and categories
2. Implement difficulty levels
3. Add persistent high scores
4. User authentication
5. Question randomization
6. Multiple quiz modes
7. Chat functionality between players
8. Custom timer settings

## Contributing

Feel free to fork the project and submit pull requests for any improvements.

## License

This project is open source and available under the MIT License.
# quizApp
# quiz

