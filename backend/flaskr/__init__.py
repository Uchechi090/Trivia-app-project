import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# helper function for pagination


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)

    """
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    # CORS(app, resources={r"*/api/*" : {origins: '*'}})
    CORS(app)

    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()

        category_dict = {}
        for category in categories:
            category_dict[category.id] = category.type

        if len(category_dict) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": category_dict,
                "total_categories": len(category_dict)
            }
        )

    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions", methods=["GET"])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        # get categories and format their IDs and TYPEs as key-value pairs
        categories = {}
        list_of_categories = Category.query.order_by(Category.id).all()
        for category in list_of_categories:
            categories[category.id] = category.type

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                # so number of pages will be according to number of questions
                "total_questions": len(Question.query.all()),
                "categories": categories,
                # set this to None because we are not getting questions by
                # category
                "current_category": None
            }
        )

    """
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            # {
            #     "answer": "Lake Victoria",
            #     "category": 3,
            #     "difficulty": 2,
            #     "id": 13,
            #     "question": "What is the largest lake in Africa?"
            # }

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except BaseException:
            abort(422)

    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    # Merged the search and create question endpoint since they both use POST
    # method
    @app.route("/questions", methods=["POST"])
    def create_and_search_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_difficulty = body.get("difficulty", None)
        new_category = body.get("category", None)
        searchTerm = body.get("searchTerm", None)

        try:
            if searchTerm:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(searchTerm))
                )
                current_questions = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "total_questions": len(selection.all()),
                    }
                )

            else:
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    difficulty=new_difficulty,
                    category=new_category)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "created": question.id,
                        "questions": current_questions,
                        "total_questions": len(Question.query.all()),
                    }
                )

        except BaseException:
            abort(422)

    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_question_by_category(category_id):

        category = Category.query.filter(
            Category.id == category_id).one_or_none()
        if category is None:
            abort(404)

        try:
            selection = Question.query.filter(
                Question.category == str(category_id)).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({"success": True,
                            "questions": current_questions,
                            "total_questions": len(selection),
                            "current_category": category.type})

        except BaseException:
            abort(404)

    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random question within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=["POST"])
    def get_quizzes():

        try:
            body = request.get_json()

            previous_questions = body.get("previous_questions", None)
            category = body.get("quiz_category", None)

            if category['id'] == 0 and len(previous_questions) == 0:
                fresh_quizzes = Question.query.order_by(Question.id).all()
            elif len(previous_questions) == 0:
                fresh_quizzes = Question.query.filter(
                    Question.category == str(category['id'])).all()
            elif category['id'] == 0:
                fresh_quizzes = Question.query.filter(
                    Question.id.not_in_(previous_questions)).all()
            else:
                fresh_quizzes = Question.query.filter(Question.category == str(
                    category['id']), Question.id.not_in(previous_questions)).all()

            current_question = None
            if (fresh_quizzes):
                current_question = random.choice(fresh_quizzes).format()

            return jsonify(
                {
                    "success": True,
                    "question": current_question,
                    "current_category": category['type']
                }
            )

        except BaseException:
            abort(422)

    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500

    return app
