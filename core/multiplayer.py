import socket
import threading
import json


class Server:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.clients = []          # [(conn, player_id), ...]
        self.players = {}          # player_id -> данные
        self.next_id = 1           # уникальные ID
        self.lock = threading.Lock()

    def handle_client(self, conn, addr):
        print(f"{addr} подключился")
        player_id = f"player{len(self.clients)+1}"
        with self.lock:
            self.players[player_id] = {"x": 100, "y": 100, "angle": 0}
            self.clients.append((conn, player_id))

        # отправляем подключившемуся клиенту его player_id
        try:
            init_msg = json.dumps({
                "type": "init",
                "player_id": player_id
            }).encode() + b"\n"
            conn.send(init_msg)
        except Exception:
            pass

        try:
            buffer = ""
            while True:
                try:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    buffer += chunk.decode()

                    # обрабатываем все полные сообщения, разделенные '\n'
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                        except Exception:
                            continue
                        if isinstance(data, dict):
                            with self.lock:
                                self.players[player_id] = data
                except ConnectionResetError:
                    break
                except Exception:
                    pass

                pass

        finally:
            conn.close()
            # убираем отключившегося игрока
            with self.lock:
                self.clients = [
                    (c, pid) for c, pid in self.clients if c != conn
                ]
                if player_id in self.players:
                    del self.players[player_id]
            print(f"{addr} отключился")

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()
        print(f"Сервер запущен на {self.host}:{self.port}")
        # Запускаем поток, который периодически рассылает состояние всем клиентам

        def broadcaster():
            import time
            while True:
                try:
                    with self.lock:
                        state = dict(self.players)
                        clients = list(self.clients)
                    if state:
                        data = json.dumps(state).encode() + b"\n"
                        for c, pid in clients:
                            try:
                                c.send(data)
                            except Exception:
                                pass
                except Exception:
                    pass
                time.sleep(1 / 30)  # 30 Hz

        threading.Thread(target=broadcaster, daemon=True).start()

        while True:
            conn, addr = server.accept()
            t = threading.Thread(
                target=self.handle_client,
                args=(conn, addr),
                daemon=True,
            )
            t.start()


class Client:
    def __init__(self, host, port=5555):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        self.state = {}      # player_id -> {"x": ..., "y": ..., "angle": ...}
        self.player_id = None
        threading.Thread(target=self.receive_loop, daemon=True).start()

    def send_action(self, action):
        try:
            self.client.send(json.dumps(action).encode() + b"\n")
        except Exception:
            pass

    def receive_loop(self):
        buffer = ""
        while True:
            try:
                chunk = self.client.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                    except Exception:
                        continue

                    # если это инициализационное сообщение с назначенным id
                    if isinstance(data, dict) and data.get("type") == "init":
                        self.player_id = data.get("player_id")
                    else:
                        # ожидаем здесь словарь со всем состоянием игроков
                        if isinstance(data, dict):
                            self.state = data
            except Exception:
                break


if __name__ == "__main__":
    mode = input("Выберите режим (server/client): ").strip().lower()
    if mode == "server":
        Server().start()
    elif mode == "client":
        host = input("Введите IP хоста: ").strip()
        Client(host)
    else:
        print("Неверный режим. Введите 'server' или 'client'.")
