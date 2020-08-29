from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from .views import post_list

# Create your tests here.
class PostListTest(TestCase):
    
    def test_home_html_valid(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'post_list.html')
        
    def test_login(self):
        #TODO
    
    def test_logout(self):
        #TODO
    
    def test_new_post(self):
        #TODO
    
    def test_publish_post(self):
        #TODO
    
    def test_delete_post(self):
        #TODO
    
    def test_update_post(self):
        #TODO
    
    def test_update_cv(self):
        #TODO
    
    
    