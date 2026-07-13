import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class SmartLenderTests(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_predict_approved_case(self):
        # Scenario 1: Salaried, good credit history, stable income
        payload = {
            'gender': '1', 'married': '1', 'dependents': '0', 'education': '1', 'self_employed': '0',
            'applicant_income': '5000', 'coapplicant_income': '2000', 'loan_amount': '150000',
            'loan_amount_term': '360', 'credit_history': '1.0', 'property_area': '1'
        }
        response = self.client.post('/predict', data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Approved', response.data)

    def test_predict_rejected_case(self):
        # Scenario 2: Unemployed, no credit history, high request
        payload = {
            'gender': '0', 'married': '0', 'dependents': '2', 'education': '0', 'self_employed': '1',
            'applicant_income': '2000', 'coapplicant_income': '0', 'loan_amount': '300000',
            'loan_amount_term': '180', 'credit_history': '0.0', 'property_area': '0'
        }
        response = self.client.post('/predict', data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Rejected', response.data)

if __name__ == '__main__':
    unittest.main()
