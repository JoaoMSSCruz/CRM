from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import psycopg2


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

    return render_template("manage_clients.html")


#Tela e recursos do Manage Services
@app.route("/manage_services")
def manage_services():
    if "username" not in session:
        return redirect(url_for("sign_in"))

    return render_template("manage_services.html")


#Recursos do Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("sign_in"))



#Função principal que corre o código
if __name__ == "__main__":
    app.run(debug=True)