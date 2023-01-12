from flask import Flask, request
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()
url = os.getenv("DB_URL")

def create_app():

    app = Flask(__name__)

    connection = psycopg2.connect(url)

    CREATE_ENCLOSURES_TABLE = (
        "CREATE TABLE IF NOT EXISTS enclosures (id SERIAL PRIMARY KEY, name TEXT);"
    )

    CREATE_ANIMALS_TABLE = (
        "CREATE TABLE IF NOT EXISTS animals (id SERIAL PRIMARY KEY, name TEXT, quantity INTEGER, enclosure_id INTEGER, FOREIGN KEY(enclosure_id) REFERENCES enclosures(id) ON DELETE CASCADE);"
    )

    INSERT_ENCLOSURE_RETURN_ID = "INSERT INTO enclosures (name) VALUES (%s) RETURNING id;"
    INSERT_ANIMAL = (
        "INSERT INTO animals (name, quantity, enclosure_id) VALUES (%s, %s, %s);"
    )

    GET_ONE_ENCLOSURE = "SELECT name FROM enclosures WHERE id = (%s)"

    GET_HABITAT_BY_ID = "SELECT enclosures.name, animals.id, animals.name, animals.quantity FROM enclosures INNER JOIN animals ON enclosures.id=animals.enclosure_id WHERE enclosures.id = (%s);"
    GET_HABITAT_BY_NAME = "SELECT enclosures.name, animals.id, animals.name, animals.quantity FROM enclosures INNER JOIN animals ON enclosures.id=animals.enclosure_id WHERE enclosures.name = (%s);"

    @app.get("/")
    def home():
        return "Welcome to the Safari Park! Hope you're not afraid of lions, tigers, bears, and much more!"

    @app.post("/api/enclosure")
    def create_enclosure():
        data = request.get_json()
        name = data["name"]
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_ENCLOSURES_TABLE)
                cursor.execute(INSERT_ENCLOSURE_RETURN_ID, (name,))
                enclosure_id = cursor.fetchone()[0]
            return {"id": enclosure_id, "message": f"{name} habitat created."}, 201

    @app.post("/api/animal")
    def add_animal():
        data = request.get_json()
        name = data["name"]
        quantity = data["quantity"]
        enclosure_id = data["enclosure_id"]
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_ANIMALS_TABLE)
                cursor.execute(INSERT_ANIMAL, (name, quantity, enclosure_id))
            return {"message": "New species added!"}, 201

    @app.get("/api/habitat/<enclosure_id_or_name>")
    def get_habitat(enclosure_id_or_name):
        with connection:
            with connection.cursor() as cursor:
                if request.view_args['enclosure_id_or_name'].isdigit():
                    cursor.execute(GET_HABITAT_BY_ID, (enclosure_id_or_name,))
                else:
                    name = request.view_args['enclosure_id_or_name'].replace("-", " ")
                    cursor.execute(GET_HABITAT_BY_NAME, (name,))
                animals = []
                habitat = ""
                for result in cursor:
                    habitat = result[0]
                    animals.append({"animal_id": result[1], "name": result[2], "quantity": result[3]})
            return {habitat: animals}, 201
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)