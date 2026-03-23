# _*_ coding:utf-8 _*_
import json
from datetime import datetime

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Category, Tagprofile, Blog, Conment, Message
from .templatetags.custom_filter import (
    slice_list, custom_markdown, paginate, tag2string, getTag
)


User = get_user_model()


class UserModelTest(TestCase):
    def test_str(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        self.assertEqual(str(user), 'testuser')

    def test_create_superuser(self):
        user = User.objects.create_superuser(username='admin', password='adminpass', email='admin@test.com')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class CategoryModelTest(TestCase):
    def test_str(self):
        category = Category.objects.create(name='Python')
        self.assertEqual(str(category), 'Python')

    def test_auto_add_time(self):
        category = Category.objects.create(name='Django')
        self.assertIsNotNone(category.add_time)

    def test_auto_edit_time(self):
        category = Category.objects.create(name='Flask')
        self.assertIsNotNone(category.edit_time)


class TagprofileModelTest(TestCase):
    def test_str(self):
        tag = Tagprofile.objects.create(tag_name='Python')
        self.assertEqual(str(tag), 'Python')

    def test_tag_name_max_length(self):
        tag = Tagprofile.objects.create(tag_name='a' * 30)
        self.assertEqual(len(tag.tag_name), 30)


class BlogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='author', password='pass')
        self.category = Category.objects.create(name='Tech')
        self.tag1 = Tagprofile.objects.create(tag_name='Python')
        self.tag2 = Tagprofile.objects.create(tag_name='Django')

    def test_str(self):
        blog = Blog.objects.create(
            title='Test Blog',
            category=self.category,
            author=self.user,
            content='Test content',
            read_nums=0,
            conment_nums=0
        )
        self.assertEqual(str(blog), 'Test Blog')

    def test_default_values(self):
        blog = Blog.objects.create(
            title='Default Test',
            category=self.category,
            author=self.user,
            content='Content'
        )
        self.assertEqual(blog.read_nums, 0)
        self.assertEqual(blog.conment_nums, 0)
        self.assertEqual(blog.digest, '')

    def test_many_to_many_tags(self):
        blog = Blog.objects.create(
            title='Tagged Blog',
            category=self.category,
            author=self.user,
            content='Content'
        )
        blog.tag.add(self.tag1, self.tag2)
        self.assertEqual(blog.tag.count(), 2)
        self.assertIn(self.tag1, blog.tag.all())

    def test_auto_add_time(self):
        blog = Blog.objects.create(
            title='Time Test',
            category=self.category,
            author=self.user,
            content='Content'
        )
        self.assertIsNotNone(blog.add_time)
        self.assertIsNotNone(blog.edit_time)


class ConmentModelTest(TestCase):
    def test_str(self):
        comment = Conment.objects.create(
            user='testuser',
            title='Test Comment',
            source_id='1',
            conment='This is a test comment',
            url='http://example.com'
        )
        self.assertEqual(str(comment), 'Test Comment')

    def test_auto_add_time(self):
        comment = Conment.objects.create(
            user='user',
            title='Title',
            source_id='1',
            conment='Content',
            url='http://example.com'
        )
        self.assertIsNotNone(comment.add_time)


class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='msguser', password='pass')

    def test_str(self):
        msg = Message.objects.create(
            user=self.user,
            message='Hello World'
        )
        self.assertEqual(str(msg), 'Hello World')

    def test_auto_add_time(self):
        msg = Message.objects.create(
            user=self.user,
            message='Test message'
        )
        self.assertIsNotNone(msg.add_time)


