from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest

SITE_URL = "http://localhost:8000"
SITE_NAME = "Richard's Website"


class NewVisitorTest(unittest.TestCase):  

    def setUp(self):  
        self.browser = webdriver.Firefox()

    def tearDown(self):  
        self.browser.quit()        

    def test_view_posts(self):
        #site is correct
        self.browser.get(SITE_URL)
        self.assertIn(SITE_NAME, self.browser.title)        
        header_text = self.browser.find_element_by_tag_name('h1').text  
        self.assertIn(SITE_NAME, header_text)        
        
        #able to log in/shows logged in
        login_link = self.browser.find_element_by_id('login-link')
        
        #able to see posts   
             
        
        self.fail('test finished!')
        
    #test_login
    
    #test_logout
        
    #test_post_creation
    
    #test_post_publish_list
    
    #test_post_publish
    
    #test_post_detail_shown_correctly
    
    #test_post_edit
    
    #test_post_deletion
    
    #test_cv_shown
    
    #test_cv_update


if __name__ == '__main__':  
    unittest.main(warnings='ignore')  