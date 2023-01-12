import pytest
import psycopg2
import os
from app import url, create_app

@pytest.fixture
def setup_database():
    """ Fixture to set up the in-memory database with test data """
    conn = psycopg2.connect(url)
    print(conn.info)
    cursor = conn.cursor()
    print(cursor)
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
    print(result)
    assert len(list(result)) == 2
    cursor.execute('SELECT * FROM animals')
    result2 = cursor.fetchmany(3)
    print(result2)
    assert len(list(result2)) == 3

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_request_home(client):
    print("HOME get request")
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the Safari Park! Hope you're not afraid of lions, tigers, bears, and much more!" in response.data

def test_request_habitat(client):
    print("HABITAT get request")
    response = client.get("/api/habitat/1")
    json_response = response.get_json()
    assert response.status_code == 201
    assert json_response == {'desert': [{'animal_id': 1, 'name': 'snake', 'quantity': 4}, {'animal_id': 2, 'name': 'scorpion', 'quantity': 10}]}

@pytest.mark.skip
def test_file_exists():
    # Test to make sure all necessary files exists
    assert os.path.exists('./requirements.txt')
    assert os.path.exists('./app.py')

## NOT TDD tests
# def test_get_home():
#     # Testing home route
#     response = app.test_client().get('/')
#     assert response.status_code == 200
#     assert response.data == b"Welcome to the Safari Park! Hope you're not afraid of lions, tigers, bears, and much more!"

# def test_get_habitat():
#     # Testing habitat get request
#     with app.test_client() as connection:
#         response = connection.get('/api/habitat/desert')
#         json_response = response.get_json()
#         assert response.status_code == 201
#         assert json_response == {'desert': [{'animal_id': 1, 'name': 'snake', 'quantity': 4}, {'animal_id': 2, 'name': 'scorpion', 'quantity': 10}]}

# def test_post_enclosure():
#     # Testing enclosure post request
#     with app.test_client() as connection:
#         response = connection.post('/api/enclosure', json={
#             "name": "reef"
#         })
#         json_response = response.get_json()
#         assert response.status_code == 201
#         assert json_response == {'id': 6, 'message': 'reef habitat created.'}