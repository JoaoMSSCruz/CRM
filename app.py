from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import psycopg2
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = "vhv387g3ytv87y4589v34"


# Ligação à base de dados
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="crm_pessoal",
        user="postgres",
        password="kRti8421"
    )


#Tela e recursos para o Sign In
@app.route("/")
def sign_in():
    return render_template("index.html")

@app.route("/receive_sign_in", methods=["POST"])
def receive_sign_in():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verifica se as credenciais existem
        cursor.execute(
            "SELECT * FROM Users WHERE username = %s AND password = %s",
            (username, password)
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session["username"] = username
            session["user_id"] = user[0]  # se user[0] for o id
            session["is_admin"] = user[3]   
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "failure"})
    
    except Exception as e:
        print("DB error:", e)
        return jsonify({"status": "failure"})


#Tela e recursos para o Sign Up
@app.route("/sign_up")
def sign_up():
    return render_template("sign_up.html")


@app.route("/receive_sign_up", methods=["POST"])
def receive_sign_up():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Insere o novo utilizador
        cursor.execute(
            "INSERT INTO Users (username, password) VALUES (%s, %s)",
            (username, password)
        )

        conn.commit()  # ← IMPORTANTE: grava as alterações na base de dados

        cursor.close()
        conn.close()

        return jsonify({"status": "success"})

    
    except Exception as e:
        print("DB error:", e)
        return jsonify({"status": "failure"})
    


#Tela e recursos do Selection Menu
@app.route("/selection_menu")
def selection_menu():
    if "username" not in session:
        return redirect(url_for("sign_in"))
    
    return render_template("selection_menu.html", username=session["username"])



#Tela e recursos do Manage Clients
@app.route("/manage_clients")
def manage_clients():
    if "username" not in session:
        return redirect(url_for("sign_in"))

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, date, email, number, nif, address, obs, active, company
            FROM Clients
        """)
        rows = cursor.fetchall()

        # Nomeia as colunas para usar no template
        clients = [
            {
                "name": r[0],
                "company": r[8],
                "date": r[1],
                "email": r[2],
                "number": r[3],
                "nif": r[4],
                "address": r[5],
                "obs": r[6],
                "active": r[7]
            }
            for r in rows
        ]

        cursor.close()
        conn.close()

        return render_template("manage_clients.html", clients=clients)

    except Exception as e:
        print("DB error:", e)
        return "Erro ao carregar os clientes"


@app.route("/add_client_form")
def add_client_form():
    if "username" not in session:
        return redirect(url_for("sign_in"))
    
    return render_template("add_client.html")

from flask import request, jsonify

@app.route("/add_client", methods=["POST"])
def add_client():
    if "username" not in session:
        return jsonify({"status": "unauthorized"})

    data = request.get_json()

    name = data.get("name")
    company = data.get("company")
    date = data.get("date")
    email = data.get("email")
    phone = data.get("phone")
    nif = data.get("nif")
    address = data.get("address")
    obs = data.get("obs")
    active = data.get("active", False)

    if not re.match(r"^[A-Za-zÀ-ÿ\s'-]+$", name):
        return jsonify({"status": "error", "message": "Name cannot contain numbers or special characters."})

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid date format. Use YYYY-MM-DD."})

    if not email and not phone:
        return jsonify({"status": "error", "message": "Email or phone is required."})

    if phone and not re.match(r"^\d{9}$", phone):
        return jsonify({"status": "error", "message": "Phone number must be 9 digits."})

    if nif:
        if not re.match(r"^\d{9}$", nif):
            return jsonify({"status": "error", "message": "NIF must be 9 digits."})


    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Clients (name, company, date, email, number, nif, address, obs, active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, company, date, email, phone, nif, address, obs, active))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success"})

    except Exception as e:
        print("DB error:", e)
        return jsonify({"status": "error", "message": "DB insertion failed"})
    


@app.route("/add_service_form")
def add_service_form():
    if "username" not in session:
        return redirect(url_for("sign_in"))

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name FROM Clients WHERE active = TRUE")
        clients = cursor.fetchall()

        cursor.execute("SELECT id, username FROM Users")
        workers = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            "add_service.html",
            clients=clients,
            workers=workers,
            is_admin=session.get("is_admin"),
            current_user=session.get("username")
        )

    except Exception as e:
        print("DB error:", e)
        return "Erro ao carregar dados"

    

from flask import request, jsonify

@app.route("/add_service", methods=["POST"])
def add_service():
    if "username" not in session:
        return jsonify({"status": "unauthorized"})

    data = request.get_json()

    date = data.get("date")
    client = data.get("client")
    worker = data.get("worker")
    description = data.get("description")
    duration = data.get("duration")
    cost = data.get("cost")

    try:
        duration = float(duration)
        cost = float(cost)
        if duration < 0 or cost < 0:
            return jsonify({"status": "error", "message": "Duration and cost must be non-negative!"})
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Duration and cost must be numeric values!"})

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Se o worker for um username (caso do utilizador não admin)
        if not str(worker).isdigit():
            cursor.execute("SELECT id FROM Users WHERE username = %s", (worker,))
            result = cursor.fetchone()
            if result:
                worker_id = result[0]
            else:
                return jsonify({"status": "error", "message": "Worker username not found"})
        else:
            worker_id = int(worker)  # Admin já enviou o ID do worker

        cursor.execute("""
            INSERT INTO Services (date, client, worker, description, duration, cost)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (date, client, worker_id, description, duration, cost))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success"})

    except Exception as e:
        print("DB error:", e)
        return jsonify({"status": "error", "message": "DB insertion failed"})



@app.route("/manage_services")
def manage_services():
    if "username" not in session:
        return redirect(url_for("sign_in"))

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                s.date,
                c.name AS client_name,
                s.worker,
                s.description,
                s.duration,
                s.cost
            FROM Services s
            JOIN Clients c ON s.client = c.id
        """)
        rows = cursor.fetchall()

        services = [
            {
                "date": r[0],
                "client": r[1],
                "worker": r[2],
                "description": r[3],
                "duration": r[4],
                "cost": r[5]
            }
            for r in rows
        ]

        cursor.close()
        conn.close()

        return render_template("manage_services.html", services=services)

    except Exception as e:
        print("DB error:", e)
        return "Erro ao carregar os serviços"


#Recursos do Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("sign_in"))



#Função principal que corre o código
if __name__ == "__main__":
    app.run(debug=True)