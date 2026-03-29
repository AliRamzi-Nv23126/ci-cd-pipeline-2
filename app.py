"""Flask ToDo app with basic functionality."""
from flask import Flask, request, jsonify, session, render_template
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# In-memory todo storage (in production, use a database)
todos = {
    'user1': [
        {'id': 1, 'title': 'Buy groceries', 'completed': False},
        {'id': 2, 'title': 'Write tests', 'completed': True},
    ]
}


@app.route('/')
def index():
    """Home page - list todos."""
    user_id = session.get('user_id', 'user1')
    user_todos = todos.get(user_id, [])
    return render_template('dashboard.html', todos=user_todos)


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/todos', methods=['GET'])
def get_todos():
    """Get all todos for the current user."""
    user_id = session.get('user_id', 'user1')
    user_todos = todos.get(user_id, [])
    return jsonify(user_todos), 200


@app.route('/todos', methods=['POST'])
def add_todo():
    """Add a new todo."""
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    user_id = session.get('user_id', 'user1')
    if user_id not in todos:
        todos[user_id] = []

    new_todo = {
        'id': max([t['id'] for t in todos[user_id]], default=0) + 1,
        'title': data['title'],
        'completed': False
    }
    todos[user_id].append(new_todo)
    return jsonify(new_todo), 201


@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo by ID."""
    user_id = session.get('user_id', 'user1')
    user_todos = todos.get(user_id, [])

    for todo in user_todos:
        if todo['id'] == todo_id:
            data = request.get_json()
            if 'title' in data:
                todo['title'] = data['title']
            if 'completed' in data:
                todo['completed'] = data['completed']
            return jsonify(todo), 200

    return jsonify({'error': 'Todo not found'}), 404


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo by ID."""
    user_id = session.get('user_id', 'user1')
    user_todos = todos.get(user_id, [])

    for i, todo in enumerate(user_todos):
        if todo['id'] == todo_id:
            user_todos.pop(i)
            return jsonify({'message': 'Todo deleted'}), 200

    return jsonify({'error': 'Todo not found'}), 404


@app.errorhandler(404)
def not_found(error):
    """404 error handler."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
