import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app, resources={r"*": {"origins": "*"}})
    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Origin, Content-Type, Authorization, X-Auth-Token')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATH, DELETE, OPTIONS')
        return response
    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories')
    def getCategories():
        try:
            data = Category.query.all()
            categories = {}
            for category in data:
                categories[category.id] = category.type

            return jsonify({
                'success': True,
                'status code': 200,
                'categories': categories
            })
        except:
            abort(405)
        '''
  @TODO:
  def getQuestions(page):
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions/<int:page>', methods=['GET'])
    def getQuestions(page):
        data = Question.query.paginate(page, QUESTIONS_PER_PAGE, True)
        items = data.items
        categs = Category.query.all()
        categories = {}
        for category in categs:
            categories[category.id] = category.type
        result = []
        for q in items:
            result.append(q.format())
        return jsonify({
            'success': True,
            'status code': 200,
            'questions': result,
            'categories': categories,
            'totalQuestions': Question.query.count(),
            'current_category': None
        })

    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def deleteQuestions(id):
      try:
        question = Question.query.filter(Question.id == id).one_or_none()
        if question:
          question.delete()
          return jsonify({
            'success': True,
            'status code': 200,
            'question': question.format()
            })
        else:
          abort(404)
      except:
        abort(404)
      

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
    @app.route('/questions', methods=['POST'])
    def createQuestion():
      try:
        data = request.get_json()
        if not(data.get('question') and data.get('answer') and data.get('category') and data.get('difficulty')):
          abort(422)
        else:
          print(data)
        question = Question(data.get('question'), data.get('answer'),data.get('category'),data.get('difficulty'))
        question.insert()
        return jsonify({
          'success': True,
          'questions':question.format()
          }), 201
      except:
        abort(422)
    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
    @app.route('/questions/search', methods=['GET'])
    def searchQuestions():
      try:
        searchTerm = request.args.get('searchTerm', type=str).lower()
        questions = Question.query.filter(
            Question.question.ilike(f'%{searchTerm}%')).all()
        questionsList = []
        for q in questions:
            questionsList.append(q.format())
        return jsonify({
            'success': True,
            'questions': questionsList
        })
      except:
        abort(422)

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
    @app.route('/categories/<int:id>/questions')
    def questionsByCategory(id):
        category = Category.query.get(id)
        if category:
            questions = Question.query.filter(Question.category == id).all()
            return jsonify({
                'success': True,
                'status code': 200,
                'questions': [q.format() for q in questions]
            })
        else:
            abort(404)

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        # previous_questions: previousQuestions,
        # quiz_category: this.state.quizCategory
        
        data = request.get_json()
        quiz_category = data.get('quiz_category')
        previousQuestions = data.get('previous_questions')
        questions = []
        if quiz_category["id"] == "0":
            questions = db.session.query(Question).filter(
                Question.id not in previousQuestions).all()
        else:
            category = Category.query.get(quiz_category["id"])
            if not category:
              abort(404)
            # questions = Question.query.filter(and_(Question.category == category.id, ~Question.id._in(previousQuestions))).all()
            questions = db.session.query(Question).filter((Question.id.notin_(
                previousQuestions)) & (Question.category == category.id)).all()
        if questions:
            return jsonify({
                'success': True,
                'status code': 200,
                'question': random.choice(questions).format()
            })
        else:
            abort(404)

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'Error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'Error': 404,
            'message': 'Not Found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'Error': 422,
            'message': 'Unable to process request'
        }), 422

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'Error': 405,
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'Error': 500,
            'message': 'Server Error'
        }), 500

    return app
