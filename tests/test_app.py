"""Unit tests for Flask ToDo app."""
import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_app_import():
    """Test that app can be imported."""
    assert app is not None


def test_app_responds():
    """Smoke test: app responds to a request."""
    app.config['TESTING'] = True
    with app.test_client() as c:
        rv = c.get('/')
    assert rv.status_code in [200, 302]


def test_index_route(client):
    """Test the index route returns todos."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'todos' in data
    assert 'message' in data
    assert data['message'] == 'Flask ToDo App'


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data


def test_get_todos(client):
    """Test getting todos."""
    response = client.get('/todos')
    assert response.status_code == 200
    todos = response.get_json()
    assert isinstance(todos, list)


def test_add_todo(client):
    """Test adding a new todo."""
    response = client.post('/todos', json={'title': 'New task'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'New task'
    assert data['completed'] is False


def test_add_todo_missing_title(client):
    """Test adding a todo without a title."""
    response = client.post('/todos', json={})
    assert response.status_code == 400


def test_update_todo(client):
    """Test updating a todo."""
    # First, add a todo
    add_response = client.post('/todos', json={'title': 'Task to update'})
    todo_id = add_response.get_json()['id']
    
    # Update it
    response = client.put(f'/todos/{todo_id}', json={
        'title': 'Updated task',
        'completed': True
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Updated task'
    assert data['completed'] is True


def test_delete_todo(client):
    """Test deleting a todo."""
    # First, add a todo
    add_response = client.post('/todos', json={'title': 'Task to delete'})
    todo_id = add_response.get_json()['id']
    
    # Delete it
    response = client.delete(f'/todos/{todo_id}')
    assert response.status_code == 200


def test_404_not_found(client):
    """Test 404 error handling."""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
