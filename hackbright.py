"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a github account name, print information about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM students
        WHERE github = :github
        """
    db_cursor = db.session.execute(QUERY, {'github': github})
    row = db_cursor.fetchone()
    print "Student: %s %s\nGithub account: %s" % (row[0], row[1], row[2])

    return row


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """
    QUERY = """
            INSERT INTO students
                VALUES (:first_name, :last_name, :github)
            """

    db.session.execute(QUERY, {'first_name': first_name,
                               'last_name': last_name,
                               'github': github})

    db.session.commit()

    print "Added student: %s %s with github ID %s" % (first_name, last_name, github)


def get_project_by_title(title):
    """Given a project title, print information about the project."""

    QUERY = """
        SELECT title, description, max_grade
            FROM projects
        WHERE title = :title
            """

    db_cursor = db.session.execute(QUERY, {'title': title})
    row = db_cursor.fetchone()
    print "Project: %s - %s\nMax grade: %d" % (row[0], row[1], row[2])

    return row


def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""

    QUERY = """
        SELECT first_name, last_name, grade, project_title
            FROM students s
            JOIN grades g ON s.github = g.student_github
        WHERE s.github = :github
            AND g.project_title = :title
            """
    db_cursor = db.session.execute(QUERY, {'github': github,
                                           'title': title})
    rows = db_cursor.fetchall()
    for row in rows:
        print "%s %s recieved a %d on %s" % (row[0], row[1], row[2], row[3])


def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""

    QUERY = """
        INSERT INTO grades (student_github, project_title, grade)
            VALUES (:github, :title, :grade)
            """

    db.session.execute(QUERY, {'github': github,
                               'title': title,
                               'grade': grade})

    db.session.commit()

    print "Assigned grade %s to github ID %s for project %s" % (grade, github, title)


def add_project(title, description, max_grade):
    """Add a project"""

    QUERY = """
        INSERT INTO projects (title, description, max_grade)
            VALUES (:title, :description, :max_grade)
            """

    db.session.execute(QUERY, {'title': title,
                               'description': description,
                               'max_grade': int(max_grade)})

    db.session.commit()

    print "Added project %s - %s, with maximum grade of %s" % (title, description, max_grade)


def get_all_student_grades(github):
    """Given a github ID, displays all student grades"""

    QUERY = """
        SELECT DISTINCT first_name, last_name, grade, project_title
            FROM students s
            JOIN grades g ON s.github = g.student_github
        WHERE s.github = :github
        ORDER BY project_title, grade
            """
    db_cursor = db.session.execute(QUERY, {'github': github})
    rows = db_cursor.fetchall()
    print rows
    for row in rows:
        print "%s %s recieved a %s on %s" % (row[0], row[1], row[2], row[3])

    return rows


def get_students_for_project(title):
    """Given a project title, display students and grades."""

    QUERY = """
        SELECT DISTINCT first_name, last_name, grade, github
            FROM grades g
            JOIN students s ON g.student_github = s.github
        WHERE g.project_title = :title
        ORDER BY last_name, first_name, grade
            """
    db_cursor = db.session.execute(QUERY, {'title': title})
    rows = db_cursor.fetchall()

    return rows


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received as a
    command."""

    command = None

    while command != "quit":
        input_string = raw_input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        elif command == "new_student":
            first_name, last_name, github = args   # unpack!
            make_new_student(first_name, last_name, github)

        elif command == "project_title":
            title = args[0]
            get_project_by_title(title)

        elif command == "grade_github_title":
            github = args[0]
            title = args[1]
            get_grade_by_github_title(github, title)

        elif command == "assign_grade":
            github = args[0]
            title = args[1]
            grade = args[2]
            assign_grade(github, title, grade)

        elif command == "add_project":
            title = args[0]
            description = " ".join(args[1:-1])
            max_grade = args[-1]
            add_project(title, description, max_grade)

        elif command == "all_grades":
            github = args[0]
            get_all_student_grades(github)

        else:
            if command != "quit":
                print "Invalid Entry. Try again."

if __name__ == "__main__":
    app = Flask(__name__)
    connect_to_db(app)

    handle_input()

    db.session.close()
