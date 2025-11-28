from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, random, time

app = Flask(__name__)
CORS(app)

DB_PATH = "/data/licenses.db"
CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            key TEXT PRIMARY KEY,
            created_at INTEGER
        )
    """)
    conn.commit()
    conn.close()

def generate_segment():
    return "".join(random.choice(CHARS) for _ in range(4))

def generate_key():
    return "-".join(generate_segment() for _ in range(4))

def save_key(key):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO licenses VALUES (?, ?)", (key, int(time.time())))
    conn.commit()
    conn.close()

def key_exists(key):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM licenses WHERE key = ?", (key,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

@app.route("/generate", methods=["POST"])
def generate():
    key = generate_key()
    save_key(key)
    return jsonify({"key": key})

@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json(force=True)
    key = data.get("key", "").strip().upper()
    return jsonify({"valid": key_exists(key)})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080)
