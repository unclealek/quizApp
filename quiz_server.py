import socket
import threading
import json
import random
import flet as ft
from datetime import datetime

class QuizServer:
    def __init__(self, host='0.0.0.0', port=5002):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.clients = {}  
        self.completed_quizzes = []  
        self.questions = [
            {
                "question": "What is the capital of France?",
                "options": ["London", "Berlin", "Paris", "Madrid"],
                "correct_answer": "Paris"
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                "correct_answer": "Mars"
            },
            {
                "question": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4"
            },
            {
                "question": "Who painted the Mona Lisa?",
                "options": ["Van Gogh", "Da Vinci", "Picasso", "Rembrandt"],
                "correct_answer": "Da Vinci"
            }
        ]
        self.page = None  
        self.results_column = None  
        print(f"Quiz Server running on {self.host}:{self.port}")

    def update_server_ui(self):
        if self.page and self.results_column:
            self.results_column.controls.clear()
            self.results_column.controls.append(
                ft.Row(
                    [
                        ft.Text("Name", size=16, weight=ft.FontWeight.BOLD, width=200),
                        ft.Text("Score", size=16, weight=ft.FontWeight.BOLD, width=100),
                        ft.Text("Time Completed", size=16, weight=ft.FontWeight.BOLD, width=200)
                    ],
                    alignment=ft.MainAxisAlignment.START
                )
            )
            self.results_column.controls.append(ft.Divider())
            for result in self.completed_quizzes:
                self.results_column.controls.append(
                    ft.Row(
                        [
                            ft.Text(result["name"], size=16, width=200),
                            ft.Text(f"{result['score']}/{result['total']}", size=16, width=100),
                            ft.Text(result["time"], size=16, width=200)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    )
                )
            self.page.update()

    def handle_client(self, client_socket, address):
        try:
            # Wait for client name
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                return

            try:
                data = json.loads(message)
                if data["type"] == "name":
                    self.clients[address] = {
                        "name": data["name"],
                        "score": 0,
                        "total_questions": 0,
                        "start_time": datetime.now()
                    }
                    
                    # Send welcome message
                    welcome_msg = {
                        "type": "welcome",
                        "message": f"Welcome {data['name']}! Get ready to start the quiz."
                    }
                    client_socket.send(json.dumps(welcome_msg).encode('utf-8'))
                    
                    # Start the quiz immediately after welcome
                    current_question = random.choice(self.questions)
                    client_socket.send(json.dumps({
                        "type": "question",
                        "data": current_question,
                        "total_time": 5
                    }).encode('utf-8'))
            except json.JSONDecodeError:
                return

            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                try:
                    data = json.loads(message)
                    if data["type"] == "answer":
                        answer = data["answer"]
                        correct = answer == current_question["correct_answer"]
                        
                        if correct:
                            self.clients[address]["score"] += 1
                        self.clients[address]["total_questions"] += 1
                        
                        response = {
                            "type": "result",
                            "correct": correct,
                            "message": "Correct!" if correct else f"Wrong! The correct answer was {current_question['correct_answer']}",
                            "score": self.clients[address]["score"]
                        }
                        client_socket.send(json.dumps(response).encode('utf-8'))

                        # Send next question immediately
                        current_question = random.choice(self.questions)
                        client_socket.send(json.dumps({
                            "type": "question",
                            "data": current_question,
                            "total_time": None
                        }).encode('utf-8'))
                    elif data["type"] == "timeout" or data["type"] == "quiz_end":
                        client_info = self.clients[address]
                        self.completed_quizzes.append({
                            "name": client_info["name"],
                            "score": client_info["score"],
                            "total": client_info["total_questions"],
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        self.update_server_ui()
                        response = {
                            "type": "final_score",
                            "score": client_info["score"],
                            "message": f"Quiz ended! Final score: {client_info['score']}/{client_info['total_questions']}"
                        }
                        client_socket.send(json.dumps(response).encode('utf-8'))
                        break
                except json.JSONDecodeError:
                    print(f"Invalid JSON from client {address}")
        except Exception as e:
            print(f"Error with client {address}: {e}")
        finally:
            if address in self.clients:
                del self.clients[address]
            client_socket.close()
            print(f"Connection closed with {address}")

    def server_ui(self, page: ft.Page):
        self.page = page
        page.title = "Quiz Server Dashboard"
        page.window_width = 600
        page.window_height = 400
        header = ft.Text(
            "Quiz Results Dashboard",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        self.results_column = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            height=300
        )
        page.add(
            ft.Column([
                header,
                ft.Container(height=20),
                self.results_column
            ])
        )
        self.update_server_ui()

    def start(self):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.daemon = True
        server_thread.start()
        ft.app(target=self.server_ui)

    def run_server(self):
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"New connection from {client_address}")
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.start()
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    server = QuizServer()
    server.start()
