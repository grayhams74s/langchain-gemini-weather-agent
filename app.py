from flask import Flask, render_template, request, redirect, url_for, session
from agent import agent, get_message_text
import uuid
import os

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

@app.route('/')
def home():
    if 'thread_id' not in session:
        session['thread_id'] = str(uuid.uuid4())
    if 'messages' not in session:
        session['messages'] = []
    else:
        for message in session['messages']:
            if message.get('type') == 'ai':
                message['content'] = get_message_text(message.get('content', ''))
        session.modified = True
    return render_template('chat.html', messages=session['messages'])

@app.route('/send', methods=['POST'])
def send():
    user_message = request.form.get('message', '').strip()
    user_lat = request.form.get('latitude')
    user_lon = request.form.get('longitude')

    if not user_message:
        return redirect(url_for('home'))

    if user_lat and user_lon:
        session['user_location'] = {'lat': user_lat, 'lon': user_lon}

    thread_id = session.setdefault('thread_id', str(uuid.uuid4()))
    messages = session.setdefault('messages', [])
    messages.append({'type': 'human', 'content': user_message})

    try:
        response = agent.invoke(
            {"messages": [{'role': 'user', 'content': user_message}]},
            {"configurable": {"thread_id": thread_id}},
        )
        reply = get_message_text(response['messages'][-1])
    except Exception:
        app.logger.exception('Weather agent request failed')
        reply = (
            'Sorry, I could not reach the weather service right now. '
            'Please try again in a moment.'
        )

    messages.append({'type': 'ai', 'content': reply})
    session['messages'] = messages
    session.modified = True
    return redirect(url_for('home'))


@app.route('/clear', methods=['POST'])
def clear():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
