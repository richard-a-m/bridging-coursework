from django.test import TestCase
from django.test import Client
from django.urls import resolve
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import SESSION_KEY
from django.utils import timezone

TEST_USERNAME = "test_bot"
TEST_PASS = "UJjhzh3m9J+mRV]"

# Create your tests here. #TODO improve usable tests?
class SiteTests(TestCase):
    fixtures = ["test_data.json"]
    
    def setUp(self): #setup for each test
        self.c = Client()
        self.user = User.objects.create_user(TEST_USERNAME, 'test@example.com', TEST_PASS) #TODO Make sure this doesn't have to be superuser
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
        
    