from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
     return '<h1>Hello from DevOps Pipeline!</hi><p>Version 1.0</p>'

@app.route('/health')
def health():
     return {'status': 'healthy', 'version': '1.0'}

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000, debug=True)