class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='author', password='pass')
        self.category = Category.objects.create(name='Tech')

    def test_get_empty_list(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_get_with_articles(self):
        blog = Blog.objects.create(
            title='Test Article',
            category=self.category,
            author=self.user,
            content='Content'
        )
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('article_list', response.context)
        self.assertIn('article_rank', response.context)


class AboutViewTest(TestCase):
    def test_get(self):
        response = self.client.get(reverse('blog:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')


class ArticlesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='author', password='pass')
        self.category = Category.objects.create(name='Tech')

    def test_get_all_articles(self):
        response = self.client.get(reverse('blog:article', args=[0]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles.html')
        self.assertEqual(response.context['category'], '')

    def test_get_by_category(self):
        blog = Blog.objects.create(
            title='Category Article',
            category=self.category,
            author=self.user,
            content='Content'
        )
        response = self.client.get(reverse('blog:article', args=[self.category.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['category'], 'Tech')
        self.assertEqual(response.context['count'], 1)

    def test_get_nonexistent_category(self):
        response = self.client.get(reverse('blog:article', args=[9999]))
        self.assertEqual(response.status_code, 404)


class ArchiveViewTest(TestCase):
    def test_get(self):
        response = self.client.get(reverse('blog:archive'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'archive.html')


class LinkViewTest(TestCase):
    def test_get(self):
        response = self.client.get(reverse('blog:link'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'link.html')


class MessageViewTest(TestCase):
    def test_get(self):
        response = self.client.get(reverse('blog:message'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'message_board.html')


class SearchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='author', password='pass')
        self.category = Category.objects.create(name='Tech')
        self.blog = Blog.objects.create(
            title='Python Tutorial',
            category=self.category,
            author=self.user,
            content='Learn Python programming'
        )

    def test_search_with_key(self):
        response = self.client.get(reverse('blog:search'), {'key': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['count'], 1)
        self.assertEqual(response.context['key'], 'Python')

    def test_search_no_match(self):
        response = self.client.get(reverse('blog:search'), {'key': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['count'], 0)

    def test_search_in_content(self):
        response = self.client.get(reverse('blog:search'), {'key': 'programming'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['count'], 1)


class DetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='author', password='pass')
        self.category = Category.objects.create(name='Tech')
        self.blog = Blog.objects.create(
            title='Detail Test',
            category=self.category,
            author=self.user,
            content='Content'
        )

    def test_get_detail(self):
        response = self.client.get(reverse('blog:detail', args=[self.blog.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail.html')
        self.assertEqual(response.context['article'].title, 'Detail Test')

    def test_get_nonexistent_detail(self):
        response = self.client.get(reverse('blog:detail', args=[9999]))
        self.assertEqual(response.status_code, 404)


class TagcloudViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='author', password='pass')
        self.category = Category.objects.create(name='Tech')
        self.tag = Tagprofile.objects.create(tag_name='Python')
        self.blog = Blog.objects.create(
            title='Tagged Article',
            category=self.category,
            author=self.user,
            content='Content'
        )
        self.blog.tag.add(self.tag)

    def test_get_tagcloud(self):
        response = self.client.get(reverse('blog:tag', args=[self.tag.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag.html')
        self.assertEqual(response.context['tag'], 'Python')
        self.assertEqual(response.context['count'], 1)

    def test_get_nonexistent_tag(self):
        response = self.client.get(reverse('blog:tag', args=[9999]))
        self.assertEqual(response.status_code, 404)


class GetCommentTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='author', password='pass')
        self.category = Category.objects.create(name='Tech')
        self.blog = Blog.objects.create(
            title='Comment Test',
            category=self.category,
            author=self.user,
            content='Content',
            conment_nums=0
        )

    def test_post_comment_for_message(self):
        data = {
            'data': json.dumps({
                'title': 'Message Title',
                'url': 'http://example.com',
                'sourceid': 'message',
                'comments': [{
                    'content': 'Nice message!',
                    'user': {
                        'nickname': 'msg_user'
                    }
                }]
            })
        }
        response = self.client.post(reverse('blog:get_comment'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')


class SliceListFilterTest(TestCase):
    def test_slice_positive_index(self):
        result = slice_list(['a', 'b', 'c'], 1)
        self.assertEqual(result, 'b')

    def test_slice_negative_index(self):
        result = slice_list(['a', 'b', 'c'], -1)
        self.assertEqual(result, 'c')

    def test_slice_empty_list(self):
        with self.assertRaises(IndexError):
            slice_list([], 0)


class CustomMarkdownFilterTest(TestCase):
    def test_basic_markdown(self):
        result = custom_markdown('**bold**')
        self.assertIn('<strong>', result)

    def test_code_block(self):
        result = custom_markdown('```python\nprint("hello")\n```')
        self.assertIn('language-python', result)

    def test_plain_text(self):
        result = custom_markdown('plain text')
        self.assertIn('plain text', result)

    def test_fenced_code(self):
        result = custom_markdown('```javascript\nvar x = 1;\n```')
        self.assertIn('language-javascript', result)


class PaginateTagTest(TestCase):
    def setUp(self):
        from django.template import Context, Template
        self.context = Context({'request': type('Request', (), {'GET': {}})})

    def test_paginate_first_page(self):
        items = list(range(25))
        context = {'request': type('Request', (), {'GET': {'page': '1'}})}
        paginate(context, items, 10)
        self.assertEqual(context['current_page'], 1)
        self.assertEqual(context['last_page'], 3)

    def test_paginate_invalid_page(self):
        items = list(range(25))
        context = {'request': type('Request', (), {'GET': {'page': 'invalid'}})}
        paginate(context, items, 10)
        self.assertEqual(context['current_page'], 1)

    def test_paginate_empty_page(self):
        items = list(range(25))
        context = {'request': type('Request', (), {'GET': {'page': '100'}})}
        paginate(context, items, 10)
        self.assertEqual(context['current_page'], 3)

    def test_paginate_returns_empty_string(self):
        items = list(range(10))
        context = {'request': type('Request', (), {'GET': {}})}
        result = paginate(context, items, 5)
        self.assertEqual(result, '')


class Tag2StringFilterTest(TestCase):
    def test_single_tag(self):
        result = tag2string([{'tag_name': 'Python'}])
        self.assertEqual(result, 'Python')

    def test_multiple_tags(self):
        result = tag2string([{'tag_name': 'Python'}, {'tag_name': 'Django'}])
        self.assertEqual(result, 'Python,Django')

    def test_empty_list(self):
        result = tag2string([])
        self.assertEqual(result, '')

    def test_missing_tag_name(self):
        result = tag2string([{'other': 'value'}])
        self.assertEqual(result, '')


class GetTagFilterTest(TestCase):
    def test_get_first_tag(self):
        result = getTag([{'tag_name': 'Python'}, {'tag_name': 'Django'}])
        self.assertEqual(result, 'Python')

    def test_empty_list(self):
        result = getTag([])
        self.assertEqual(result, '')

    def test_missing_tag_name(self):
        result = getTag([{'other': 'value'}])
        self.assertEqual(result, '')
