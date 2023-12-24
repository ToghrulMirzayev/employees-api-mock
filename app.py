from flask import Flask, request, jsonify, render_template
from flasgger import Swagger
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_url_path='', static_folder='static')
app.config['STATICFILES_DIRS'] = [
    os.path.join(app.static_folder, 'files')
]

swagger = Swagger(app)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
USERNAME = os.getenv("APP_SUPERUSER")
PASSWORD = os.getenv("APP_PASSWORD")

employees_data = []
skills_data = []

if os.getenv("DOCKER"):
    HOST = '0.0.0.0'
    PORT = 80
else:
    HOST = '127.0.0.1'
    PORT = 5000


@app.route('/generate-token', methods=['POST'])
def generate_token():
    """
    Generate JWT token for authentication.
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              description: username
            password:
              type: string
              description: password
    responses:
      200:
        description: JWT token generated successfully
        examples:
          token: "<your_generated_token>"
      401:
        description: Invalid username or password
    """
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
    """
    Create a new employee.
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              description: The name of the employee
            organization:
              type: string
              description: The organization of the employee
            role:
              type: string
              description: The role of the employee
    responses:
      200:
        description: Employee created
        schema:
          type: object
          properties:
            name:
              type: string
              description: The name of the created employee
            organization:
              type: string
              description: The organization of the created employee
            role:
              type: string
              description: The role of the created employee
            employeeId:
              type: integer
              description: The unique identifier of the created employee
      401:
        description: Unauthorized access
    """
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
    """
    Get the list of all employees.

    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
    responses:
      200:
        description: List of employees retrieved
        schema:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
                description: The name of the employee
              organization:
                type: string
                description: The organization of the employee
              role:
                type: string
                description: The role of the employee
              employeeId:
                type: integer
                description: The unique identifier of the employee
      401:
        description: Unauthorized access
    """
    auth_token = request.headers.get('Authorization')
    if not auth_token or not auth_token.startswith('Bearer '):
        return jsonify({'message': 'Unauthorized'}), 401
    token = auth_token.split(' ')[1]
    if not validate_token(token):
        return jsonify({'message': 'Invalid token'}), 401

    return jsonify(employees_data)


@app.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """
    Get details of a specific employee.

    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
      - name: employee_id
        in: path
        type: integer
        required: true
        description: The unique identifier of the employee
    responses:
      200:
        description: Employee details retrieved
        schema:
          type: object
          properties:
            name:
              type: string
              description: The name of the employee
            organization:
              type: string
              description: The organization of the employee
            role:
              type: string
              description: The role of the employee
            employeeId:
              type: integer
              description: The unique identifier of the employee
      401:
        description: Unauthorized access
      404:
        description: Employee not found
    """
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
    """
    Update details of a specific employee.

    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
      - name: employee_id
        in: path
        type: integer
        required: true
        description: The unique identifier of the employee
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              description: The updated name of the employee
            organization:
              type: string
              description: The updated organization of the employee
            role:
              type: string
              description: The updated role of the employee
    responses:
      200:
        description: Employee updated
      401:
        description: Unauthorized access
      404:
        description: Employee not found
    """
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
    """
    Delete a specific employee.
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
      - name: employee_id
        in: path
        type: integer
        required: true
        description: The unique identifier of the employee to be deleted
    responses:
      200:
        description: Employee deleted
      401:
        description: Unauthorized access
      404:
        description: Employee not found
    """
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


@app.route('/about', methods=['GET'])
def get_app_details():
    """
    Get details about the application.
    ---
    responses:
      200:
        description: Application details retrieved
        schema:
          type: object
          properties:
            Code owner:
              type: string
              description: The owner of the code
            App Description:
              type: string
              description: Description of the application
            App version:
              type: string
              description: The version of the application
            Contact details:
              type: array
              items:
                type: string
              description: Contact details for the application owner
    """
    return jsonify({'Code owner': "Toghrul Mirzayev",
                    "App Description": "Playground for backend testing",
                    "App version": "v2.0.0",
                    "Contact details": [
                        "togrul.mirzoev@gmail.com",
                        "https://github.com/ToghrulMirzayev/employees-api-mock"
                    ]})


