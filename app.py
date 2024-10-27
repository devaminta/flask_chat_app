from flask import Flask, request, jsonify
from redis import Redis, RedisError

app = Flask(__name__)
redis = Redis(host='localhost', port=6379)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        message = request.json
        # Using '0' as the message ID so that Redis can auto-generate one
        redis.xadd('chat_stream', message, id='*')
        return jsonify({'status': 'success', 'message': 'Message sent successfully'}), 201
    except RedisError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@app.route('/stream')
def stream():
    try:
        last_id = request.args.get('last_id', '0')  # Default to '0'
        messages = redis.xrange('chat_stream', min=last_id)
        response = {'messages': []}
        for message in messages:
            message_id = message[0].decode('utf-8')  # Decode the message ID
            message_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in message[1].items()}  # Decode key-value pairs
            response['messages'].append({'id': message_id, **message_data})
        return jsonify(response), 200
    except RedisError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
