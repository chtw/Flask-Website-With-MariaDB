# imports the Flask library
import sqlite3
from flask import Response
from flask import Flask, render_template, request, redirect, url_for
# creates the web application
app = Flask(__name__)
# defines the route, or “web address”

def get_db_connection():
    # connect to database
    conn = sqlite3.connect('database.db')
    # allows database rows to be accessed using cols names
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
# defines the function that runs when users visit /
def Home():
# sends HTML back to  home to home page
    return render_template("Home.html")

@app.route("/Projects")
def Projects():
    conn = get_db_connection()
    # take all projects from database
    projects = conn.execute('SELECT * FROM projects').fetchall()
    conn.commit()
    conn.close()
    # send to proj data 
    return render_template("Project.html" , projects = projects)

@app.route("/Skills")
def Skills():
    # display skills page
    return render_template("Skills.html")

@app.route("/Contact", methods=['GET','POST'])
def Contact():
    error = None
    # when user submits contact form 
    if request.method =='POST':
        name = request.form.get('Name')
        email = request.form.get('Email')
        message = request.form.get('Message')
        phone_number = request.form.get('phone_number')
        if ("@" not in email):
            error = "Email must contain @"
        if (len(message) == 0):
            error = "Message cannot be empty"

        if error is None:
            # insert user input and save to database    
            conn = get_db_connection()
            conn.execute('INSERT INTO contacts (name, email, phonenumber, message)  VALUES (?, ?, ?, ?)',
                        (name, email, phone_number, message))
            conn.commit()
            conn.close()
    return render_template("Contact.html",error=error)

@app.route('/add', methods=['GET', 'POST'])
def add():

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        # gets the image file
        image = request.files['image']
        #converts img to binary data to be stored in blob col in sql
        image_data = image.read()
        #check which type of image isit 
        mimetype = image.mimetype
        conn = get_db_connection()
        #insert proj info and save to database
        conn.execute(
            '''
            INSERT INTO projects(title, description, image, mimetype)
            VALUES (?, ?, ?, ?)
            ''',
            (title, description, image_data, mimetype)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('Projects'))
    return render_template('AddProject.html')


@app.route('/image/<int:id>')
def image(id):

    conn = get_db_connection()
    #select the image and its file type
    project = conn.execute(
        "SELECT image , mimetype FROM projects WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()
    # returns binary and image type to browser
    return Response(project['image'], mimetype=project['mimetype'])

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    conn = get_db_connection()

    project = conn.execute(
        'SELECT * FROM projects WHERE id = ?',
        (id,)
    ).fetchone()

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        image = request.files['image']

        # If user selected a new image
        if image.filename != '':
            #convert image to binary data and get its file type
            image_data = image.read()
            mimetype = image.mimetype

            #update proj info and save to database 
            conn.execute(
                '''
                UPDATE projects
                SET title = ?,
                    description = ?,
                    image = ?,
                    mimetype = ?
                WHERE id = ?
                ''',
                (title, description, image_data, mimetype, id)
            )

        # If user did not select a new image
        else:

            conn.execute(
                '''
                UPDATE projects
                SET title = ?,
                    description = ?
                WHERE id = ?
                ''',
                (title, description, id)
            )

        conn.commit()
        conn.close()
        return redirect(url_for('Projects'))

    conn.close()

    return render_template('EditProject.html',project=project)
        
        
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    # del the proj 
    conn.execute('DELETE FROM projects WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('Projects'))

if __name__ == "__main__":
# starts the Flask development server
    app.run(debug=True)