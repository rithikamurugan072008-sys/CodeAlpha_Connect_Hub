from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from network.models import Profile, Post, Like, Comment, Follow, Bookmark, Notification


class SocialPlatformTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create test users
        self.user1 = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='testpassword123',
            first_name='Alice',
            last_name='Wonder'
        )
        self.user2 = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='testpassword123',
            first_name='Bob',
            last_name='Builder'
        )

        # Create sample post
        self.post1 = Post.objects.create(
            author=self.user1,
            content="Hello world! This is my first test post #Test #Pulse"
        )

    def test_user_profile_creation_signal(self):
        """Test that profile is automatically created when a user registers."""
        self.assertTrue(hasattr(self.user1, 'profile'))
        self.assertEqual(self.user1.profile.posts_count(), 1)
        self.assertEqual(self.user1.profile.followers_count(), 0)
        self.assertEqual(self.user1.profile.following_count(), 0)

    def test_like_system(self):
        """Test liking and unliking a post via API."""
        self.client.login(username='bob', password='testpassword123')

        # Like
        response = self.client.post(reverse('api_toggle_like', args=[self.post1.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['liked'])
        self.assertEqual(data['likes_count'], 1)
        self.assertTrue(Like.objects.filter(user=self.user2, post=self.post1).exists())

        # Unlike
        response = self.client.post(reverse('api_toggle_like', args=[self.post1.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['liked'])
        self.assertEqual(data['likes_count'], 0)
        self.assertFalse(Like.objects.filter(user=self.user2, post=self.post1).exists())

    def test_comment_system(self):
        """Test adding and deleting comments."""
        self.client.login(username='bob', password='testpassword123')

        # Add comment
        response = self.client.post(
            reverse('api_add_comment', args=[self.post1.id]),
            data={'content': 'Great post Alice!'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['comments_count'], 1)
        comment_id = data['comment']['id']

        # Delete comment
        del_response = self.client.post(reverse('api_delete_comment', args=[comment_id]))
        self.assertEqual(del_response.status_code, 200)
        del_data = del_response.json()
        self.assertEqual(del_data['comments_count'], 0)
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())

    def test_follow_system(self):
        """Test following and unfollowing another user."""
        self.client.login(username='bob', password='testpassword123')

        # Follow Alice
        response = self.client.post(reverse('api_toggle_follow', args=['alice']))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['is_following'])
        self.assertEqual(data['followers_count'], 1)
        self.assertEqual(self.user1.profile.followers_count(), 1)
        self.assertEqual(self.user2.profile.following_count(), 1)

        # Unfollow Alice
        response = self.client.post(reverse('api_toggle_follow', args=['alice']))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['is_following'])
        self.assertEqual(data['followers_count'], 0)
        self.assertEqual(self.user1.profile.followers_count(), 0)

    def test_bookmark_system(self):
        """Test bookmarking posts."""
        self.client.login(username='bob', password='testpassword123')

        response = self.client.post(reverse('api_toggle_bookmark', args=[self.post1.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['bookmarked'])
        self.assertTrue(Bookmark.objects.filter(user=self.user2, post=self.post1).exists())

    def test_feed_and_profile_views(self):
        """Test feed and profile view page rendering."""
        # Feed view
        res = self.client.get(reverse('feed'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Pulse')
        self.assertContains(res, 'Hello world!')

        # Profile view
        res = self.client.get(reverse('profile', args=['alice']))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '@alice')
        self.assertContains(res, 'Alice Wonder')

    def test_create_post_api(self):
        """Test creating post via API."""
        self.client.login(username='alice', password='testpassword123')

        response = self.client.post(reverse('api_create_post'), {
            'content': 'Another awesome post from Alice!'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['post']['content'], 'Another awesome post from Alice!')
        self.assertEqual(self.user1.posts.count(), 2)
