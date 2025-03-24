from django import forms
from .models import Job, Application, Category

class JobForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    job_type = forms.ChoiceField(
        choices=Job.JOB_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    experience_level = forms.ChoiceField(
        choices=Job.EXPERIENCE_LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Job
        fields = [
            'title', 'category', 'description', 'requirements',
            'location', 'salary', 'job_type', 'experience_level', 'deadline'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'requirements': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'salary': forms.TextInput(attrs={'class': 'form-control'}),
        }



class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(
                attrs={
                    'rows': 4, 
                    'placeholder': 'Write your cover letter here...',
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-custom focus:border-custom bg-white text-gray-900'
                }
            )
        }

class JobSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Job title or keyword'}
    ))
    location = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Location'}
    ))
    category = forms.ChoiceField(required=False)
    job_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + Job.JOB_TYPE_CHOICES
    )

class JobPostForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'salary', 'job_type']