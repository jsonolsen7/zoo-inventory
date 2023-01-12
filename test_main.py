# import sys
# sys.path.insert(1, './code')
import pytest
import psycopg2
# import sqlite3
# import requests
import os
from app import url, GET_HABITAT

@pytest.fixture
def setup_database():
    """ Fixture to set up the in-memory database with test data """
    conn = psycopg2.connect(url)
    cursor = conn.cursor()
    cursor.execute('''
	    CREATE TABLE IF NOT EXISTS enclosures
        (id INT, name TEXT)''')
    sample_data = [
        (1, 'desert'),
        (2, 'reef'),
    ]
    cursor.execute('''
	    CREATE TABLE IF NOT EXISTS animals
        (id INT, name TEXT, quantity INT, enclosure_id INT)''')
    sample_data2 = [
        (1, 'snake', 4, 1),
        (2, 'scorpion', 10, 1),
        (3, 'seabass', 12, 2),
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

def test_file_exists():
    # Test to make sure all necessary files exists
    assert os.path.exists('./requirements.txt')
    assert os.path.exists('./app.py')