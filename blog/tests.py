# _*_ coding:utf-8 _*_
import json

from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.http import JsonResponse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import User, Category, Tagprofile, Blog, Conment
from .views import (Index, About, Articles, Archive, Link, Message, Search,
                    GetComment, Detail, Tagcloud)
from .templatetags.custom_filter import (slice_list, custom_markdown, paginate,
                                         tag2string, getTag)


class UserModelTest(TestCase):
    """User模型测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_user_creation(self):
        """测试用户创建"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(str(self.user), 'testuser')

    def test_user_str_method(self):
        """测试User的__str__方法"""
        self.assertEqual(str(self.user), 'testuser')


class CategoryModelTest(TestCase):
    """Category模型测试"""

    def setUp(self):
        self.category = Category.objects.create(name='Python')

    def test_category_creation(self):
        """测试分类创建"""
        self.assertEqual(self.category.name, 'Python')
        self.assertIsNotNone(self.category.add_time)
        self.assertIsNotNone(self.category.edit_time)

    def test_category_str_method(self):
        """测试Category的__str__方法"""
        self.assertEqual(str(self.category), 'Python')

    def test_category_verbose_name(self):
        """测试分类的verbose_name"""
        self.assertEqual(Category._meta.verbose_name, '文档分类')


class TagprofileModelTest(TestCase):
    """Tagprofile模型测试"""

    def setUp(self):
        self.tag = Tagprofile.objects.create(tag_name='Django')

    def test_tag_creation(self):
        """测试标签创建"""
        self.assertEqual(self.tag.tag_name, 'Django')

    def test_tag_str_method(self):
        """测试Tagprofile的__str__方法"""
        self.assertEqual(str(self.tag), 'Django')


class BlogModelTest(TestCase):
    """Blog模型测试"""

    def setUp(self):
        self.user = User.objects.create_user(username='author', password='pass123')
        self.category = Category.objects.create(name='Tech')
        self.tag = Tagprofile.objects.create(tag_name='Python')
        self.blog = Blog.objects.create(
            title='Test Blog',
            category=self.category,
            author=self.user,
            content='This is a test blog content',
            digest='Test digest',
            read_nums=10,
            conment_nums=5
        )
        self.blog.tag.add(self.tag)

    def test_blog_creation(self):
        """测试博客创建"""
        self.assertEqual(self.blog.title, 'Test Blog')
        self.assertEqual(self.blog.category, self.category)
        self.assertEqual(self.blog.author, self.user)
        self.assertEqual(self.blog.read_nums, 10)
        self.assertEqual(self.blog.conment_nums, 5)

    def test_blog_str_method(self):
        """测试Blog的__str__方法"""
        self.assertEqual(str(self.blog), 'Test Blog')

    def test_blog_tag_relationship(self):
        """测试博客与标签的多对多关系"""
        self.assertEqual(self.blog.tag.count(), 1)
        self.assertIn(self.tag, self.blog.tag.all())

    def test_blog_default_values(self):
        """测试博客默认值"""
        new_blog = Blog.objects.create(title='New Blog', content='Content')
        self.assertEqual(new_blog.read_nums, 0)
        self.assertEqual(new_blog.conment_nums, 0)
        self.assertEqual(new_blog.digest, '')


class ConmentModelTest(TestCase):
    """Conment模型测试"""

    def setUp(self):
        self.comment = Conment.objects.create(
            user='TestUser',
            title='Test Comment',
            source_id='1',
            conment='This is a comment',
            url='http://example.com'
        )

    def test_comment_creation(self):
        """测试评论创建"""
        self.assertEqual(self.comment.user, 'TestUser')
        self.assertEqual(self.comment.title, 'Test Comment')
        self.assertEqual(self.comment.source_id, '1')
        self.assertEqual(self.comment.conment, 'This is a comment')

    def test_comment_str_method(self):
        """测试Conment的__str__方法"""
        self.assertEqual(str(self.comment), 'Test Comment')


class IndexViewTest(TestCase):
    """Index视图测试"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test123')
        self.category = Category.objects.create(name='Tech')
        self.tag = Tagprofile.objects.create(tag_name='Python')
        for i in range(10):
            blog = Blog.objects.create(
                title=f'Blog {i}',
                category=self.category,
                author=self.user,
                content=f'Content {i}',
                conment_nums=i
            )
            blog.tag.add(self.tag)

    def test_index_get(self):
        """测试首页GET请求"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_index_context(self):
        """测试首页上下文数据"""
        response = self.client.get(reverse('index'))
        self.assertIn('article_list', response.context)
        self.assertIn('article_rank', response.context)
        self.assertIn('category_list', response.context)
        self.assertIn('tag_list', response.context)
        self.assertIn('comment_list', response.context)

    def test_index_article_list_limit(self):
        """测试首页文章列表限制为5条"""
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context['article_list']), 5)