@app.route('/status', methods=['GET'])
def get_status():
    """
    Get the status of the service.
    ---
    responses:
      200:
        description: Service status retrieved successfully
        schema:
          type: object
          properties:
            status:
              type: string
              description: The status of the service
      401:
        description: Unauthorized access
    """
    return jsonify({'status': "The service is up and running"})


@app.route('/skills', methods=['GET'])
def get_skills():
    """
    Get all skills.
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
    responses:
      200:
        description: List of skills retrieved
        schema:
          type: object
          properties:
            skills:
              type: array
              items:
                type: object
                properties:
                  skillId:
                    type: integer
                    description: The unique identifier of the skill
                  skill:
                    type: string
                    description: The skill name
      401:
        description: Unauthorized access
    """
    auth_token = request.headers.get('Authorization')
    if not auth_token or not auth_token.startswith('Bearer '):
        return jsonify({'message': 'Unauthorized'}), 401
    token = auth_token.split(' ')[1]
    if not validate_token(token):
        return jsonify({'message': 'Invalid token'}), 401

    return jsonify({'skills': skills_data})


@app.route('/skills', methods=['POST'])
def add_skills():
    """
    Add a new skill.
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            skill:
              type: string
              description: The name of the skill
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              skill:
                type: string
                description: The skill name to be added
                example: Java
    responses:
      401:
        description: Unauthorized access
      422:
        description: Missing skill parameter
      201:
        description: Skill added
        schema:
          type: object
          properties:
            message:
              type: string
              description: Confirmation message
    """
    auth_token = request.headers.get('Authorization')
    if not auth_token or not auth_token.startswith('Bearer '):
        return jsonify({'message': 'Unauthorized'}), 401
    token = auth_token.split(' ')[1]
    if not validate_token(token):
        return jsonify({'message': 'Invalid token'}), 401

    data = request.get_json()
    if 'skill' not in data:
        return jsonify({'message': 'Missing skill parameter'}), 422

    new_skill = {
        'skillId': len(skills_data) + 1,
        'skill': data['skill']
    }
    skills_data.append(new_skill)
    return jsonify({'message': 'Skill added'})


@app.route('/skills/<int:skillId>', methods=['GET'])
def get_skill(skillId):
    """
    Get details of a specific skill.
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
      - name: skillId
        in: path
        type: integer
        required: true
        description: The unique identifier of the skill
    responses:
      200:
        description: Skill details retrieved
        schema:
          type: object
          properties:
            skillId:
              type: integer
              description: The unique identifier of the skill
            skill:
              type: string
              description: The skill name
      401:
        description: Unauthorized access
      404:
        description: Skill not found
    """
    auth_token = request.headers.get('Authorization')
    if not auth_token or not auth_token.startswith('Bearer '):
        return jsonify({'message': 'Unauthorized'}), 401
    token = auth_token.split(' ')[1]
    if not validate_token(token):
        return jsonify({'message': 'Invalid token'}), 401

    skill = next((sk for sk in skills_data if sk['skillId'] == skillId), None)
    if skill:
        return jsonify(skill)
    else:
        return jsonify({'error': 'Skill not found'}), 404


@app.route('/skills/<int:skillId>', methods=['DELETE'])
def delete_skill(skillId):
    """
    Delete a specific skill.
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
      - name: skillId
        in: path
        type: integer
        required: true
        description: The unique identifier of the skill
    responses:
      200:
        description: Skill deleted
      401:
        description: Unauthorized access
      404:
        description: Skill not found
    """
    auth_token = request.headers.get('Authorization')
    if not auth_token or not auth_token.startswith('Bearer '):
        return jsonify({'message': 'Unauthorized'}), 401
    token = auth_token.split(' ')[1]
    if not validate_token(token):
        return jsonify({'message': 'Invalid token'}), 401

    skill = next((sk for sk in skills_data if sk['skillId'] == skillId), None)
    if skill:
        skills_data.remove(skill)
        return jsonify({'message': 'Skill deleted'})
    else:
        return jsonify({'error': 'Skill not found'}), 404


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
