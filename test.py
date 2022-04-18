from main import app
import unittest
import sys

class FlaskTestCase(unittest.TestCase):

    def test_login(self):
        tester=app.test_client(self)
        response=tester.get('/login',content_type='html/text')
        self.assertEqual(response.status_code,200)


    def test_login_loads(self):
        tester=app.test_client(self)
        response=tester.get('/login',content_type='html/text')
        self.assertTrue(b'LOGIN' in response.data)





    def test_all_sellers(self):
        tester=app.test_client(self)
        response=tester.get('/get_all_sellers',content_type='html/text')
        self.assertTrue(b'Madara' in response.data)
        self.assertTrue(b'User1' in response.data)
        self.assertTrue(b'User2' in response.data)
        self.assertTrue(b'User3' in response.data)

    def test_view_item_details(self):
        tester=app.test_client(self)
        response=tester.get('/item_details/1',content_type='html/text')
        self.assertTrue(b'Madara' in response.data)
        self.assertTrue(b'$5.0' in response.data)

    def test_search_item(self):
        tester=app.test_client(self)
        response=tester.get('/search?searched=pumpkin',content_type='html/text')
        self.assertTrue(b'Seller : Madara' in response.data)
        self.assertTrue(b'Seller : User1' in response.data)
        self.assertTrue(b'Seller : User3' in response.data)

    def test_get_user_item(self):
        tester=app.test_client(self)
        response=tester.get('/get_user_items/1',content_type='html/text')
        self.assertTrue(b'Carrots' in response.data)
        self.assertTrue(b'$5.0 per kg' in response.data)
        self.assertTrue(b'Pumpkin' in response.data)
        self.assertTrue(b'$15.0 per kg' in response.data)
        self.assertTrue(b'Lettuce' in response.data) 
        self.assertTrue(b'$4.0 per kg' in response.data)


if __name__=='__main__':
    unittest.main()