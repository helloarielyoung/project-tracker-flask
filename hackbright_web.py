"""A web application for tracking projects, students, and student grades."""

from flask import Flask, request, render_template

import hackbright

app = Flask(__name__)


@app.route("/student")
def get_student():
    """Show information about a student."""

    #get student data
    github = request.args.get('github')

    first, last, github = hackbright.get_student_by_github(github)

    #get student's projects
    grades = hackbright.get_all_student_grades(github)
    #returns first, last, grade, project title

    html = render_template("student_info.html",
                           first=first,
                           last=last,
                           github=github,
                           grades=grades)
    return html


@app.route("/student-search")
def get_student_form():
    """Show form for searching for a student."""

    html = render_template("student_search.html")

    return html


@app.route("/student-add-form")
def student_add():
    """Add a student."""

    html = render_template("student_add.html")

    return html


@app.route("/add-confirmation", methods=['POST'])
def confirm_add():
    """This Adds the student and confirms that student was added."""

    last_name = request.form.get('last_name')
    first_name = request.form.get('first_name')
    github = request.form.get('github')

    hackbright.make_new_student(first_name, last_name, github)

    html = render_template("add_confirmation.html",
                           last_name=last_name,
                           first_name=first_name,
                           github=github)

    return html


@app.route("/project")
def show_project():
    """Given project title this displays project info."""

    #this receives the title and github via GET via link from student_info.html
    title = request.args.get('title')

    #list with title, description, max_grade
    project_title, description, max_grade = hackbright.get_project_by_title(title)

    # get a list with student name, grade, github
    # returns first_name, last_name, grade, github
    students = hackbright.get_students_for_project(title)

    html = render_template("project_info.html",
                           project_title=project_title,
                           description=description,
                           max_grade=max_grade,
                           students=students)

    return html

if __name__ == "__main__":
    hackbright.connect_to_db(app)
    app.run(debug=True)
