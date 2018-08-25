from django import forms
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

User = get_user_model()


from .models import EmailActivation
from .signals import user_logged_in


class ReactivateEmailForm(forms.Form):
    email           = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = EmailActivation.objects.email_exists(email) #.filter(email=email | user__email=email).filter(activated=False)
        if not qs.exists():
            register_link = reverse('register')
            msg = """This email does not exist, would you like to <a href="{link}">register</a>?
                    """.format(link=register_link)
            raise forms.ValidationError(mark_safe(msg))
        return email


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'full_name') # 'full_name',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password', 'is_active', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class GuestForm(forms.Form):
    email = forms.EmailField()


class LoginForm(forms.Form):
    # username       = forms.EmailField(label='Email')
    email       = forms.EmailField(label='Email')
    password    = forms.CharField(
        widget=forms.PasswordInput()
    )

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        request = self.request

        data = self.cleaned_data
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is None:
            raise forms.ValidationError('Invalid credentials!')
        login(request, user)
        self.user = user
        user_logged_in.send(user.__class__, instance=user, request=request)
        try:
            del request.session['guest_email_id']
        except:
            pass
        return data

    # def form_valid(self, form):
    #             request = self.request
    #             next_ = request.GET.get('next')
    #             next_post = request.POST.get('next')
    #             redirect_path = next_ or next_post or None
                
                
    #             # print(user)
    #             # print('2.: user logged in: ' + str(request.user.is_authenticated()))
    #             if user is not None:
    #                     if not user.is_active:
    #                             messages.error(request, "This user is inactive")
    #                             return super(LoginView, self).form_invalid(form)
    #                     # print('3.: user logged in: ' + str(request.user.is_authenticated()))
    #                     login(request, user)
    #                     user_logged_in.send(user.__class__, instance=user, request=request)
    #                     try:
    #                             del request.session['guest_email_id']
    #                     except:
    #                             pass
    #                     # redirect to a success page.
    #                     if is_safe_url(redirect_path, request.get_host()):
    #                             return redirect(redirect_path)
    #                     else:
    #                             return redirect('/')
    #             return super(LoginView, self).form_invalid(form)



class RegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'full_name') # 'full_name',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False # send confirmation email via signals
        # obj = EmailActivation.objects.create(user=user)
        # obj.send_activation()
        if commit:
            user.save()
        return user


# class RegisterForm(forms.Form):
#     username = forms.CharField()
#     email = forms.EmailField()
#     password = forms.CharField(
#         widget=forms.PasswordInput
#     )
#     password2 = forms.CharField(
#         label='Confirm password',
#         widget=forms.PasswordInput
#     )

#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         qs = User.objects.filter(username=username)
#         if qs.exists():
#             raise forms.ValidationError('Username is taken')
#         return username

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         qs = User.objects.filter(email=email)
#         if qs.exists():
#             raise forms.ValidationError('Email is taken')
#         return email

#     def clean(self):
#         data = self.cleaned_data
#         password = self.cleaned_data.get('password')
#         password2 = self.cleaned_data.get('password2')
#         if password2 != password:
#                 raise forms.ValidationError('Passwords must match.')
#         return data
