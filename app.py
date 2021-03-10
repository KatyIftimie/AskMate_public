import os
from uuid import *
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import data_manager as dm

app = Flask(__name__)
app.config["IMAGE_UPLOADS"] = "static/images/"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPG", "JPEG", "PNG"]


def allowed_image(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


@app.route("/")
def main():
    title = "Main Page"
    questions = dm.get_all_entries(limit=5)
    return render_template("main.html", questions=questions, title=title)


@app.route("/list")
def list_all_question():
    questions = dm.get_all_entries()
    return render_template("main.html", questions=questions)


@app.route("/question/<question_id>", methods=['GET'])
def list_question(question_id):
    question = dm.get_question(question_id)
    answers = dm.get_answer_for_question(question_id)
    dm.count_views(question_id)
    return render_template("question.html", question=question, answers=answers)


@app.route('/add_question', methods=['GET', 'POST'])
def add_questions():
    change_route_variable = 'question'
    if request.method == 'POST':
        question = {
                'title'  : request.form.get('title'),
                'message': request.form.get('message'),
                'image'  : request.form.get('image')
                }
        dm.add_new_question(question)
        return redirect('/list')
    return render_template('add_comment.html', change_route_variable=change_route_variable)


@app.route("/question/<question_id>/question_comment", methods=['GET', 'POST'])
def add_question_comment(question_id):
    change_route_variable = 'question_comment'
    if request.method == 'POST':
        comment = {
                'question_id': question_id,
                'message': request.form.get('message')
                }
        dm.add_question_comment(comment)
        return redirect(url_for("show_comments_on_question", question_id=question_id))
    return render_template('add_comment.html', question_id=question_id, change_route_variable=change_route_variable)


@app.route("/answer/<answer_id>/new-comment", methods=['GET', 'POST'])
def add_answer_comment(answer_id):
    change_route_variable = 'answer_comment'
    if request.method == 'POST':
        comment = {
                'answer_id': answer_id,
                'message'  : request.form.get('message')
                }
        dm.add_answer_comment(comment)
        return redirect(url_for("show_comments_on_answers", answer_id=answer_id))
    return render_template('add_comment.html', answer_id=answer_id, change_route_variable=change_route_variable)


@app.route('/question/<question_id>/new_answer', methods=['GET', 'POST'])
def add_answer(question_id):
    change_route_variable = 'answer'
    if request.method == 'POST':
        print("asd")
        answer = {
                'question_id': question_id,
                'message'    : request.form.get('message'),
                'image'      : request.form.get('image')
                }
        dm.add_new_answer(answer)

        return redirect(url_for('list_question', question_id=question_id))
    return render_template('add_comment.html',question_id = question_id , change_route_variable= change_route_variable)


@app.route('/question/<int:id>/<type>')
def vote_questions(id, type):
    id = id
    type = type
    dm.vote(id, type, "question")
    return redirect(request.referrer)


@app.route('/delete/<int:id>/<type>')
def delete_entry(id, type):
    row_id = id
    table = type
    if type == "question":
        dm.delete_entry(row_id, table)
        return redirect(request.referrer)
    elif type == "answer":
        dm.delete_entry(row_id, table)
        return redirect(request.referrer)
        # return redirect(url_for('list_question', question_id=id))
    


@app.route("/question/<question_id>/comments")
def show_comments_on_question(question_id):
    comments = dm.get_question_comments(question_id)
    return render_template("question_comments.html", question_id=question_id, comments=comments)


@app.route("/answer/<answer_id>/comments")
def show_comments_on_answers(answer_id):
    comments = dm.get_answer_comments(answer_id)
    question_id = dm.question_id_by_answer_id(answer_id)
    print(question_id)
    return render_template("answer_comments.html", answer_id=answer_id, comments=comments, question_id=question_id)


@app.route("/<table>/<id>/upload-image", methods=["GET", "POST"])
def upload_image(table, id):
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            if image.filename == "":
                print("Image must have a filename")
                return redirect(request.url)
            if not allowed_image(image.filename):
                print("The file extension is not allowed!")
                return redirect(request.url)
            else:
                filename = secure_filename(image.filename)
                ext = filename.split(".")[-1]
                filename = table + "_" + str(UUID('{12345678-1234-5678-1234-567812345678}')) + "." + ext
                image.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))
                dm.add_picture_to_db(table_id=id, filename=filename, table=table)
        return redirect(request.url)
    return render_template('upload_image.html', table=table)


@app.route("/search", methods=["GET"])
def search():
    key_words = request.args["search"]
    answers = dm.search_answer(key_words)
    questions = dm.search_question(key_words)
    return render_template("search_results.html", questions=questions, answers=answers)


@app.route('/question/<question_id>/edit', methods=["GET", "POST"])
def edit_question(question_id):
    if request.method == 'POST':
        new_content = {
                'message': request.form.get('message'),
                'title'  : request.form.get('title')
                }
        dm.edit_question(question_id, new_content)
        redirect_to = url_for('list_question', question_id=question_id)
        return redirect(redirect_to)
    question_content = dm.get_question(question_id)
    return render_template("edit.html", question_content=question_content)


if __name__ == "__main__":
    app.run(
            debug=True,
            port=5000,
            host="0.0.0.0"
            )
