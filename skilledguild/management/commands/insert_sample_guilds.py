from django.core.management.base import BaseCommand
from skilledguild.models import Guild

class Command(BaseCommand):
    help = 'Insert sample guilds into the database.'

    def handle(self, *args, **options):
        sample_guilds = [
            {
                'name': 'Robotika',
                'description': 'A guild for robotics, AI, and automation enthusiasts.',
                'icon_url': 'https://cdn-icons-png.flaticon.com/512/4712/4712035.png',
                'theme_color': '#00b4d8',
            },
            {
                'name': 'Develepur',
                'description': 'Web and app development, coding, and software engineering.',
                'icon_url': 'https://cdn-icons-png.flaticon.com/512/2721/2721297.png',
                'theme_color': '#ff3c41',
            },
            {
                'name': 'CyberKnights',
                'description': 'Cybersecurity, hacking, and digital defense.',
                'icon_url': 'https://cdn-icons-png.flaticon.com/512/3062/3062634.png',
                'theme_color': '#6f42c1',
            },
            {
                'name': 'Datanauts',
                'description': 'Data science, analytics, and machine learning.',
                'icon_url': 'https://cdn-icons-png.flaticon.com/512/2721/2721298.png',
                'theme_color': '#ffba08',
            },
        ]
        for guild in sample_guilds:
            obj, created = Guild.objects.get_or_create(name=guild['name'], defaults=guild)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created guild: {guild['name']}"))
            else:
                self.stdout.write(f"Guild already exists: {guild['name']}")
