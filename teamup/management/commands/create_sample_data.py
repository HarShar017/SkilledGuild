from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from teamup.models import TeamUpProfile, Skill, Team

class Command(BaseCommand):
    help = 'Create sample data for TeamUp'
    
    def handle(self, *args, **options):
        # Create sample skills
        skills_data = [
            "Python", "JavaScript", "React", "Django", "Node.js", "Machine Learning",
            "Data Science", "UI/UX Design", "Mobile Development", "DevOps", "Cybersecurity",
            "Game Development", "Blockchain", "Cloud Computing", "AI/ML"
        ]
        
        skills = []
        for skill_name in skills_data:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            skills.append(skill)
            if created:
                self.stdout.write(f"Created skill: {skill_name}")
        
        # Create sample users if they don't exist
        sample_users = [
            {'username': 'alice_dev', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Johnson'},
            {'username': 'bob_designer', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Smith'},
            {'username': 'charlie_ml', 'email': 'charlie@example.com', 'first_name': 'Charlie', 'last_name': 'Brown'},
            {'username': 'diana_fullstack', 'email': 'diana@example.com', 'first_name': 'Diana', 'last_name': 'Wilson'},
        ]
        
        users = []
        for user_data in sample_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name']
                }
            )
            if created:
                user.set_password('password123')  # Demo password
                user.save()
                self.stdout.write(f"Created user: {user_data['username']}")
            users.append(user)
        
        # Create/update profiles with skills
        profile_updates = [
            {
                'user': users[0],
                'bio': 'Passionate Python developer with 3 years of experience in web development and automation.',
                'skills': ['Python', 'Django', 'JavaScript'],
                'interests': ['Machine Learning', 'AI/ML', 'Data Science'],
                'city': 'San Francisco',
                'state': 'CA',
                'country': 'USA'
            },
            {
                'user': users[1],
                'bio': 'Creative UI/UX designer focused on creating beautiful and intuitive user experiences.',
                'skills': ['UI/UX Design', 'JavaScript', 'React'],
                'interests': ['Mobile Development', 'Game Development'],
                'city': 'New York',
                'state': 'NY',
                'country': 'USA'
            },
            {
                'user': users[2],
                'bio': 'Machine Learning engineer specializing in computer vision and natural language processing.',
                'skills': ['Machine Learning', 'Python', 'Data Science'],
                'interests': ['AI/ML', 'Cloud Computing'],
                'city': 'Austin',
                'state': 'TX',
                'country': 'USA'
            },
            {
                'user': users[3],
                'bio': 'Full-stack developer with expertise in both frontend and backend technologies.',
                'skills': ['JavaScript', 'React', 'Node.js', 'Python'],
                'interests': ['DevOps', 'Cloud Computing', 'Cybersecurity'],
                'city': 'Seattle',
                'state': 'WA',
                'country': 'USA'
            }
        ]
        
        for profile_data in profile_updates:
            profile = profile_data['user'].teamup_profile
            profile.bio = profile_data['bio']
            profile.city = profile_data['city']
            profile.state = profile_data['state']
            profile.country = profile_data['country']
            profile.availability_status = 'available'
            profile.save()
            
            # Add skills
            user_skills = [skill for skill in skills if skill.name in profile_data['skills']]
            profile.skills.set(user_skills)
            
            # Add interests
            user_interests = [skill for skill in skills if skill.name in profile_data['interests']]
            profile.interests.set(user_interests)
            
            self.stdout.write(f"Updated profile for: {profile_data['user'].username}")
        
        # Create sample teams
        sample_teams = [
            {
                'title': 'AI Chatbot Project',
                'description': 'Building an intelligent chatbot using machine learning and natural language processing.',
                'creator': users[2],  # charlie_ml
                'required_skills': ['Python', 'Machine Learning', 'AI/ML'],
                'members': [users[2]],
                'max_members': 4
            },
            {
                'title': 'E-commerce Platform',
                'description': 'Developing a modern e-commerce platform with React frontend and Django backend.',
                'creator': users[0],  # alice_dev
                'required_skills': ['Python', 'Django', 'React', 'JavaScript'],
                'members': [users[0]],
                'max_members': 5
            },
            {
                'title': 'Mobile Fitness App',
                'description': 'Creating a cross-platform mobile app for fitness tracking and workout planning.',
                'creator': users[1],  # bob_designer
                'required_skills': ['Mobile Development', 'UI/UX Design', 'JavaScript'],
                'members': [users[1]],
                'max_members': 3
            }
        ]
        
        for team_data in sample_teams:
            team, created = Team.objects.get_or_create(
                title=team_data['title'],
                defaults={
                    'description': team_data['description'],
                    'creator': team_data['creator'],
                    'max_members': team_data['max_members'],
                    'status': 'open'
                }
            )
            
            if created:
                # Add required skills
                team_skills = [skill for skill in skills if skill.name in team_data['required_skills']]
                team.required_skills.set(team_skills)
                
                # Add members
                team.members.set(team_data['members'])
                
                self.stdout.write(f"Created team: {team_data['title']}")
            else:
                self.stdout.write(f"Team already exists: {team_data['title']}")
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))
