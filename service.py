from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from datetime import datetime
import typing as tp
import sqlite3
import json
import os


class Record:
    def __init__(self, timestamp: datetime, temperature: int, humidity: int):
        self.timestamp = timestamp
        self.temperature = temperature
        self.humidity = humidity

    def as_json(self) -> tp.Dict[str, tp.Any]:
        return {
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "temperature": self.temperature,
            "humidity": self.humidity
        }


class Repository:
    __instance: tp.Optional["Repository"] = None

    def __new__(cls):
        if Repository.__instance is None:
            Repository.__instance = object.__new__(Repository)
        return Repository.__instance

    def __init__(self):
        create_tables = not os.path.isfile("stuff.db")
        self.connection = sqlite3.connect("stuff.db")
        if create_tables:
            print("creating db")
            c = self.connection.cursor()
            c.execute("""CREATE TABLE Temperatures(timestamp TEXT, temperature INTEGER, humidity INTEGER)""")
            self.connection.commit()

    def insert(self, timestamp: datetime, temperature: int, humidity: int):
        try:
            c = self.connection.cursor()
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
            c.execute("INSERT INTO Temperatures VALUES (?, ?, ?)", (timestamp, temperature, humidity))
            self.connection.commit()
        except Exception as e:
            print(e)

    def get_all(self):
        c = self.connection.cursor()
        for ts, temp, hum in c.execute("SELECT * FROM Temperatures"):
            yield Record(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.%f"), temp, hum)

    def __del__(self):
        self.connection.close()


REPO = Repository()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
        else:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            data = json.dumps([r.as_json() for r in REPO.get_all()])
            self.wfile.write(data.encode("ascii"))

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        length = int(self.headers["Content-length"])
        self.end_headers()
        x = self.rfile.read(length)
        data = json.loads(x.decode("utf-8"))
        REPO.insert(datetime.now(), int(data["temp"]), int(data["humidity"]))


def main():
    port = int(os.environ.get("PORT", "3000"))
    with TCPServer(("", port), Handler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()


if __name__ == '__main__':
    main()
