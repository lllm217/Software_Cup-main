"""Run: ../.venv/Scripts/python.exe -m unittest test_accessibility -v"""
import os
import tempfile
import unittest
from pathlib import Path
from copy import deepcopy

_temp = tempfile.TemporaryDirectory(prefix='six-profile-test-')
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///' + (Path(_temp.name) / 'test.db').as_posix()
os.environ['AUTH_ENABLED'] = 'true'
os.environ['JWT_SECRET'] = 'test-only-secret-' * 4

from fastapi.testclient import TestClient
from main import app
from api.accessibility import _handoffs

ANSWERS = {
    'goal': ['探索个人兴趣'], 'foundation': ['零基础'],
    'format': ['图文讲解'], 'duration': ['15–30 分钟'],
    'difficulty': ['理解抽象概念'], 'feedback': ['分步骤讲解思路'],
}


class AccessibilityIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = TestClient(app)
        cls.client = cls.context.__enter__()

    @classmethod
    def tearDownClass(cls):
        from db.database import engine
        cls.client.portal.call(engine.dispose)
        cls.context.__exit__(None, None, None)
        _temp.cleanup()

    def session(self):
        response = self.client.post('/api/accessibility/session')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        return data, {'Authorization': 'Bearer ' + data['access_token']}

    def submit(self, headers, answers=None, course='人工智能导论', scores=None):
        return self.client.post('/api/accessibility/profile', headers=headers, json={
            'answers': answers if answers is not None else deepcopy(ANSWERS),
            'course': course, 'scores': scores or [],
        })

    def test_real_algorithm_save_reload_path_and_handoff(self):
        session, headers = self.session()
        response = self.submit(headers)
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        profile = result['profile']
        self.assertEqual(profile['base_level'], 1)
        self.assertEqual(profile['learn_goal'], '兴趣')
        self.assertEqual(profile['learn_preference'], '教案文档')
        self.assertEqual(profile['learn_speed'], 3)
        self.assertIn('分步骤讲解思路', result['summary'])
        current = self.client.get('/api/chat/profile/' + session['student_id'], headers=headers).json()
        self.assertTrue(current['questionnaire_complete'])
        self.assertEqual(current['base_level'], 1)
        status = self.client.get('/api/questionnaire/status/' + session['student_id'], headers=headers).json()
        self.assertEqual(status['answers']['supplemental'], ANSWERS)
        self.assertEqual(status['profile'], profile)
        path = self.client.get('/api/path/get_path', params={'student_id': session['student_id']}, headers=headers)
        self.assertEqual(path.status_code, 200, path.text)
        self.assertGreater(len(path.json()['path']), 0)
        exchange = self.client.post('/api/accessibility/handoff', json={'handoff': result['handoff']})
        self.assertEqual(exchange.status_code, 200, exchange.text)
        self.assertEqual(exchange.json()['profile'], profile)
        replay = self.client.post('/api/accessibility/handoff', json={'handoff': result['handoff']})
        self.assertEqual(replay.status_code, 401)

    def test_different_answers_and_course_snapshots(self):
        session, headers = self.session()
        first = self.submit(headers).json()['profile']
        answers = deepcopy(ANSWERS)
        answers.update(goal=['提升项目与实践能力'], foundation=['有相关项目经验'],
                       format=['项目实战', '交互练习'], difficulty=['将知识应用到实践'],
                       duration=['60 分钟以上'])
        response = self.submit(headers, answers, '软件安全', [1, 2, 3, 4, 5, 1])
        self.assertEqual(response.status_code, 200, response.text)
        profile = response.json()['profile']
        self.assertEqual(profile['course'], '软件安全技术')
        self.assertEqual(profile['base_level'], 5)
        self.assertEqual(profile['learn_speed'], 5)
        self.assertEqual(profile['cognitive_style'], '实践型')
        self.assertNotEqual(profile, first)
        restored = self.client.get('/api/questionnaire/status/' + session['student_id'],
                                   params={'course': '人工智能导论'}, headers=headers).json()
        self.assertEqual(restored['profile'], first)
        settings = self.client.get('/api/profile/settings/' + session['student_id'],
                                   params={'course': '软件安全技术'}, headers=headers).json()
        self.assertEqual(settings['focus_min'], 60)

    def test_invalid_incomplete_and_unauthenticated(self):
        session, headers = self.session()
        self.assertEqual(self.submit({}).status_code, 401)
        invalid = deepcopy(ANSWERS)
        del invalid['feedback']
        self.assertEqual(self.submit(headers, invalid).status_code, 422)
        invalid = deepcopy(ANSWERS)
        invalid['foundation'] = ['invalid']
        self.assertEqual(self.submit(headers, invalid).status_code, 422)
        self.assertEqual(self.submit(headers, scores=[6] * 6).status_code, 422)
        status = self.client.get('/api/questionnaire/status/' + session['student_id'], headers=headers).json()
        self.assertFalse(status['completed'])

    def test_guest_isolation_and_expired_handoff(self):
        first, headers = self.session()
        second, other = self.session()
        self.assertNotEqual(first['student_id'], second['student_id'])
        result = self.submit(headers).json()
        # Original repository endpoints must resolve identity from token.
        response = self.client.get('/api/chat/profile/' + first['student_id'], headers=other).json()
        self.assertEqual(response['student_id'], second['student_id'])
        self.assertFalse(response['questionnaire_complete'])
        _handoffs[result['handoff']] = (first['student_id'], 0)
        self.assertEqual(self.client.post('/api/accessibility/handoff',
                                         json={'handoff': result['handoff']}).status_code, 401)


if __name__ == '__main__':
    unittest.main()