class AboutViewTest(TestCase):
    """About视图测试"""

    def test_about_get(self):
        """测试关于页面GET请求"""
        response = self.client.get(reverse('blog:about'))
        self.assertEqual(response.status_code, 200)


class ArticlesViewTest(TestCase):
    """Articles视图测试"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test123')
        self.category = Category.objects.create(name='Tech')
        self.tag = Tagprofile.objects.create(tag_name='Python')
        self.blog = Blog.objects.create(
            title='Test Blog',
            category=self.category,
            author=self.user,
            content='Test content'
        )

    def test_articles_with_category(self):
        """测试带分类ID的文章列表"""
        response = self.client.get(reverse('blog:article', kwargs={'pk': self.category.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['category'], 'Tech')

    def test_articles_all(self):
        """测试全部文章列表(pk=0)"""
        response = self.client.get(reverse('blog:article', kwargs={'pk': 0}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['category'], '')

    def test_articles_count(self):
        """测试文章计数"""
        response = self.client.get(reverse('blog:article', kwargs={'pk': self.category.id}))
        self.assertEqual(response.context['count'], 1)

    def test_articles_404(self):
        """测试不存在的分类返回404"""
        response = self.client.get(reverse('blog:article', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)


class ArchiveViewTest(TestCase):
    """Archive视图测试"""

    def test_archive_get(self):
        """测试归档页面GET请求"""
        response = self.client.get(reverse('blog:archive'))
        self.assertEqual(response.status_code, 200)


class LinkViewTest(TestCase):
    """Link视图测试"""

    def test_link_get(self):
        """测试链接页面GET请求"""
        response = self.client.get(reverse('blog:link'))
        self.assertEqual(response.status_code, 200)


class MessageViewTest(TestCase):
    """Message视图测试"""

    def test_message_get(self):
        """测试留言页面GET请求"""
        response = self.client.get(reverse('blog:message'))
        self.assertEqual(response.status_code, 200)


class SearchViewTest(TestCase):
    """Search视图测试"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test123')
        self.category = Category.objects.create(name='Tech')
        self.blog1 = Blog.objects.create(
            title='Python Tutorial',
            category=self.category,
            author=self.user,
            content='Learn Python programming'
        )
        self.blog2 = Blog.objects.create(
            title='Django Guide',
            category=self.category,
            author=self.user,
            content='Web development with Django'
        )

    def test_search_with_keyword(self):
        """测试带关键词的搜索"""
        response = self.client.get(reverse('blog:search'), {'key': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['key'], 'Python')
        self.assertEqual(response.context['count'], 1)

    def test_search_content_match(self):
        """测试内容匹配搜索"""
        response = self.client.get(reverse('blog:search'), {'key': 'Django'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['count'], 1)

    def test_search_no_results(self):
        """测试无结果的搜索"""
        response = self.client.get(reverse('blog:search'), {'key': 'nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['count'], 0)

    def test_search_or_condition(self):
        """测试搜索OR条件（标题或内容）"""
        response = self.client.get(reverse('blog:search'), {'key': 'development'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['count'], 1)


class DetailViewTest(TestCase):
    """Detail视图测试"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test123')
        self.category = Category.objects.create(name='Tech')
        self.blog = Blog.objects.create(
            title='Test Blog',
            category=self.category,
            author=self.user,
            content='Test content'
        )

    def test_detail_get(self):
        """测试博客详情页GET请求"""
        response = self.client.get(reverse('blog:detail', kwargs={'pk': self.blog.id}))
        self.assertEqual(response.status_code, 200)

    def test_detail_context(self):
        """测试详情页上下文"""
        response = self.client.get(reverse('blog:detail', kwargs={'pk': self.blog.id}))
        self.assertEqual(response.context['article'], self.blog)
        self.assertEqual(response.context['source_id'], self.blog.id)

    def test_detail_404(self):
        """测试不存在的博客返回404"""
        response = self.client.get(reverse('blog:detail', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)


class TagcloudViewTest(TestCase):
    """Tagcloud视图测试"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test123')
        self.category = Category.objects.create(name='Tech')
        self.tag = Tagprofile.objects.create(tag_name='Python')
        self.blog = Blog.objects.create(
            title='Test Blog',
            category=self.category,
            author=self.user,
            content='Test content'
        )
        self.blog.tag.add(self.tag)

    def test_tagcloud_get(self):
        """测试标签云页面GET请求"""
        response = self.client.get(reverse('blog:tag', kwargs={'id': self.tag.id}))
        self.assertEqual(response.status_code, 200)

    def test_tagcloud_context(self):
        """测试标签云上下文"""
        response = self.client.get(reverse('blog:tag', kwargs={'id': self.tag.id}))
        self.assertEqual(response.context['tag'], 'Python')
        self.assertEqual(response.context['count'], 1)

    def test_tagcloud_404(self):
        """测试不存在的标签返回404"""
        response = self.client.get(reverse('blog:tag', kwargs={'id': 9999}))
        self.assertEqual(response.status_code, 404)


class GetCommentTest(TestCase):
    """GetComment评论回推接口测试"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test123')
        self.category = Category.objects.create(name='Tech')
        self.blog = Blog.objects.create(
            title='Test Blog',
            category=self.category,
            author=self.user,
            content='Test content',
            conment_nums=0
        )

    def test_get_comment_message_source(self):
        """测试留言板评论回推(source_id='message') - 绕过commenced()调用"""
        data = {
            'title': 'Message Comment',
            'url': 'http://example.com',
            'sourceid': 'message',
            'comments': [{
                'content': 'Nice message board!',
                'user': {'nickname': 'Anonymous'}
            }]
        }
        response = self.client.post(
            reverse('blog:get_comment'),
            {'data': json.dumps(data)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_get_comment_saves_to_db(self):
        """测试评论保存到数据库 - 使用message source绕过commenced()"""
        initial_count = Conment.objects.count()
        data = {
            'title': 'DB Test',
            'url': 'http://example.com',
            'sourceid': 'message',
            'comments': [{
                'content': 'Database test comment',
                'user': {'nickname': 'DBTester'}
            }]
        }
        self.client.post(reverse('blog:get_comment'), {'data': json.dumps(data)})
        self.assertEqual(Conment.objects.count(), initial_count + 1)





class CustomFilterTest(TestCase):
    """自定义模板过滤器测试"""

    def test_slice_list(self):
        """测试slice_list过滤器"""
        test_list = [1, 2, 3, 4, 5]
        self.assertEqual(slice_list(test_list, 0), 1)
        self.assertEqual(slice_list(test_list, 2), 3)
        self.assertEqual(slice_list(test_list, slice(1, 3)), [2, 3])

    def test_custom_markdown(self):
        """测试custom_markdown过滤器"""
        content = '# Hello\n\nThis is **bold** text.'
        result = custom_markdown(content)
        self.assertIn('<h1>', result)
        self.assertIn('<strong>', result)

    def test_custom_markdown_code_highlight(self):
        """测试代码高亮转换"""
        content = '```python\nprint("hello")\n```'
        result = custom_markdown(content)
        self.assertIn('language-python', result)
        self.assertIn('line-numbers', result)

    def test_tag2string(self):
        """测试tag2string过滤器"""
        tags = [{'tag_name': 'Python'}, {'tag_name': 'Django'}]
        self.assertEqual(tag2string(tags), 'Python,Django')

    def test_tag2string_empty(self):
        """测试tag2string空列表"""
        self.assertEqual(tag2string([]), '')

    def test_tag2string_missing_key(self):
        """测试tag2string缺少tag_name键"""
        tags = [{'tag_name': 'Python'}, {'other': 'value'}]
        self.assertEqual(tag2string(tags), 'Python,')

    def test_getTag(self):
        """测试getTag过滤器"""
        tags = [{'tag_name': 'Python'}, {'tag_name': 'Django'}]
        self.assertEqual(getTag(tags), 'Python')

    def test_getTag_empty(self):
        """测试getTag空列表"""
        self.assertEqual(getTag([]), '')

    def test_getTag_no_tag_name(self):
        """测试getTag没有tag_name"""
        tags = [{'other': 'value'}]
        self.assertEqual(getTag(tags), '')


class PaginateTagTest(TestCase):
    """分页标签测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='test', password='test123')
        self.category = Category.objects.create(name='Tech')
        for i in range(25):
            Blog.objects.create(
                title=f'Blog {i}',
                category=self.category,
                author=self.user,
                content=f'Content {i}'
            )

    def test_paginate_valid_page(self):
        """测试有效页码分页"""
        request = self.factory.get('/test?page=2')
        context = {'request': request}
        object_list = Blog.objects.all()
        result = paginate(context, object_list, 10)
        self.assertEqual(result, '')
        self.assertEqual(context['current_page'], 2)

    def test_paginate_not_integer(self):
        """测试非整数页码"""
        request = self.factory.get('/test?page=abc')
        context = {'request': request}
        object_list = Blog.objects.all()
        paginate(context, object_list, 10)
        self.assertEqual(context['current_page'], 1)

    def test_paginate_empty_page(self):
        """测试超出范围的页码"""
        request = self.factory.get('/test?page=999')
        context = {'request': request}
        object_list = Blog.objects.all()
        paginate(context, object_list, 10)
        self.assertEqual(context['current_page'], 3)

    def test_paginate_context_values(self):
        """测试分页上下文值"""
        request = self.factory.get('/test?page=1')
        context = {'request': request}
        object_list = Blog.objects.all()
        paginate(context, object_list, 10)
        # count is assigned as the count method itself (business code behavior)
        self.assertEqual(context['count'](), 25)
        self.assertEqual(context['first_page'], 1)
        self.assertEqual(context['last_page'], 3)


class EdgeCaseTest(TestCase):
    """边界条件和异常路径测试"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test123')
        self.category = Category.objects.create(name='Tech')

    def test_blog_with_empty_title(self):
        """测试空标题博客"""
        blog = Blog.objects.create(
            title='',
            category=self.category,
            author=self.user,
            content='Content'
        )
        self.assertEqual(str(blog), '')

    def test_blog_with_long_title(self):
        """测试超长标题博客"""
        long_title = 'A' * 50
        blog = Blog.objects.create(
            title=long_title,
            category=self.category,
            author=self.user,
            content='Content'
        )
        self.assertEqual(blog.title, long_title)

    def test_comment_with_special_chars(self):
        """测试特殊字符评论"""
        comment = Conment.objects.create(
            user='User<script>',
            title='Title"Test"',
            source_id='1',
            conment='Content with <html> & "quotes"',
            url='http://example.com?param=value&other=test'
        )
        self.assertEqual(comment.user, 'User<script>')
        self.assertEqual(comment.conment, 'Content with <html> & "quotes"')

    def test_search_special_characters(self):
        """测试搜索特殊字符"""
        response = self.client.get(reverse('blog:search'), {'key': '<script>alert(1)</script>'})
        self.assertEqual(response.status_code, 200)

    def test_search_sql_injection_attempt(self):
        """测试搜索SQL注入尝试"""
        response = self.client.get(reverse('blog:search'), {'key': "' OR '1'='1"})
        self.assertEqual(response.status_code, 200)

    def test_articles_zero_pk(self):
        """测试文章列表pk=0边界"""
        response = self.client.get(reverse('blog:article', kwargs={'pk': 0}))
        self.assertEqual(response.status_code, 200)

    def test_blog_without_category(self):
        """测试无分类博客"""
        blog = Blog.objects.create(
            title='No Category',
            author=self.user,
            content='Content'
        )
        self.assertIsNone(blog.category)

    def test_blog_without_author(self):
        """测试无作者博客"""
        blog = Blog.objects.create(
            title='No Author',
            category=self.category,
            content='Content'
        )
        self.assertIsNone(blog.author)

    def test_multiple_tags_on_blog(self):
        """测试博客多个标签"""
        tag1 = Tagprofile.objects.create(tag_name='Python')
        tag2 = Tagprofile.objects.create(tag_name='Django')
        tag3 = Tagprofile.objects.create(tag_name='Web')
        blog = Blog.objects.create(
            title='Multi Tag Blog',
            category=self.category,
            author=self.user,
            content='Content'
        )
        blog.tag.add(tag1, tag2, tag3)
        self.assertEqual(blog.tag.count(), 3)

    def test_negative_read_nums(self):
        """测试负数阅读数边界"""
        blog = Blog.objects.create(
            title='Negative Reads',
            category=self.category,
            author=self.user,
            content='Content',
            read_nums=-1
        )
        self.assertEqual(blog.read_nums, -1)

    def test_very_long_comment(self):
        """测试超长评论"""
        long_comment = 'A' * 10000
        comment = Conment.objects.create(
            user='User',
            title='Long',
            source_id='1',
            conment=long_comment,
            url='http://example.com'
        )
        self.assertEqual(comment.conment, long_comment)
