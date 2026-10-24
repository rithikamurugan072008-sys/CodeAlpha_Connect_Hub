from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from network.models import Profile, Post, Like, Comment, Follow, Notification


class Command(BaseCommand):
    help = 'Seeds initial sample data with realistic users, posts, comments, likes, and followers.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding social platform data...')

        users_data = [
            {
                'username': 'alex_rivera',
                'first_name': 'Alex',
                'last_name': 'Rivera',
                'email': 'alex@example.com',
                'bio': '🚀 Full-Stack Developer & UI Enthusiast. Building fluid web applications with Python & modern web tech. Always tinkering with micro-interactions.',
                'location': 'San Francisco, CA',
                'website': 'https://alexrivera.dev',
            },
            {
                'username': 'sophia_chen',
                'first_name': 'Sophia',
                'last_name': 'Chen',
                'email': 'sophia@example.com',
                'bio': '✨ Product Designer & Design Systems lead. Obsessed with typography, glassmorphism, and seamless UX flows. Coffee enthusiast ☕',
                'location': 'Seattle, WA',
                'website': 'https://sophiachen.design',
            },
            {
                'username': 'marcus_v',
                'first_name': 'Marcus',
                'last_name': 'Vance',
                'email': 'marcus@example.com',
                'bio': '⚡ Senior Backend Engineer & Open Source contributor. Scalable architecture, databases, and high-performance APIs. Rust + Python advocate.',
                'location': 'Austin, TX',
                'website': 'https://marcusv.io',
            },
            {
                'username': 'elena_ai',
                'first_name': 'Elena',
                'last_name': 'Rostova',
                'email': 'elena@example.com',
                'bio': '🧠 AI Research Scientist & Deep Learning practitioner. Exploring reasoning agents, multimodal LLMs, and creative neural synthesis.',
                'location': 'Boston, MA',
                'website': 'https://elena-ai.org',
            },
            {
                'username': 'maya_cloud',
                'first_name': 'Maya',
                'last_name': 'Patel',
                'email': 'maya@example.com',
                'bio': '☁️ Cloud Solutions Architect & Kubernetes fan. Scaling distributed systems and cloud infrastructure. Open source maintainer.',
                'location': 'New York, NY',
                'website': 'https://mayacloud.tech',
            },
        ]

        created_users = {}
        for u_data in users_data:
            user, created = User.objects.get_or_create(
                username=u_data['username'],
                defaults={
                    'first_name': u_data['first_name'],
                    'last_name': u_data['last_name'],
                    'email': u_data['email']
                }
            )
            user.set_password('password123')
            user.first_name = u_data['first_name']
            user.last_name = u_data['last_name']
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.bio = u_data['bio']
            profile.location = u_data['location']
            profile.website = u_data['website']
            profile.save()

            created_users[u_data['username']] = user
            self.stdout.write(f"Created/updated user: @{user.username}")

        # Follow relationships
        follow_pairs = [
            ('alex_rivera', 'sophia_chen'),
            ('alex_rivera', 'marcus_v'),
            ('alex_rivera', 'elena_ai'),
            ('sophia_chen', 'alex_rivera'),
            ('sophia_chen', 'elena_ai'),
            ('marcus_v', 'alex_rivera'),
            ('marcus_v', 'maya_cloud'),
            ('elena_ai', 'alex_rivera'),
            ('elena_ai', 'marcus_v'),
            ('elena_ai', 'sophia_chen'),
            ('maya_cloud', 'marcus_v'),
            ('maya_cloud', 'alex_rivera'),
            ('maya_cloud', 'sophia_chen'),
        ]

        for follower_uname, following_uname in follow_pairs:
            follower = created_users[follower_uname]
            following = created_users[following_uname]
            Follow.objects.get_or_create(follower=follower, following=following)

        # Clear existing posts to prevent duplicates when re-seeding
        Post.objects.all().delete()

        # Posts
        posts_data = [
            {
                'author': 'alex_rivera',
                'content': "Just completed shipping a brand new responsive glassmorphic dashboard! 🚀 The feeling when micro-animations line up with 60fps smoothness is unmatched. What are your favorite CSS transition properties to play with? #WebDevelopment #Frontend #DesignSystems",
                'image': 'posts/glassmorphic_dashboard.jpg',
            },
            {
                'author': 'sophia_chen',
                'content': "Design tip of the day: High contrast doesn't mean harsh pure black and pure white. Deep rich slates (#0f172a) combined with subtle indigo glows create an atmosphere that feels truly premium and easy on the eyes. 🎨 #UIUX #DesignInspiration #Creatives",
                'image': 'posts/design_system_tokens.jpg',
            },
            {
                'author': 'marcus_v',
                'content': "Optimized our relational database queries today using Django select_related & prefetch_related. Query count dropped from 142 down to just 3! 📉 Database connection latency matters just as much as caching layers. #DjangoPython #BackendDev #DatabaseOptimization",
                'image': 'posts/database_query_optimization.jpg',
            },
            {
                'author': 'elena_ai',
                'content': "Working on autonomous agent workflows today. The shift from single prompt-response loops to agentic systems with memory, self-correction, and tool invocation is redefining software engineering! 🤖⚡ What agents are you building? #ArtificialIntelligence #MachineLearning #TechInnovation",
                'image': 'posts/ai_agent_workflow.jpg',
            },
            {
                'author': 'maya_cloud',
                'content': "Migrated another batch of stateless workloads to Kubernetes multi-cluster today with zero downtime. Automated failover tests passed on the first run! ☁️ Celebrate the small wins, team! #CloudNative #DevOps #Kubernetes",
                'image': 'posts/kubernetes_cloud_cluster.jpg',
            },
            {
                'author': 'alex_rivera',
                'content': "Building social applications with Django and clean vanilla JavaScript is surprisingly refreshing. No heavy bundle sizes, instant loads, and complete control over every pixel. Simplicity is an art form. 💻✨ #WebDev #FullStack #JavaScript",
                'image': 'posts/django_vanilla_code.jpg',
            },
            {
                'author': 'sophia_chen',
                'content': "Working on a new icon library with 2px optical stroke widths. Consistency across icons makes user interfaces feel 10x more polished. Here's to details that users feel even if they don't consciously notice them! 📐 #VisualDesign #Iconography",
                'image': 'posts/icon_design_system.jpg',
            }
        ]

        created_posts = []
        for p in posts_data:
            post = Post.objects.create(
                author=created_users[p['author']],
                content=p['content'],
                image=p.get('image', '')
            )
            created_posts.append(post)

        # Comments
        comments_data = [
            (created_posts[0], 'sophia_chen', "Totally agree! Especially cubic-bezier easing curves. They make everything feel natural and tactile."),
            (created_posts[0], 'marcus_v', "Clean UI! Make sure GPU acceleration with transform: translateZ(0) is active if you have heavy blurs."),
            (created_posts[1], 'alex_rivera', "Bookmarking this! Deep slate palettes look so much better than pitch black OLED themes."),
            (created_posts[1], 'elena_ai', "The indigo glow accent gives such a sci-fi modern vibe. Love it!"),
            (created_posts[2], 'maya_cloud', "Huge win! N+1 queries are the silent killers of production databases."),
            (created_posts[2], 'alex_rivera', "prefetch_related with Prefetch objects changed my life back when I first discovered it!"),
            (created_posts[3], 'marcus_v', "The tool-calling integration pattern is definitely where the magic happens."),
            (created_posts[3], 'alex_rivera', "Fascinating work Elena! Are you evaluating local models or API-driven agents?"),
            (created_posts[5], 'sophia_chen', "Vanilla JS with CSS variables is genuinely so powerful nowadays. So glad people are rediscovering it!"),
        ]

        for post, author_uname, comment_text in comments_data:
            Comment.objects.create(
                post=post,
                author=created_users[author_uname],
                content=comment_text
            )

        # Likes
        like_matrix = [
            (created_posts[0], ['sophia_chen', 'marcus_v', 'elena_ai', 'maya_cloud']),
            (created_posts[1], ['alex_rivera', 'elena_ai', 'maya_cloud']),
            (created_posts[2], ['alex_rivera', 'maya_cloud', 'sophia_chen']),
            (created_posts[3], ['alex_rivera', 'marcus_v', 'sophia_chen', 'maya_cloud']),
            (created_posts[4], ['marcus_v', 'alex_rivera']),
            (created_posts[5], ['sophia_chen', 'marcus_v', 'elena_ai']),
            (created_posts[6], ['alex_rivera', 'sophia_chen', 'maya_cloud']),
        ]

        for post, usernames in like_matrix:
            for uname in usernames:
                Like.objects.get_or_create(post=post, user=created_users[uname])

        self.stdout.write(self.style.SUCCESS('Successfully seeded sample database with users, posts, comments, likes, and follows!'))
