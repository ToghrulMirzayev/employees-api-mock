from flask import Flask, request, jsonify, render_template
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_url_path='', static_folder='static')
app.config['STATICFILES_DIRS'] = [
    os.path.join(app.static_folder, 'files')
]

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
USERNAME = os.getenv("APP_SUPERUSER")
PASSWORD = os.getenv("APP_PASSWORD")

employees_data = []


@app.route('/generate-token', methods=['POST'])
def generate_token():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not authenticate_user(username, password):
        return jsonify({'message': 'Invalid username or password'}), 401
    token = jwt.encode({'username': username}, JWT_SECRET_KEY, algorithm='HS256')
    encoded_token = token
    return jsonify({'token': encoded_token})


@app.route('/get_environment_variables')
def get_environment_variables():
    return jsonify({
        'username': USERNAME,
        'password': PASSWORD,
        'jwt_secret_key': JWT_SECRET_KEY
    })


def authenticate_user(username, password):
    return username == USERNAME and password == PASSWORD


@app.route('/employees', methods=['POST'])
def create_employee():
    auth_token = request.headers.get('Authorization')
    if not auth_token or not auth_token.startswith('Bearer '):
        return jsonify({'message': 'Unauthorized'}), 401
    token = auth_token.split(' ')[1]
    if not validate_token(token):
        return jsonify({'message': 'Invalid token'}), 401

    data = request.get_json()
    name = data.get('name')
    organization = data.get('organization')
    role = data.get('role')

    new_employee = {
        'name': name,
        'organization': organization,
        'role': role,
        'employeeId': len(employees_data) + 1,
    }

    employees_data.append(new_employee)
    return jsonify(new_employee)


@app.route('/employees', methods=['GET'])
def get_employees():
    auth_token = request.headers.get('Authorization')
    if not auth_token or not auth_token.startswith('Bearer '):
        return jsonify({'message': 'Unauthorized'}), 401
    token = auth_token.split(' ')[1]
    if not validate_token(token):
        return jsonify({'message': 'Invalid token'}), 401

    return jsonify(employees_data)


@app.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    auth_token = request.headers.get('Authorization')
    if not auth_token or not auth_token.startswith('Bearer '):
        return jsonify({'message': 'Unauthorized'}), 401
    token = auth_token.split(' ')[1]
    if not validate_token(token):
        return jsonify({'message': 'Invalid token'}), 401

    employee = next((emp for emp in employees_data if emp['employeeId'] == employee_id), None)
    if employee:
        return jsonify(employee)
    return jsonify({'error': 'Employee not found'}), 404


@app.route('/employees/<int:employee_id>', methods=['PUT', 'PATCH'])
def update_employee(employee_id):
    auth_token = request.headers.get('Authorization')
    if not auth_token or not auth_token.startswith('Bearer '):
        return jsonify({'message': 'Unauthorized'}), 401
    token = auth_token.split(' ')[1]
    if not validate_token(token):
        return jsonify({'message': 'Invalid token'}), 401

    data = request.get_json()
    name = data.get('name')
    organization = data.get('organization')
    role = data.get('role')

    employee = next((emp for emp in employees_data if emp['employeeId'] == employee_id), None)
    if employee:
        if request.method == 'PUT':
            employee['name'] = name
            employee['organization'] = organization
            employee['role'] = role
        elif request.method == 'PATCH':
            if name:
                employee['name'] = name
            if organization:
                employee['organization'] = organization
            if role:
                employee['role'] = role
        return jsonify({'message': 'Employee updated'})
    return jsonify({'error': 'Employee not found'}), 404


@app.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    auth_token = request.headers.get('Authorization')
    if not auth_token or not auth_token.startswith('Bearer '):
        return jsonify({'message': 'Unauthorized'}), 401
    token = auth_token.split(' ')[1]
    if not validate_token(token):
        return jsonify({'message': 'Invalid token'}), 401

    global employees_data
    employees_data = [emp for emp in employees_data if emp['employeeId'] != employee_id]
    return jsonify({'message': 'Employee deleted'})


def validate_token(token):
    try:
        jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return True
    except jwt.exceptions.DecodeError:
        return False


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()