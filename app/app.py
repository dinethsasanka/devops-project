from flask import Flask, request, redirect, url_for, render_template
import mysql.connector
import os

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "notesuser"),
        password=os.getenv("DB_PASSWORD", "notespass"),
        database=os.getenv("DB_NAME", "notesdb")
    )

@app.route("/")
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notes ORDER BY id DESC")
    notes = cursor.fetchall()
    db.close()
    return render_template("index.html", notes=notes)

@app.route("/add", methods=["POST"])
def add():
    content = request.form.get("content")
    if content:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO notes (content) VALUES (%s)", (content,))
        db.commit()
        db.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:note_id>")
def delete(note_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    db.commit()
    db.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)