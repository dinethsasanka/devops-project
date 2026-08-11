from flask import Flask, jsonify, request
import mysql.connector
import redis
import os
import json

app = Flask(__name__)

# Redis connection
cache = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    decode_responses=True
)

# MariaDB connection
def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "mariadb"),
        user=os.getenv("DB_USER", "notesuser"),
        password=os.getenv("DB_PASSWORD", "notespass"),
        database=os.getenv("DB_NAME", "notesdb")
    )

# Health check endpoint
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "notes-api"})

# Get all notes
@app.route("/api/notes")
def get_notes():
    # Check Redis cache first
    cached = cache.get("all_notes")
    if cached:
        return jsonify({
            "source": "cache",
            "notes": json.loads(cached)
        })

    # Cache miss — query the database
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
    notes = cursor.fetchall()
    db.close()

    # Convert datetime objects to strings for JSON serialization
    for note in notes:
        note["created_at"] = str(note["created_at"])

    # Store in Redis with 60 second expiry
    cache.setex("all_notes", 60, json.dumps(notes))

    return jsonify({
        "source": "database",
        "notes": notes
    })

# Add a note via API
@app.route("/api/notes", methods=["POST"])
def add_note():
    data = request.get_json()
    content = data.get("content")

    if not content:
        return jsonify({"error": "content is required"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO notes (content) VALUES (%s)", (content,))
    db.commit()
    new_id = cursor.lastrowid
    db.close()

    # Invalidate cache so next GET returns fresh data
    cache.delete("all_notes")

    return jsonify({
        "message": "note created",
        "id": new_id
    }), 201

# Delete a note via API
@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    db.commit()
    affected = cursor.rowcount
    db.close()

    if affected == 0:
        return jsonify({"error": "note not found"}), 404

    # Invalidate cache
    cache.delete("all_notes")

    return jsonify({"message": "note deleted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
