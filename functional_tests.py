from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest
from bridging_coursework import urls

SITE_URL = "http://localhost:8000"
SITE_NAME = "Richard's Website"


class NewVisitorTest(unittest.TestCase):  

    def setUp(self):  
        self.browser = webdriver.Firefox()

    def tearDown(self):  
        self.browser.quit()        

    def test_posts_view(self):
        #site is correct
        self.browser.get(SITE_URL)
        self.assertIn(SITE_NAME, self.browser.title)        
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn(SITE_NAME, header_text)
        
        #able to view posts # TODO verify more than one post is visible & visibility is good
        post_title = self.browser.find_element_by_tag_name('h2').text
        self.assertIsNotNone(post_title)
        post_text = self.browser.find_element_by_tag_name('p').text
        self.assertIsNotNone(post_text)
        
        #able to see correct log in
        login_link = self.browser.find_element_by_id('login-link')
        self.assertIsNotNone(login_link)
        response = self.browser.get(login_link)
        #TODO somehow assert response is the correct login page
        
        #self.fail('test finished!') #TODO remove this later?
        
    def test_login_logout(self):
        #TODO
        
    def test_post_creation(self):
        #TODO
    
    def test_post_publish(self):
        #TODO
    
    def test_post_edit(self):
        #TODO
    
    def test_post_deletion(self):
        #TODO
    
    def test_cv_view(self):
        self.browser.get(SITE_URL)
        #TODO finish
    
    def test_cv_update(self):
        #TODO


if __name__ == '__main__':  
    unittest.main(warnings='ignore')  