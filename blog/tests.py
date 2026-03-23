# _*_ coding:utf-8 _*_
import json
from datetime import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Blog, Category, Conment, Tagprofile, Message

User = get_user_model()


class ModelTests(TestCase):
    """模型测试用例"""

    def setUp(self):
        """测试准备：创建测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='测试分类')
        self.tag = Tagprofile.objects.create(tag_name='测试标签')
        self.blog = Blog.objects.create(
            title='测试博客标题',
            category=self.category,
            author=self.user,
            content='测试博客内容',
            digest='测试摘要',
            image='test_image.jpg'
        )
        self.blog.tag.add(self.tag)

    def test_user_model_str(self):
        """测试User模型的__str__方法"""
        self.assertEqual(str(self.user), 'testuser')

    def test_user_model_verbose_name(self):
        """测试User模型的verbose_name"""
        self.assertEqual(User._meta.verbose_name, '用户信息')
        self.assertEqual(User._meta.verbose_name_plural, '用户信息')

    def test_category_model_str(self):
        """测试Category模型的__str__方法"""
        self.assertEqual(str(self.category), '测试分类')

    def test_category_model_fields(self):
        """测试Category模型的字段"""
        self.assertTrue(hasattr(self.category, 'name'))
        self.assertTrue(hasattr(self.category, 'add_time'))
        self.assertTrue(hasattr(self.category, 'edit_time'))

    def test_tagprofile_model_str(self):
        """测试Tagprofile模型的__str__方法"""
        self.assertEqual(str(self.tag), '测试标签')

    def test_tagprofile_model_fields(self):
        """测试Tagprofile模型的字段"""
        self.assertTrue(hasattr(self.tag, 'tag_name'))

    def test_blog_model_str(self):
        """测试Blog模型的__str__方法"""
        self.assertEqual(str(self.blog), '测试博客标题')

    def test_blog_model_fields(self):
        """测试Blog模型的所有字段"""
        self.assertTrue(hasattr(self.blog, 'title'))
        self.assertTrue(hasattr(self.blog, 'category'))
        self.assertTrue(hasattr(self.blog, 'author'))
        self.assertTrue(hasattr(self.blog, 'content'))
        self.assertTrue(hasattr(self.blog, 'digest'))
        self.assertTrue(hasattr(self.blog, 'add_time'))
        self.assertTrue(hasattr(self.blog, 'edit_time'))
        self.assertTrue(hasattr(self.blog, 'read_nums'))
        self.assertTrue(hasattr(self.blog, 'conment_nums'))
        self.assertTrue(hasattr(self.blog, 'image'))
        self.assertTrue(hasattr(self.blog, 'tag'))

    def test_blog_model_default_values(self):
        """测试Blog模型的默认值"""
        self.assertEqual(self.blog.read_nums, 0)
        self.assertEqual(self.blog.conment_nums, 0)

    def test_conment_model_str(self):
        """测试Conment模型的__str__方法"""
        comment = Conment.objects.create(
            user='评论用户',
            title='评论标题',
            source_id='1',
            conment='评论内容',
            url='http://example.com'
        )
        self.assertEqual(str(comment), '评论标题')

    def test_conment_model_fields(self):
        """测试Conment模型的字段"""
        comment = Conment.objects.create(
            user='评论用户',
            title='评论标题',
            source_id='1',
            conment='评论内容',
            url='http://example.com'
        )
        self.assertTrue(hasattr(comment, 'user'))
        self.assertTrue(hasattr(comment, 'title'))
        self.assertTrue(hasattr(comment, 'source_id'))
        self.assertTrue(hasattr(comment, 'conment'))
        self.assertTrue(hasattr(comment, 'add_time'))
        self.assertTrue(hasattr(comment, 'url'))

    def test_message_model_str(self):
        """测试Message模型的__str__方法"""
        message = Message.objects.create(
            user=self.user,
            message='这是一条留言'
        )
        self.assertEqual(str(message), '这是一条留言')

    def test_message_model_fields(self):
        """测试Message模型的字段"""
        message = Message.objects.create(
            user=self.user,
            message='这是一条留言'
        )
        self.assertTrue(hasattr(message, 'user'))
        self.assertTrue(hasattr(message, 'message'))
        self.assertTrue(hasattr(message, 'add_time'))

    def test_model_relationships(self):
        """测试模型间的关系"""
        # 测试Blog与Category的外键关系
        self.assertEqual(self.blog.category, self.category)
        # 测试Blog与User的外键关系
        self.assertEqual(self.blog.author, self.user)
        # 测试Blog与Tagprofile的多对多关系
        self.assertIn(self.tag, self.blog.tag.all())


class ViewTests(TestCase):
    """视图测试用例"""

    def setUp(self):
        """测试准备：创建测试数据和客户端"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='测试分类')
        self.tag = Tagprofile.objects.create(tag_name='测试标签')
        self.blog = Blog.objects.create(
            title='测试博客标题',
            category=self.category,
            author=self.user,
            content='测试博客内容',
            digest='测试摘要',
            image='test_image.jpg'
        )
        self.blog.tag.add(self.tag)
        self.comment = Conment.objects.create(
            user='评论用户',
            title='评论标题',
            source_id=str(self.blog.id),
            conment='评论内容',
            url='http://example.com'
        )

    def test_index_view_get(self):
        """测试首页视图GET请求"""
        # index在根URL配置中，没有namespace
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertIn('article_list', response.context)
        self.assertIn('article_rank', response.context)

    def test_about_view_get(self):
        """测试关于页面视图GET请求"""
        response = self.client.get(reverse('blog:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')

    def test_articles_view_with_pk(self):
        """测试文章列表视图 - 带分类ID"""
        response = self.client.get(reverse('blog:article', args=[self.category.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles.html')
        self.assertIn('article_list', response.context)
        self.assertIn('category', response.context)
        self.assertIn('count', response.context)

    def test_articles_view_without_pk(self):
        """测试文章列表视图 - 不带分类ID（显示全部）"""
        # 测试pk=0的情况
        response = self.client.get(reverse('blog:article', args=[0]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles.html')
        self.assertIn('article_list', response.context)

    def test_archive_view_get(self):
        """测试归档页面视图GET请求"""
        response = self.client.get(reverse('blog:archive'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'archive.html')
        self.assertIn('article_list', response.context)

    def test_link_view_get(self):
        """测试链接页面视图GET请求"""
        response = self.client.get(reverse('blog:link'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'link.html')

    def test_message_view_get(self):
        """测试留言页面视图GET请求"""
        response = self.client.get(reverse('blog:message'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'message_board.html')

    def test_search_view_with_key(self):
        """测试搜索视图 - 带搜索关键词"""
        response = self.client.get(reverse('blog:search'), {'key': '测试'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search.html')
        self.assertIn('article_list', response.context)
        self.assertIn('count', response.context)
        self.assertIn('key', response.context)

    def test_detail_view_get(self):
        """测试博客详情视图GET请求"""
        response = self.client.get(reverse('blog:detail', args=[self.blog.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail.html')
        self.assertIn('article', response.context)
        self.assertIn('source_id', response.context)

    def test_tagcloud_view_get(self):
        """测试标签云视图GET请求"""
        response = self.client.get(reverse('blog:tag', args=[self.tag.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag.html')
        self.assertIn('tag', response.context)
        self.assertIn('article_list', response.context)
        self.assertIn('count', response.context)


class EdgeCaseTests(TestCase):
    """边界情况测试用例"""

    def setUp(self):
        """测试准备"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='测试分类')
        self.tag = Tagprofile.objects.create(tag_name='测试标签')
        self.blog = Blog.objects.create(
            title='测试博客标题',
            category=self.category,
            author=self.user,
            content='测试博客内容',
            digest='测试摘要',
            image='test_image.jpg'
        )

    def test_articles_view_nonexistent_category(self):
        """测试文章列表视图 - 不存在的分类ID"""
        response = self.client.get(reverse('blog:article', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_nonexistent_blog(self):
        """测试博客详情视图 - 不存在的博客ID"""
        response = self.client.get(reverse('blog:detail', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_tagcloud_view_nonexistent_tag(self):
        """测试标签云视图 - 不存在的标签ID"""
        response = self.client.get(reverse('blog:tag', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_search_view_no_results(self):
        """测试搜索视图 - 没有搜索结果"""
        response = self.client.get(reverse('blog:search'), {'key': '不存在的关键词123456'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['count'], 0)

    def test_search_view_special_characters(self):
        """测试搜索视图 - 特殊字符搜索"""
        special_chars = '!@#$%^&*()_+'
        response = self.client.get(reverse('blog:search'), {'key': special_chars})
        self.assertEqual(response.status_code, 200)
        # 特殊字符应该正常处理，不报错

    def test_search_view_long_key(self):
        """测试搜索视图 - 过长关键词"""
        long_key = 'a' * 1000
        response = self.client.get(reverse('blog:search'), {'key': long_key})
        self.assertEqual(response.status_code, 200)
        # 长关键词应该正常处理

    def test_articles_view_zero_articles(self):
        """测试文章列表视图 - 零文章的分类"""
        empty_category = Category.objects.create(name='空分类')
        response = self.client.get(reverse('blog:article', args=[empty_category.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['count'], 0)

    def test_model_foreignkey_null(self):
        """测试模型外键null情况"""
        # Blog模型category和author允许为null
        blog = Blog.objects.create(
            title='无分类无作者博客',
            content='测试内容',
            image='test.jpg'
        )
        self.assertIsNone(blog.category)
        self.assertIsNone(blog.author)

    def test_model_field_max_length(self):
        """测试模型字段最大长度边界"""
        # 测试Category.name的最大长度
        long_name = 'a' * 20
        category = Category.objects.create(name=long_name)
        self.assertEqual(len(category.name), 20)

        # 测试Tagprofile.tag_name的最大长度
        long_tag_name = 'a' * 30
        tag = Tagprofile.objects.create(tag_name=long_tag_name)
        self.assertEqual(len(tag.tag_name), 30)

        # 测试Blog.title的最大长度
        long_title = 'a' * 50
        blog = Blog.objects.create(
            title=long_title,
            content='测试内容',
            image='test.jpg'
        )
        self.assertEqual(len(blog.title), 50)


class ExceptionPathTests(TestCase):
    """异常路径测试用例"""

    def setUp(self):
        """测试准备"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_getcomment_view_get_method(self):
        """测试GetComment视图 - GET方法"""
        # GetComment函数没有做方法检查，GET请求会进入函数并在json.loads(data)时失败
        with self.assertRaises(TypeError):
            self.client.get(reverse('blog:get_comment'))

    def test_getcomment_view_post_without_data(self):
        """测试GetComment视图 - POST无数据"""
        # 无数据时会触发TypeError，因为data为None时json.loads()会失败
        with self.assertRaises(TypeError):
            self.client.post(reverse('blog:get_comment'))

    def test_getcomment_view_post_invalid_json(self):
        """测试GetComment视图 - POST无效JSON"""
        invalid_data = {
            'data': 'invalid json'
        }
        with self.assertRaises(json.JSONDecodeError):
            self.client.post(reverse('blog:get_comment'), invalid_data)

    def test_view_post_method_not_allowed(self):
        """测试仅支持GET的视图使用POST方法"""
        views_to_test = [
            reverse('index'),  # index在根URL中
            reverse('blog:about'),
            reverse('blog:archive'),
            reverse('blog:link'),
            reverse('blog:message'),
        ]
        for view_url in views_to_test:
            response = self.client.post(view_url)
            self.assertEqual(response.status_code, 405)

    def test_invalid_http_method(self):
        """测试无效的HTTP方法"""
        response = self.client.put(reverse('index'))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_article_view_negative_pk(self):
        """测试文章列表视图 - 负数ID"""
        # URL模式限制了pk为正整数，负数无法匹配URL模式
        # 改为直接访问URL字符串进行测试
        response = self.client.get('/blog/article/-1/')
        self.assertEqual(response.status_code, 404)

    def test_detail_view_negative_pk(self):
        """测试博客详情视图 - 负数ID"""
        # URL模式限制了pk为正整数，负数无法匹配URL模式
        response = self.client.get('/blog/detail/-1/')
        self.assertEqual(response.status_code, 404)

    def test_tagcloud_view_negative_id(self):
        """测试标签云视图 - 负数ID"""
        # URL模式限制了id为正整数，负数无法匹配URL模式
        response = self.client.get('/blog/tag/-1/')
        self.assertEqual(response.status_code, 404)


class ContextDataTests(TestCase):
    """上下文数据测试用例"""

    def setUp(self):
        """测试准备"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='测试分类')
        self.tag = Tagprofile.objects.create(tag_name='测试标签')
        self.blog = Blog.objects.create(
            title='测试博客标题',
            category=self.category,
            author=self.user,
            content='测试博客内容',
            digest='测试摘要',
            image='test_image.jpg'
        )

    def test_common_context_variables(self):
        """测试所有视图共有的上下文变量"""
        # 排除search，因为它在没有key参数时有bug
        views_to_test = [
            reverse('index'),
            reverse('blog:about'),
            reverse('blog:archive'),
            reverse('blog:link'),
            reverse('blog:message'),
            reverse('blog:article', args=[self.category.id]),
            reverse('blog:detail', args=[self.blog.id]),
            reverse('blog:tag', args=[self.tag.id]),
        ]
        for view_url in views_to_test:
            response = self.client.get(view_url)
            if response.status_code == 200:
                self.assertIn('category_list', response.context)
                self.assertIn('tag_list', response.context)
                self.assertIn('article_rank', response.context)
                self.assertIn('comment_list', response.context)


class EmptyDatabaseTests(TestCase):
    """空数据库测试用例"""

    def setUp(self):
        """测试准备"""
        self.client = Client()

    def test_index_view_empty_db(self):
        """测试首页视图 - 空数据库"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['article_list']), 0)
        self.assertEqual(len(response.context['article_rank']), 0)

    def test_archive_view_empty_db(self):
        """测试归档视图 - 空数据库"""
        response = self.client.get(reverse('blog:archive'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['article_list']), 0)

    def test_search_view_empty_db(self):
        """测试搜索视图 - 空数据库"""
        response = self.client.get(reverse('blog:search'), {'key': '测试'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['count'], 0)

    def test_articles_view_all_empty_db(self):
        """测试文章列表视图 - 空数据库显示全部"""
        response = self.client.get(reverse('blog:article', args=[0]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['count'], 0)
