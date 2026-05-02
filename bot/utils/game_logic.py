import random
from typing import Literal

# ─── Rock Paper Scissors ──────────────────────────────────────────────────────

RPS_CHOICES = ["rock", "paper", "scissors"]

RPS_WINS = {
    "rock": "scissors",
    "scissors": "paper",
    "paper": "rock",
}


def rps_determine_winner(p1_choice: str, p2_choice: str) -> Literal["p1", "p2", "draw"]:
    """Return 'p1', 'p2', or 'draw'."""
    if p1_choice == p2_choice:
        return "draw"
    if RPS_WINS[p1_choice] == p2_choice:
        return "p1"
    return "p2"


# ─── Tic Tac Toe ─────────────────────────────────────────────────────────────

def make_board() -> list[list[str]]:
    return [[" ", " ", " "] for _ in range(3)]


def make_move(board: list[list[str]], row: int, col: int, symbol: str) -> bool:
    """Returns True if move was valid."""
    if board[row][col] != " ":
        return False
    board[row][col] = symbol
    return True


def check_winner(board: list[list[str]]) -> str | None:
    """Returns 'X', 'O', 'draw', or None if game ongoing."""
    lines = []
    # rows
    for row in board:
        lines.append(row)
    # cols
    for col in range(3):
        lines.append([board[r][col] for r in range(3)])
    # diagonals
    lines.append([board[i][i] for i in range(3)])
    lines.append([board[i][2 - i] for i in range(3)])

    for line in lines:
        if line[0] != " " and all(c == line[0] for c in line):
            return line[0]

    if all(board[r][c] != " " for r in range(3) for c in range(3)):
        return "draw"
    return None


def board_position_to_rc(pos: int) -> tuple[int, int]:
    """Convert 1-9 position to (row, col)."""
    pos -= 1
    return pos // 3, pos % 3


# ─── Trivia ───────────────────────────────────────────────────────────────────

TRIVIA_QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "options": ["A) London", "B) Paris", "C) Berlin", "D) Madrid"],
        "answer": "B",
        "category": "Geography",
        "difficulty": "easy",
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["A) Venus", "B) Jupiter", "C) Mars", "D) Saturn"],
        "answer": "C",
        "category": "Science",
        "difficulty": "easy",
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["A) Charles Dickens", "B) William Shakespeare", "C) Mark Twain", "D) Jane Austen"],
        "answer": "B",
        "category": "Literature",
        "difficulty": "easy",
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["A) Atlantic", "B) Indian", "C) Arctic", "D) Pacific"],
        "answer": "D",
        "category": "Geography",
        "difficulty": "easy",
    },
    {
        "question": "How many sides does a hexagon have?",
        "options": ["A) 5", "B) 6", "C) 7", "D) 8"],
        "answer": "B",
        "category": "Math",
        "difficulty": "easy",
    },
    {
        "question": "What is the chemical symbol for Gold?",
        "options": ["A) Ag", "B) Go", "C) Au", "D) Gd"],
        "answer": "C",
        "category": "Science",
        "difficulty": "medium",
    },
    {
        "question": "In which year did World War II end?",
        "options": ["A) 1943", "B) 1944", "C) 1945", "D) 1946"],
        "answer": "C",
        "category": "History",
        "difficulty": "medium",
    },
    {
        "question": "What is the speed of light (approximately)?",
        "options": ["A) 300,000 km/s", "B) 150,000 km/s", "C) 450,000 km/s", "D) 100,000 km/s"],
        "answer": "A",
        "category": "Science",
        "difficulty": "medium",
    },
    {
        "question": "Which country invented pizza?",
        "options": ["A) Greece", "B) Spain", "C) Italy", "D) France"],
        "answer": "C",
        "category": "Culture",
        "difficulty": "easy",
    },
    {
        "question": "What is the powerhouse of the cell?",
        "options": ["A) Nucleus", "B) Ribosome", "C) Mitochondria", "D) Golgi apparatus"],
        "answer": "C",
        "category": "Science",
        "difficulty": "easy",
    },
    {
        "question": "Which element has the atomic number 1?",
        "options": ["A) Helium", "B) Hydrogen", "C) Oxygen", "D) Lithium"],
        "answer": "B",
        "category": "Science",
        "difficulty": "easy",
    },
    {
        "question": "What programming language was created by Guido van Rossum?",
        "options": ["A) Ruby", "B) Java", "C) Python", "D) C++"],
        "answer": "C",
        "category": "Technology",
        "difficulty": "medium",
    },
    {
        "question": "How many bones are in the adult human body?",
        "options": ["A) 196", "B) 206", "C) 216", "D) 226"],
        "answer": "B",
        "category": "Science",
        "difficulty": "medium",
    },
    {
        "question": "Which country has the most natural lakes?",
        "options": ["A) Russia", "B) USA", "C) Canada", "D) Finland"],
        "answer": "C",
        "category": "Geography",
        "difficulty": "hard",
    },
    {
        "question": "What is the Fibonacci sequence rule?",
        "options": [
            "A) Each number is the sum of the previous two",
            "B) Each number is double the previous",
            "C) Each number is the product of the previous two",
            "D) Each number is 3 more than the previous"
        ],
        "answer": "A",
        "category": "Math",
        "difficulty": "medium",
    },
]


def get_trivia_questions(count: int = 5) -> list[dict]:
    return random.sample(TRIVIA_QUESTIONS, min(count, len(TRIVIA_QUESTIONS)))
