from django.test import TestCase, LiveServerTestCase
from django.urls import resolve
from django.http import HttpRequest
from datetime import datetime

from blogpost.views import index, view_post
from blogpost.models import BlogPost
from selenium import webdriver

# Create your tests here.
class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, index)
    
    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = index(request)
        self.assertIn(b'Welcome to my blog', response.content)

class BlogpostTest(TestCase):
    def test_blogpost_view_post_url(self):
        found = resolve('/blog/this-is-a-test')
        self.assertEqual(found.func, view_post)
    
    def test_blogpost_view_post(self):
        BlogPost.objects.create(title = 'hello',
                                author = 'Victor',
                                slug = 'this-is-a-test',
                                body = 'This is a blog',
                                posted = datetime.now)
        response = self.client.get('/blog/this-is-a-test')
        self.assertIn(b'This is a blog', response.content)
    
    def test_blogpost_show_in_homepage(self):
        BlogPost.objects.create(title = 'hello',
                                author = 'Victor',
                                slug = 'this-is-a-test',
                                body = 'This is a blog',
                                posted = datetime.now)
        response = self.client.get('/')
        self.assertIn(b'This is a blog', response.content)

class HomepageTestCase(LiveServerTestCase):
    def setUp(self):
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(HomepageTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(HomepageTestCase, self).tearDown()

    # def test_visit_homepage(self):
    #     print(self.live_server_url)
    #     self.selenium.get('%s%s' % (self.live_server_url, "/"))
    #     self.assertIn("Welcom to my blog", self.selenium.title)