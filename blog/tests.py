from django.test import TestCase
from django.test import Client
from django.test import LiveServerTestCase
from django.urls import resolve
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import SESSION_KEY
from django.utils import timezone

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

import pickle, time

SITE_URL = "http://localhost:8000"
TEST_USERNAME = "test_bot"
TEST_PASS = "UJjhzh3m9J+mRV]"

# Create your tests here. #TODO improve usable tests?
class UnitTests(TestCase):
    fixtures = ["test_data.json"]
    
    def setUp(self): #setup for each test
        self.c = Client()
        self.user = User.objects.create_user(TEST_USERNAME, 'test@example.com', TEST_PASS)
        self.user.save()
    
    def test_home_html_valid(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_list.html')       
        
    def test_unauthenticated_user_permissions(self): #unauthenticated user shouldn't be able to perform certain actions #TODO breakup into separate tests
        #what options should be visible
        response = self.c.get("/")
        self.assertNotContains(response, "glyphicon-plus")
        self.assertNotContains(response, "glyphicon-edit")
        self.assertContains(response, "login")
        
        #shouldn't have any options for a post
        response = self.c.get("/post/1/")
        self.assertNotContains(response, "edit")
        self.assertNotContains(response, "remove")
        
        #shouldn't be able to see certain pages
        response = self.c.get("/post/2/")
        self.assertNotEqual(response.status_code, 200)
        response = self.c.get("/post/new/")
        self.assertNotEqual(response.status_code, 200)
        response = self.c.get("/post/1/edit/")
        self.assertNotEqual(response.status_code, 200)
        response = self.c.get("/drafts/")
        self.assertNotEqual(response.status_code, 200)
        
        #should no longer be authenticated
        self.assertNotIn('_auth_user_id', self.c.session)
        self.assertFalse(SESSION_KEY in self.client.session)
        
        #TODO directly attempt to create, edit, publish & remove posts?
        
    def test_login_page_usable(self):
        response = self.c.get("/accounts/login/")
        self.assertContains(response, "Username")
        self.assertContains(response, "Password")
        self.assertContains(response, "login")
    
    def test_login(self):
        response = self.c.post("/accounts/login/", {"username": TEST_USERNAME, "password": TEST_PASS}, follow=True)
        self.assertTemplateUsed(response, 'blog/post_list.html') #should redirect back to homepage
        self.assertContains(response, TEST_USERNAME) #username should be displayed after login
        self.assertContains(response, "Log out") #logout option should be displayed
        self.assertContains(response, "glyphicon-plus")
        self.assertContains(response, "glyphicon-edit")
        self.assertTrue(response.context['user'].is_authenticated)
    
    def test_new_post_page_usable(self):
        self.c.force_login(self.user)
        response = self.c.get("/post/new/")
        self.assertTemplateUsed(response, 'blog/post_edit.html')
        self.assertContains(response, "New post")
        self.assertContains(response, "Title")
        self.assertContains(response, "Text")
        
    def test_new_post(self):
        self.c.force_login(self.user)
        response = self.c.post("/post/new/", {"title" : "Test Post", "text" : "A quick brown fox jumps over the lazy dog."}, follow=True)
        self.assertTemplateUsed(response, 'blog/post_detail.html') #should redirect back to the new post's detail view
        self.assertEqual(response.status_code, 200) #if it doesn't 404 then the post should exist (or the authentication is broken)
        #self.assertURLEqual();
    
    def test_post_detail_page_usable(self):
        self.c.force_login(self.user)
        #published post shouldn't have publish option
        response = self.c.get("/post/1/")
        self.assertTemplateUsed(response, 'blog/post_detail.html')
        self.assertContains(response, "glyphicon-pencil")
        self.assertContains(response, "glyphicon-remove")
        self.assertNotContains(response, "Publish</a>")
        
        #unpublished post should have publish option
        response = self.c.get("/post/2/")
        self.assertContains(response, "glyphicon-pencil")
        self.assertContains(response, "glyphicon-remove")
        self.assertContains(response, "Publish</a>")
        
    def test_publish_post(self):
        self.c.force_login(self.user)
        response = self.c.post("/post/2/publish/", follow=True)
        self.assertTemplateUsed(response, 'blog/post_detail.html')
        self.assertNotContains(response, "Publish</a>")
    
    def test_update_post(self):
        self.c.force_login(self.user)
        response = self.c.post("/post/2/edit/", {"title":"983rjdwt3", "text":"<p>wa3867fhg3</p>"}, follow=True)
        self.assertTemplateUsed(response, 'blog/post_detail.html')
        self.assertContains(response, "983rjdwt3")
        self.assertContains(response, "wa3867fhg3")
        self.assertContains(response, "Publish</a>") #Check edit doesn't accidently publish the post
        
    def test_delete_post(self):
        self.c.force_login(self.user)
        response = self.c.post("/post/2/remove/", follow=True)
        self.assertTemplateUsed(response, 'blog/post_list.html') #should redirect back to homepage
        response = self.c.get("/post/2/")
        self.assertEqual(response.status_code, 404) #should 404 now that the post has been deleted(or authentication is broken)
        
    def test_logout(self):
        self.c.force_login(self.user)
        response = self.c.get("/accounts/logout/", follow=True)
        self.assertRedirects(response, "/")
        self.assertNotContains(response, TEST_USERNAME) #a username shouldn't be displayed
        self.assertNotContains(response, "Log out") #logout option shouldn't be displayed
        
        #should no longer be authenticated
        self.assertNotIn('_auth_user_id', self.c.session)
        self.assertFalse(SESSION_KEY in self.client.session)
        
    def test_cv_shown(self):
        response = self.c.get("/cv/view")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CV")
        
class FunctionalTests(LiveServerTestCase):

    def setUp(self):  
        self.selenium = webdriver.Firefox()
        self.user = User.objects.create_user(TEST_USERNAME, 'test@example.com', TEST_PASS)
        self.user.save()

    def tearDown(self):  
        self.selenium.quit()

    def test_home(self):
        #site is correct
        self.selenium.get(self.live_server_url)
        self.assertIn("Richard's Website", self.selenium.title)        
        header_text = self.selenium.find_element_by_tag_name('h1').text
        self.assertIn("Richard's Website", header_text)
        
        #log in & CV exists
        self.assertTrue(len(self.selenium.find_elements_by_id("login-link")) == 1)
        self.assertTrue(len(self.selenium.find_elements_by_link_text("CV")) == 1)
    
    def test_login_logout(self):
        timeout = 2
        self.selenium.get('%s%s' % (self.live_server_url, "/accounts/login/"))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(TEST_USERNAME)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(TEST_PASS)
        self.selenium.find_element_by_xpath('//input[@value="login"]').click()
        WebDriverWait(self.selenium, timeout).until(lambda driver: driver.find_element_by_tag_name('body'))
        xpath_str = "//*[contains(text(), '" + TEST_USERNAME + "')]"
        self.assertTrue(len(self.selenium.find_elements_by_xpath(xpath_str)) == 1)
        
        #logout
        self.selenium.find_element_by_link_text("Log out").click()
        WebDriverWait(self.selenium, timeout).until(lambda driver: driver.find_element_by_tag_name('body'))
        self.assertTrue(len(self.selenium.find_elements_by_id("login-link")) == 1)
        self.assertTrue(len(self.selenium.find_elements_by_xpath(xpath_str)) == 0)
        
    def test_update_cv(self):
        timeout = 2
        
        #login code #TODO find a way to force login?
        self.selenium.get('%s%s' % (self.live_server_url, "/accounts/login/"))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(TEST_USERNAME)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(TEST_PASS)
        self.selenium.find_element_by_xpath('//input[@value="login"]').click()
        WebDriverWait(self.selenium, timeout).until(lambda driver: driver.find_element_by_tag_name('body'))
        
        #workaround as fixtures don't seem to want to work for this...
        self.selenium.find_element_by_class_name("glyphicon-plus").click()
        self.selenium.find_element_by_name("title").send_keys("CV")
        self.selenium.execute_script("tinyMCE.activeEditor.setContent('%s')" % "this is a cv blah blah blah")
        self.selenium.find_element_by_class_name("save").click()
        
        #test code       
        self.selenium.find_element_by_link_text("CV").click()
        self.selenium.find_element_by_id("edit-post").click()
        WebDriverWait(self.selenium, timeout).until(lambda driver: driver.find_element_by_tag_name('body'))
        test_text = "jhawd983hgkj389gvad873hdkogg3"
        self.selenium.execute_script("tinyMCE.activeEditor.setContent('%s')" % test_text)
        self.selenium.find_element_by_class_name("save").click()
        WebDriverWait(self.selenium, timeout).until(lambda driver: driver.find_element_by_tag_name('body'))
        xpath_str = "//*[contains(text(), '" + test_text + "')]"
        self.assertTrue(len(self.selenium.find_elements_by_xpath(xpath_str)) == 1)
       
    """
    def test_post_manipulation(self):
        self.selenium.get(self.live_server_url)
        #TODO if necessary
    """
        
        
        