from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
	return 'Hello, Flask!'

@app.route('/chat') 
def chat():
    return 'Hello!'

if __name__ == '__main__':
	app.run(debug=True)