from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from .views import post_list

# Create your tests here.
class PostListTest(TestCase):
    
    def test_home_html_valid(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'post_list.html')
        

    
    