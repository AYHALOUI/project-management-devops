from flask import Flask, request, jsonify
import psycopg2
import os
import time
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge

app = Flask(__name__)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)

# Custom metrics with proper initialization
database_connections = Gauge(
    'database_connections_active', 
    'Active database connections'
)

# Database connection with proper error handling
def get_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'projectdb'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password')
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def close_db(conn):
    if conn:
        conn.close()

# Initialize database tables
def init_db():
    conn = get_db()
    if conn:
        cur = conn.cursor()
        
        # Create tables if they don't exist
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
        close_db(conn)
        print("✅ Database initialized successfully")
    else:
        print("❌ Failed to initialize database")

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    start_time = time.time()
    
    # Check database connectivity
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT 1')
            db_status = "healthy"
            close_db(conn)
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
            close_db(conn)
    else:
        db_status = "connection_failed"
    
    response_time = time.time() - start_time
    
    return jsonify({
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "response_time": response_time,
        "version": "1.0.0"
    })

@app.route('/projects', methods=['GET'])
def get_projects():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    try:
        cur = conn.cursor()
        cur.execute('SELECT id, name, description FROM projects')
        projects = cur.fetchall()
        close_db(conn)
        
        return jsonify([
            {'id': p[0], 'name': p[1], 'description': p[2]} 
            for p in projects
        ])
    except Exception as e:
        close_db(conn)
        return jsonify({'error': str(e)}), 500

@app.route('/projects', methods=['POST'])
def create_project():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
        
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    try:
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO projects (name, description) VALUES (%s, %s) RETURNING id', 
            (data['name'], data.get('description', ''))
        )
        project_id = cur.fetchone()[0]
        conn.commit()
        close_db(conn)
        
        return jsonify({
            'id': project_id,
            'name': data['name'],
            'description': data.get('description', ''),
            'message': 'Project created successfully'
        }), 201
    except Exception as e:
        close_db(conn)
        return jsonify({'error': str(e)}), 500

@app.route('/projects/<int:project_id>/tasks', methods=['GET'])
def get_tasks(project_id):
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    try:
        cur = conn.cursor()
        cur.execute(
            'SELECT id, title, completed FROM tasks WHERE project_id = %s', 
            (project_id,)
        )
        tasks = cur.fetchall()
        close_db(conn)
        
        return jsonify([
            {'id': t[0], 'title': t[1], 'completed': t[2]} 
            for t in tasks
        ])
    except Exception as e:
        close_db(conn)
        return jsonify({'error': str(e)}), 500

@app.route('/projects/<int:project_id>/tasks', methods=['POST'])
def create_task(project_id):
    data = request.json
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
        
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    try:
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO tasks (project_id, title, completed) VALUES (%s, %s, %s) RETURNING id', 
            (project_id, data['title'], False)
        )
        task_id = cur.fetchone()[0]
        conn.commit()
        close_db(conn)
        
        return jsonify({
            'id': task_id,
            'project_id': project_id,
            'title': data['title'],
            'completed': False,
            'message': 'Task created successfully'
        }), 201
    except Exception as e:
        close_db(conn)
        return jsonify({'error': str(e)}), 500

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    if not data or 'completed' not in data:
        return jsonify({'error': 'Completed status is required'}), 400
        
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    try:
        cur = conn.cursor()
        cur.execute(
            'UPDATE tasks SET completed = %s WHERE id = %s RETURNING title', 
            (data['completed'], task_id)
        )
        result = cur.fetchone()
        if not result:
            close_db(conn)
            return jsonify({'error': 'Task not found'}), 404
            
        conn.commit()
        close_db(conn)
        
        return jsonify({
            'id': task_id,
            'title': result[0],
            'completed': data['completed'],
            'message': 'Task updated successfully'
        })
    except Exception as e:
        close_db(conn)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()  # Initialize tables on startup
    app.run(host='0.0.0.0', port=5000, debug=False)
