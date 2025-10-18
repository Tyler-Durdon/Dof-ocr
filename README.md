# Dofus AI Proof of Concept

This project is a proof of concept (POC) for developing a simple AI that interacts with the Dofus game on a local PC. The AI is designed to read on-screen text and perform actions based on the game's state.

## Project Structure

```
dofus-ai-poc
├── src
│   ├── main.py          # Entry point of the application
│   ├── ai
│   │   └── agent.py     # AI agent for decision-making and interaction
│   ├── utils
│   │   ├── screen_reader.py  # Screen capturing and text extraction
│   │   └── clicker.py       # Simulates mouse clicks
│   └── types
│       └── __init__.py      # Custom types and enums
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd dofus-ai-poc
   ```

2. **Install dependencies**:
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   Then install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:
```
python src/main.py
```

## Features

- **Screen Reading**: The AI can capture the screen and extract text using Optical Character Recognition (OCR).
- **Mouse Interaction**: The AI can simulate mouse clicks at specified coordinates to interact with the game.
- **Decision Making**: The AI agent can make decisions based on the game's state and perform appropriate actions.

## Notes

This project is intended for educational purposes and to demonstrate the capabilities of AI in interacting with games. Ensure that you comply with the game's terms of service when using this AI.