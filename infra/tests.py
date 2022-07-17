import pytest
import requests

def test_app_is_available():
    response = requests.get('http://127.0.0.1/recipes')
    assert response.ok
