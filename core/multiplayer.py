import socket
import threading


class Server:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.clients = []

    def handle_client(self, conn, addr):
        print(f"Подключился {addr}")
        while True:
            try:
                msg = conn.recv(1024).decode()
                if not msg:
                    break
                print(f"{addr}: {msg}")
                # рассылаем всем клиентам
                for c in self.clients:
                    if c != conn:
                        c.send(msg.encode())
            except Exception:
                break
        conn.close()
        self.clients.remove(conn)
        print(f"{addr} отключился")

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()
        print(f"Сервер запущен на {self.host}:{self.port}")

        while True:
            conn, addr = server.accept()
            self.clients.append(conn)
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()


class Client:
    def __init__(self, host, port=5555):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

    def receive_messages(self):
        while True:
            try:
                msg = self.client.recv(1024).decode()
                if msg:
                    print("Сервер:", msg)
            except Exception:
                break

    def start(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()
        while True:
            msg = input()
            self.client.send(msg.encode())


if __name__ == "__main__":
    mode = input("Выберите режим (server/client): ").strip().lower()
    if mode == "server":
        Server().start()
    elif mode == "client":
        host = input("Введите IP хоста: ").strip()
        Client(host).start()
    else:
        print("Неверный режим. Введите 'server' или 'client'.")
