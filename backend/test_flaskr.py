import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        user = "postgres"
        password = "1111"
        self.database_path = "postgres://{}:{}@{}/{}".format(user,password,'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_getQuestions(self):
        res = self.client().get('/questions/1')
        self.assertEqual(res.status_code, 200)
    def test_getQuestions_invalid_page_fail(self):
        #use an invalid id
        res = self.client().get('/questions/9999')
        self.assertEqual(res.status_code, 404)
    def test_deleteQuestion(self):
        randomQ = self.client().get('/questions/1')        
        id=randomQ.get_json()['questions'][0]['id']
        res = self.client().delete(f'/questions/{id}')
        self.assertEqual(res.status_code, 200)
    def test_deleteQuestion_invalid_id_fail(self):
        res = self.client().delete('/questions/9999')
        self.assertEqual(res.status_code, 404)
    def test_post_questions(self):
        res = self.client().post('/questions', json={
            'question': 'is this a question',
            'answer': 'yes it is',
            'difficulty': 5,
            'category': 4
            })
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.get_json()['success'], True)
        self.assertIs(type(res.get_json()['questions']["id"]),int)
    def test_search_question(self):
        res = self.client().get('/questions/search?searchTerm=only team to play in every soccer')
        result = res.get_json()['questions'][0]
        self.assertEqual(result['question'],'Which is the only team to play in every soccer World Cup tournament?')
    def test_questions_pagination(self):
        res = self.client().get('/questions/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    def test_post_questions_fail(self):
        res = self.client().post('/questions', json={
            'question': 'is this a question',
            'answer': 'yes it is',
            'difficulty': 5
            })
        self.assertEqual(res.status_code, 422)
        self.assertEqual(res.get_json()['success'], False)
    def test_get_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
    def test_get_category_questions_fail(self):
        res = self.client().get('/categories/999/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
    def test_quizz(self):
        payload = {
            "previous_questions": [9,12,5],
            "quiz_category": {
            "type": "Art",
            "id": "4"
            } 
            }
        res = self.client().post('/quizzes',json = payload)
        self.assertEqual(res.status_code, 200)
    def test_quizz_fail(self):
        payload = {
            "previous_questions": [9,5,12,23],
            "quiz_category": {
            "type": "Art",
            "id": "55"
            } 
            }
        res = self.client().post('/quizzes',json = payload)
        self.assertEqual(res.status_code, 404)
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()