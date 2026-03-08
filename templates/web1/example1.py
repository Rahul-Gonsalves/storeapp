# app.py
from flask import Flask

# Create an instance of the Flask class
app = Flask(__name__)

# Define a "route" and the function to handle it
@app.route('/')
def hello_world():
    return '<html><body><h1>Hello, World!</h1></body></html>'

@app.route('/about')
def about():
    return '<html><body><h1>About me</h1><p>I am Dr. Tung Nguyen from Texas A&M University.</p></body></html>'


# This block allows you to run the app directly
if __name__ == '__main__':
    # The debug=True flag enables a helpful debugger
    app.run(debug=True)