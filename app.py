from flask import Flask, render_template, request
from agent import agent

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('chat.html')


@app.route("/send", methods=['POST'])
def send():
    user_message = request.form
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message,
                }
            ]
        },
        {"configurable": {"thread_id": "1"}},
    )
    return "Hello There"


if __name__ == "__main__":
    app.run(debug=True)
