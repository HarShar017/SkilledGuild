from django import forms
from .models import TeamUpProfile, Team, TeamInvitation, Skill

SAMPLE_TAGS = [
    "Python", "Web Development", "AI", "Design", "Hackathons", "Robotics", "Machine Learning", "Data Science", "UI/UX", "Mobile Apps", "Game Dev", "Cloud", "Cybersecurity"
]

class TeamUpProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate skills/interests with sample tags if empty
        if Skill.objects.count() == 0:
            for tag in SAMPLE_TAGS:
                Skill.objects.get_or_create(name=tag)
        self.fields['skills'].queryset = Skill.objects.all().order_by('name')
        self.fields['interests'].queryset = Skill.objects.all().order_by('name')

    class Meta:
        model = TeamUpProfile
        fields = ['bio', 'skills', 'interests', 'city', 'state', 'country',
                 'availability_status', 'github_profile', 'linkedin_profile',
                 'portfolio_url']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'skills': forms.SelectMultiple(attrs={'class': 'form-multiselect'}),
            'interests': forms.SelectMultiple(attrs={'class': 'form-multiselect'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'state': forms.TextInput(attrs={'class': 'form-input'}),
            'country': forms.TextInput(attrs={'class': 'form-input'}),
            'availability_status': forms.Select(attrs={'class': 'form-select'}),
            'github_profile': forms.URLInput(attrs={'class': 'form-input'}),
            'linkedin_profile': forms.URLInput(attrs={'class': 'form-input'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-input'}),
        }

class TeamCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if Skill.objects.count() == 0:
            for tag in SAMPLE_TAGS:
                Skill.objects.get_or_create(name=tag)
        self.fields['required_skills'].queryset = Skill.objects.all().order_by('name')

    class Meta:
        model = Team
        fields = ['title', 'description', 'required_skills', 'max_members',
                 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'required_skills': forms.SelectMultiple(attrs={'class': 'form-multiselect'}),
            'max_members': forms.NumberInput(attrs={'class': 'form-input', 'min': 2}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

class TeamInvitationForm(forms.ModelForm):
    class Meta:
        model = TeamInvitation
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }