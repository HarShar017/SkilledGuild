from django.core.management.base import BaseCommand
from teamup.models import Skill

class Command(BaseCommand):
    help = 'Insert sample skills into the database.'

    def handle(self, *args, **options):
        skills = [
            ('Python', 'Programming'),
            ('Django', 'Web Development'),
            ('JavaScript', 'Programming'),
            ('React', 'Web Development'),
            ('UI/UX Design', 'Design'),
            ('Machine Learning', 'AI'),
            ('Data Analysis', 'Data'),
            ('Project Management', 'Management'),
            ('DevOps', 'Infrastructure'),
            ('Mobile App Development', 'Mobile'),
            ('C++', 'Programming'),
            ('Java', 'Programming'),
            ('Figma', 'Design'),
            ('Public Speaking', 'Soft Skill'),
            ('Team Leadership', 'Soft Skill'),
        ]
        for name, category in skills:
            Skill.objects.get_or_create(name=name, category=category)
        self.stdout.write(self.style.SUCCESS('Sample skills inserted.'))
