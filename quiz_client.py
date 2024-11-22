import flet as ft
import socket
import json
import threading
import time

class QuizClient:
    def __init__(self, host='localhost', port=5002):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.score = 0
        self.total_questions = 0
        self.current_question = None
        self.timer_active = False
        self.remaining_time = 0
        self.total_quiz_time = 0
        self.quiz_started = False
        self.player_name = ""

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def send_answer(self, answer):
        if not self.timer_active:  # Don't send answers if timer has expired
            return
        message = {
            "type": "answer",
            "answer": answer
        }
        self.client_socket.send(json.dumps(message).encode('utf-8'))

    def send_name(self, name):
        message = {
            "type": "name",
            "name": name
        }
        self.client_socket.send(json.dumps(message).encode('utf-8'))

    def handle_server_messages(self, page: ft.Page):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                data = json.loads(message)
                if data["type"] == "welcome":
                    self.show_welcome_message(page, data["message"])
                elif data["type"] == "question":
                    self.current_question = data["data"]
                    if data.get("total_time") is not None and not self.quiz_started:  # Start timer only once
                        self.total_quiz_time = data["total_time"]
                        self.remaining_time = self.total_quiz_time
                        self.timer_active = True
                        self.quiz_started = True
                        threading.Thread(target=self.run_timer, args=(page,), daemon=True).start()
                    self.update_question(page)
                elif data["type"] == "result":
                    self.score = data["score"]
                    self.total_questions += 1
                    self.update_score(page)
                    self.show_result(page, data["message"])
                    if not self.timer_active:  # Quiz already ended
                        self.show_final_score(page, f"Final Score: {self.score}/{self.total_questions}")
                        break
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def run_timer(self, page: ft.Page):
        while self.timer_active and self.remaining_time > 0:
            time.sleep(1)
            self.remaining_time -= 1
            self.timer_text.value = f"Time remaining: {self.remaining_time}s"
            self.timer_text.color = ft.colors.RED if self.remaining_time <= 2 else ft.colors.BLUE
            page.update()
            
        if self.timer_active:  # Timer ran out
            self.timer_active = False
            self.quiz_started = False
            self.timer_text.value = "Time's up!"
            self.client_socket.send(json.dumps({"type": "timeout"}).encode('utf-8'))
            page.update()

    def main(self, page: ft.Page):
        page.title = "Quiz App"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        def start_quiz(e):
            name = name_input.value.strip()
            if name:
                self.player_name = name
                page.clean()  # Use clean() instead of clear()
                self.setup_quiz_ui(page)
                if self.connect():
                    self.send_name(name)
                    threading.Thread(target=self.handle_server_messages, args=(page,), daemon=True).start()
                else:
                    self.question_text.value = "Failed to connect to server"
                page.update()

        name_input = ft.TextField(
            label="Enter your name",
            width=300,
            text_align=ft.TextAlign.CENTER
        )

        start_button = ft.ElevatedButton(
            text="Start Quiz",
            on_click=start_quiz
        )

        page.add(
            ft.Column(
                [
                    ft.Text("Welcome to the Quiz!", size=32, weight=ft.FontWeight.BOLD),
                    ft.Container(height=20),
                    name_input,
                    ft.Container(height=10),
                    start_button
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    def setup_quiz_ui(self, page: ft.Page):
        self.score_text = ft.Text(
            f"Score: {self.score}/{self.total_questions}",
            size=20,
            weight=ft.FontWeight.BOLD
        )

        self.timer_text = ft.Text(
            "Time remaining: 5s",
            size=16,
            color=ft.colors.BLUE
        )

        self.question_text = ft.Text(
            size=16,
            text_align=ft.TextAlign.CENTER
        )

        self.options_column = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.result_text = ft.Text(
            size=16,
            color=ft.colors.GREEN,
            text_align=ft.TextAlign.CENTER
        )

        quiz_container = ft.Container(
            content=ft.Column(
                [
                    self.score_text,
                    ft.Container(height=10),
                    self.timer_text,
                    ft.Container(height=20),
                    self.question_text,
                    ft.Container(height=20),
                    self.options_column,
                    ft.Container(height=10),
                    self.result_text
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20
        )
        
        page.add(quiz_container)
        page.update()

    def update_question(self, page: ft.Page):
        if not self.current_question:
            return
            
        self.question_text.value = self.current_question["question"]
        self.options_column.controls.clear()
        self.result_text.value = ""

        for option in self.current_question["options"]:
            self.options_column.controls.append(
                ft.ElevatedButton(
                    text=option,
                    width=200,
                    on_click=lambda e, opt=option: self.send_answer(opt)
                )
            )
        page.update()

    def update_score(self, page: ft.Page):
        self.score_text.value = f"Score: {self.score}/{self.total_questions}"
        page.update()

    def show_result(self, page: ft.Page, message: str):
        self.result_text.value = message
        self.result_text.color = ft.colors.GREEN if "Correct" in message else ft.colors.RED
        page.update()

    def show_welcome_message(self, page: ft.Page, message: str):
        self.question_text.value = message
        page.update()

    def show_final_score(self, page: ft.Page, message: str):
        page.controls.clear()
        
        page.add(
            ft.Column(
                [
                    ft.Text(
                        "Quiz Complete!",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        message,
                        size=20,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        text="Close",
                        width=200,
                        on_click=lambda _: page.window_close()
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        page.update()

def main():
    client = QuizClient()
    ft.app(target=client.main)

if __name__ == "__main__":
    main()
