import pytest
import psycopg2
import os
from app import url, create_app

@pytest.fixture
def setup_database():
    """ Fixture to set up the in-memory database with test data """
    conn = psycopg2.connect(url)
    cursor = conn.cursor()
    cursor.execute('''
	    CREATE TABLE IF NOT EXISTS enclosures
        (id INT, name TEXT)''')
    sample_data = [
        (2, 'rain forest'),
        (3, 'reef'),
    ]
    cursor.execute('''
	    CREATE TABLE IF NOT EXISTS animals
        (id INT, name TEXT, quantity INT, enclosure_id INT)''')
    sample_data2 = [
        (3, 'toucan', 4, 2),
        (4, 'monkey', 10, 2),
        (5, 'seabass', 12, 3),
    ]
    cursor.executemany('INSERT INTO enclosures VALUES(%s, %s)', sample_data)
    cursor.executemany('INSERT INTO animals VALUES(%s, %s, %s, %s)', sample_data2)
    yield conn, cursor

def test_connection(setup_database):
    # Test to make sure that there are items in each database
    conn, cursor = setup_database
    cursor.execute('SELECT * FROM enclosures')
    result = cursor.fetchmany(2)
    assert len(list(result)) == 2
    cursor.execute('SELECT * FROM animals')
    result2 = cursor.fetchmany(3)
    assert len(list(result2)) == 3

@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_request_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the Safari Park! Hope you're not afraid of lions, tigers, bears, and much more!" in response.data

def test_add_enclosure(client):
    test_enclosure = "reef"
    test_data = {
        'name': test_enclosure
    }
    response = client.post("/api/enclosure", json=test_data)
    json_response = response.get_json()
    response_data = json_response['message']
    assert response.status_code == 201
    assert response_data == 'reef habitat created.'

def test_add_animal(client):
    test_animal_name = 'fish'
    test_quantity = 12
    test_enclosure = 1
    test_data = {
        'name': test_animal_name,
        'quantity': test_quantity,
        'enclosure_id': test_enclosure
    }
    response = client.post("/api/animal", json=test_data)
    json_response = response.get_json()
    response_data = json_response['message']
    assert response.status_code == 201
    assert response_data == f"New species, {test_animal_name}, added to enclosure {test_enclosure}!"

# @pytest.mark.skip
def test_request_habitat(client):
    response = client.get("/api/habitat/1")
    json_response = response.get_json()
    assert response.status_code == 201
    assert json_response == {'reef': [{'animal_id': 1, 'name': 'fish', 'quantity': 12}]}

def test_file_exists():
    # Test to make sure all necessary files exists
    assert os.path.exists('./requirements.txt')
    assert os.path.exists('./app.py')