from django import forms
from django.contrib.auth.models import User
from .models import Profile, Post, Comment


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Create a password (min 6 characters)',
        'required': True
    }))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Confirm your password',
        'required': True
    }))
    bio = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-input form-textarea',
        'placeholder': 'Tell the world about yourself...',
        'rows': 3
    }), required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. alex_rivera', 'required': True}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'name@example.com', 'required': True}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Passwords do not match.')
        return cleaned_data


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Profile
        fields = ['bio', 'location', 'website', 'avatar', 'cover_image']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-input form-textarea', 'rows': 3, 'placeholder': 'Your bio...'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. San Francisco, CA'}),
            'website': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://yourwebsite.com'}),
            'avatar': forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'composer-textarea',
                'placeholder': "What's happening in your universe?",
                'rows': 3,
                'maxlength': 2000
            }),
            'image': forms.FileInput(attrs={
                'class': 'composer-file-input',
                'accept': 'image/*',
                'id': 'post-image-input'
            })
        }
