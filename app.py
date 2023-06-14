from flask import Flask, request, jsonify, make_response
from flask_httpauth import HTTPBasicAuth
from base64 import b64decode
from configparser import ConfigParser
import psycopg2
import psycopg2.extras 
import jwt
import datetime

def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

params = config()

app =  Flask(__name__)
app.config.from_pyfile('config.py')
auth = HTTPBasicAuth()

@app.route('/', methods = ['GET'])
def index():
    return "Welcome to Users!"


@app.route('/api/register', methods=['POST'])
def register():

    # collect user info
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')

    # check if the request is valid
    if username is None or email is None or password is None: 
        return make_response(jsonify({"message":"insufficient data"}), 400)
    
    conn = psycopg2.connect(**params)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
    # check if user already exists
    cur.execute("select exists(select 1 from info where username='" + username + "')")
    if(cur.fetchall()[0]['exists'] is True):
        return make_response(jsonify({"message":"user exists"}), 400)
    
    # insert user 
    cur.execute("insert into info values ('" + username + "','" 
                       + email + "', crypt('" + password + "', gen_salt('bf')));")
    conn.commit()

    cur.close()
    conn.close()
    
    return make_response(jsonify({"message": "success"}), 201)


@auth.verify_password
def verify_password(username_or_token, password):

    conn = psycopg2.connect(**params)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("select exists(select 1 from info where username='" + 
                       username_or_token + "' AND password=crypt('" + password + "', password))")
    
    if(cur.fetchall()[0]['exists'] is True): # username, password verification
        return True
    else: # token verification
        try:
            data = jwt.decode(username_or_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except Exception as err:
            return False

        # check if the corresponding user exists 
        cur.execute("select exists(select 1 from info where username='" + data["name"] + "');")
        if(cur.fetchall()[0]['exists'] is True): 
            return True

    return False 


@app.route('/api/users', methods=['GET'])
def users():
    
    conn = psycopg2.connect(**params)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # retrieves all users
    cur.execute("select username, email, active, created from info;")
        
    response = jsonify(cur.fetchall())

    cur.close()
    conn.close()

    return response


@app.route('/api/token', methods=['GET'])
@auth.login_required
def token():

    # gets the username
    value = request.headers['Authorization'].encode('utf-8')
    try:
        credentials = value.split(b' ', 1)[1]
        encoded_username = b64decode(credentials).split(b':', 1)[0]
    except (ValueError, TypeError):
        return None
    
    username = encoded_username.decode('utf-8')

    # creates a token 
    token  = jwt.encode({"name": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    
    return jsonify({ 'token': token })


@app.route('/api/delete/<string:username>', methods=['DELETE'])
@auth.login_required
def delete(username):

    conn = psycopg2.connect(**params)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("select exists(select 1 from info where username='" + username + "')")

    # check if user already exists
    if(cur.fetchall()[0]['exists'] is False):
        return make_response(jsonify({"message":"error"}), 400)

    # delete user
    cur.execute("delete from info where username = '"+ username +"';")
    
    conn.commit()
    cur.close()
    conn.close()
    
    return make_response(jsonify({"message":"success"}), 200)


@app.route('/api/activate/<string:username>', methods=['PUT'])
@auth.login_required
def activate(username):

    conn = psycopg2.connect(**params)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cur.execute("select exists(select 1 from info where username='" + username + "')")

    # check if user already exists
    if(cur.fetchall()[0]['exists'] is False):
        return make_response(jsonify({"message":"user does not exist"}), 400)

    # update status
    cur.execute("update info set active =true where username = '" + username + "';")

    conn.commit()
    cur.close()
    conn.close()
    
    return make_response(jsonify({"message": "success"}), 200)


@app.route('/api/deactivate/<string:username>', methods=['PUT'])
@auth.login_required
def deactivate(username):

    conn = psycopg2.connect(**params)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("select exists(select 1 from info where username='" + username + "')")

    # check if user already exists
    if(cur.fetchall()[0]['exists'] is False):
        return make_response(jsonify({"message": "error"}), 400)

    # update status
    cur.execute("update info set active = false where username = '" + username + "';")
    
    conn.commit()
    cur.close()
    conn.close()
    
    return make_response(jsonify({"message":"success"}), 200)


if __name__=="__main__": 
    app.run()