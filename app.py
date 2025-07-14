from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Database connection
def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'projectdb'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password')
    )

def inti_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute(''' 
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(id),
            title VARCHAR(255) NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close

@app.route('/projects', methods=['GET'])
def get_projects():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, name, description FROM projects')
    projects = cur.fetchall()
    conn.close()
    return jsonify([{'id': p[0], 'name': p[1], 'description': p[2]} for p in projects])

@app.route('/projects', methods=['POST'])
def create_project():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO projects (name, description) VALUES (%s, %s)', 
                (data['name'], data.get('description', '')))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Project created'}), 201

@app.route('/projects/<int:project_id>/tasks', methods=['GET'])
def get_tasks(project_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, title, completed FROM tasks WHERE project_id = %s', (project_id,))
    tasks = cur.fetchall()
    conn.close()
    return jsonify([{'id': t[0], 'title': t[1], 'completed': t[2]} for t in tasks])

@app.route('/projects/<int:project_id>/tasks', methods=['POST'])
def create_task(project_id):
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (project_id, title, completed) VALUES (%s, %s, %s)', 
                (project_id, data['title'], False))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task created'}), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE tasks SET completed = %s WHERE id = %s', 
                (data['completed'], task_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task updated'})

@app.route("/health")
def health():
    return {"status": "healthy", "message": "DevOps pipeline working!"}

if __name__ == '__main__':
    inti_db()
    app.run(host='0.0.0.0', port=5000)