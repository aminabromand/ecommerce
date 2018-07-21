from django.contrib.auth import authenticate, login, get_user_model
from django.views.generic import CreateView, FormView
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from .forms import LoginForm, RegisterForm, GuestForm
from .models import GuestEmail
from .signals import user_logged_in

# Create your views here.

def guest_register_view(request):
        form = GuestForm(request.POST or None)
        context = {
                'form': form
        }
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if form.is_valid():
                email = form.cleaned_data.get('email')
                new_guest_email = GuestEmail.objects.create(email=email)
                request.session['guest_email_id'] = new_guest_email.id
                if is_safe_url(redirect_path, request.get_host()):
                        return redirect(redirect_path)
                else:
                        return redirect('/register/')
        return redirect('/register/')


class LoginView(FormView):
        form_class = LoginForm
        success_url = '/'
        template_name = 'accounts/login.html'

        def form_valid(self, form):
                request = self.request
                next_ = request.GET.get('next')
                next_post = request.POST.get('next')
                redirect_path = next_ or next_post or None
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=email, password=password)
                # print(user)
                # print('2.: user logged in: ' + str(request.user.is_authenticated()))
                if user is not None:
                        # print('3.: user logged in: ' + str(request.user.is_authenticated()))
                        login(request, user)
                        user_logged_in.send(user.__class__, instance=user, request=request)
                        try:
                                del request.session['guest_email_id']
                        except:
                                pass
                        # redirect to a success page.
                        if is_safe_url(redirect_path, request.get_host()):
                                return redirect(redirect_path)
                        else:
                                return redirect('/')
                return super(LoginView, self).form_invalid(form)


# def login_page(request):
#         form = LoginForm(request.POST or None)
#         context = {
#                 'form': form
#         }
#         # print('1.: user logged in: ' + str(request.user.is_authenticated()))
#         next_ = request.GET.get('next')
#         next_post = request.POST.get('next')
#         redirect_path = next_ or next_post or None
#         if form.is_valid():
#                 # print('cleaned data: ' + str(form.cleaned_data))
#                 # username = form.cleaned_data.get('username')
#                 email = form.cleaned_data.get('email')
#                 password = form.cleaned_data.get('password')
#                 # user = authenticate(request, username=username, password=password)
#                 user = authenticate(request, username=email, password=password)
#                 # print(user)
#                 # print('2.: user logged in: ' + str(request.user.is_authenticated()))
#                 if user is not None:
#                         # print('3.: user logged in: ' + str(request.user.is_authenticated()))
#                         login(request, user)
#                         try:
#                                 del request.session['guest_email_id']
#                         except:
#                                 pass
#                         # redirect to a success page.
#                         if is_safe_url(redirect_path, request.get_host()):
#                                 return redirect(redirect_path)
#                         else:
#                                 return redirect('/')
#                 else:
#                         # return an 'invalid login' error message.
#                         print('Error')
        
#         return render(request, 'accounts/login.html', context)


class RegisterView(CreateView):
        form_class = RegisterForm
        template_name = 'accounts/register.html'
        success_url = '/login/'


# User = get_user_model()
# def register_page(request):
#         form = RegisterForm(request.POST or None)
#         context = {
#                 'form': form
#         }

#         if form.is_valid():
#                 form.save()
#                 # print(form.cleaned_data)
#                 # username = form.cleaned_data.get('username')
#                 # email = form.cleaned_data.get('email')
#                 # password = form.cleaned_data.get('password')
#                 # new_user = User.objects.create_user(username, email, password)
#                 # print(new_user)
#         return render(request, 'accounts/register.html', context)
