from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

# 数据库连接函数
def get_conn():
    conn = pymysql.connect(
        host='Oneone22.mysql.pythonanywhere-services.com',
        user='Oneone22',
        password='160384Az',
        db='Oneone22$maibox',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
        )
    return conn

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username=%s", (data['username'],))
        if cursor.fetchone():
            return jsonify({'success': False, 'msg': '用户名已存在'})
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (data['username'], data['password']))
        conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (data['username'], data['password']))
        user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'msg': '用户名或密码错误'})

@app.route('/add_friend', methods=['POST'])
def add_friend():
    data = request.json
    user = data['username']
    friend = data['friend']
    conn = get_conn()
    with conn.cursor() as cursor:
        # 查找双方ID
        cursor.execute("SELECT id FROM users WHERE username=%s", (user,))
        user_row = cursor.fetchone()
        cursor.execute("SELECT id FROM users WHERE username=%s", (friend,))
        friend_row = cursor.fetchone()
        if not user_row or not friend_row:
            return jsonify({'success': False, 'msg': '用户不存在'})
        user_id = user_row['id']
        friend_id = friend_row['id']
        # 检查是否已是好友
        cursor.execute("SELECT * FROM friends WHERE user_id=%s AND friend_id=%s", (user_id, friend_id))
        if cursor.fetchone():
            return jsonify({'success': False, 'msg': '已是好友'})
        # 互加好友
        cursor.execute("INSERT INTO friends (user_id, friend_id) VALUES (%s, %s)", (user_id, friend_id))
        cursor.execute("INSERT INTO friends (user_id, friend_id) VALUES (%s, %s)", (friend_id, user_id))
        conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/get_friends', methods=['POST'])
def get_friends():
    data = request.json
    user = data['username']
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE username=%s", (user,))
        user_row = cursor.fetchone()
        if not user_row:
            return jsonify({'success': False, 'msg': '用户不存在'})
        user_id = user_row['id']
        cursor.execute("SELECT u.username FROM friends f JOIN users u ON f.friend_id=u.id WHERE f.user_id=%s", (user_id,))
        friends = [row['username'] for row in cursor.fetchall()]
    conn.close()
    return jsonify({'success': True, 'friends': friends})

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    sender = data['sender']
    receiver = data['receiver']
    msg_type = data['type']
    content = data['content']
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE username=%s", (sender,))
        sender_row = cursor.fetchone()
        cursor.execute("SELECT id FROM users WHERE username=%s", (receiver,))
        receiver_row = cursor.fetchone()
        if not sender_row or not receiver_row:
            return jsonify({'success': False, 'msg': '用户不存在'})
        sender_id = sender_row['id']
        receiver_id = receiver_row['id']
        cursor.execute("INSERT INTO messages (sender_id, receiver_id, type, content) VALUES (%s, %s, %s, %s)",
                       (sender_id, receiver_id, msg_type, content))
        conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/get_messages', methods=['POST'])
def get_messages():
    data = request.json
    user = data['username']
    friend = data['friend']
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE username=%s", (user,))
        user_row = cursor.fetchone()
        cursor.execute("SELECT id FROM users WHERE username=%s", (friend,))
        friend_row = cursor.fetchone()
        if not user_row or not friend_row:
            return jsonify({'success': False, 'msg': '用户不存在'})
        user_id = user_row['id']
        friend_id = friend_row['id']
        cursor.execute("""
            SELECT sender_id, type, content, timestamp
            FROM messages
            WHERE (sender_id=%s AND receiver_id=%s) OR (sender_id=%s AND receiver_id=%s)
            ORDER BY timestamp ASC
        """, (user_id, friend_id, friend_id, user_id))
        messages = []
        for row in cursor.fetchall():
            sender = user if row['sender_id'] == user_id else friend
            # MySQL的TIMESTAMP是UTC时间，转成ISO格式并添加Z标识
            iso_timestamp = row['timestamp'].isoformat() + 'Z'
            messages.append({
                'sender': sender,
                'type': row['type'],
                'content': row['content'],
                'timestamp': iso_timestamp
            })
    conn.close()
    return jsonify({'success': True, 'messages': messages})

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'success': True, 'msg': '后端接口正常'})
