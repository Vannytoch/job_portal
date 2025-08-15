from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserForm, CustomLoginForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from .models import UserInfo, PasswordResetOTP, CustomUser
from jobs.models import Job
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
import random
from django.contrib import messages

# ... your existing imports ...

def register(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            # Generate OTP
            otp = str(random.randint(100000, 999999))

            # Save form data & OTP in session (serialize form.cleaned_data)
            request.session['register_form_data'] = form.cleaned_data
            request.session['register_otp'] = otp

            # Send OTP email
            email = form.cleaned_data['email']
            send_mail(
                'Verify your email - OTP Code',
                f'Your verification code is: {otp}',
                None,
                [email],
                fail_silently=False
            )

            messages.info(request, 'OTP sent to your email. Please verify.')

            # Render registration page with OTP modal open
            return render(request, 'users/register.html', {
                'open_modal': 'verifyOtpModal',
                'email': email,
            })

        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = CustomUserForm()

    return render(request, 'users/register.html', {'form': form})

def verify_registration_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        saved_otp = request.session.get('register_otp')
        form_data = request.session.get('register_form_data')

        if not saved_otp or not form_data:
            messages.error(request, 'Session expired, please register again.')
            return redirect('register')

        if otp == saved_otp:
            # Create user now
            user = CustomUser(
                username=form_data['username'],
                email=form_data['email'],
                # hash password properly:
                password=make_password(form_data['password1']),  # or form_data['password']
            )
            user.save()

            # Create user info (if needed)
            UserInfo.objects.create(user=user)

            # Clear session
            del request.session['register_otp']
            del request.session['register_form_data']

            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            return render(request, 'users/register.html', {
                'open_modal': 'verifyOtpModal',
                'email': form_data.get('email', ''),
                'error': 'Invalid OTP. Please try again.',
            })

    return redirect('register')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('/')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        info = request.user.info
        info.phone = request.POST.get('phone', info.phone)
        info.location = request.POST.get('location', info.location)
        info.company = request.POST.get('company', info.company)
        info.job_title = request.POST.get('job_title', info.job_title)
        info.education = request.POST.get('education', info.education)
        info.description = request.POST.get('description', info.description)

        profile_image = request.FILES.get('profile_image')
        if request.POST.get('dob'):
            print(request.POST.get('dob'))
            info.dob = request.POST.get('dob')
        else:
            info.dob = None 
            
        if profile_image:
            info.image = profile_image

        info.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return redirect('profile')

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)

    if request.method == "POST":
        job.title = request.POST.get('title')
        job.description = request.POST.get('description')
        job.company = request.POST.get('company')
        job.location = request.POST.get('location')
        job.is_active = 'is_active' in request.POST

        try:
            job.salary_min = float(request.POST.get('salary_min') or 0)
            job.salary_max = float(request.POST.get('salary_max') or 0)
            job.save()
            messages.success(request, "Job updated successfully.")
        except ValueError:
            messages.error(request, "Please enter valid numeric values for salary.")
            return redirect('profile')

        return redirect('profile')

    return redirect('profile')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

def forgot_password_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            otp = str(random.randint(100000, 999999))  # 6-digit OTP

            PasswordResetOTP.objects.create(user=user, otp=otp)

            send_mail(
                'Your Password Reset OTP',
                f'Your OTP code is: {otp}. It will expire in 10 minutes.',
                None,
                [email],
                fail_silently=False
            )

            request.session['reset_user_id'] = user.id

            messages.success(request, 'OTP sent to your email.')
            return render(request, 'users/login.html', {
                'open_modal': 'verifyOtpModal',
                'email_sent': True,
            })

        except CustomUser.DoesNotExist:
            messages.error(request, 'Email address not found.')
            return render(request, 'users/login.html', {
                'open_modal': 'forgotPasswordModal',
            })

    return render(request, 'users/login.html', {
        'open_modal': 'forgotPasswordModal',
    })

def verify_otp(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'Please request password reset first.')
        return redirect('forgot_password')

    if request.method == 'POST':
        otp = request.POST.get('otp')
        try:
            otp_entry = PasswordResetOTP.objects.filter(user_id=user_id, otp=otp).latest('created_at')
            if otp_entry.is_expired():
                messages.error(request, 'OTP expired. Please request a new one.')
                return render(request, 'users/login.html', {
                    'open_modal': 'verifyOtpModal',
                })
            messages.success(request, 'OTP verified. Please reset your password.')
            return render(request, 'users/login.html', {
                'open_modal': 'resetPasswordModal',
            })
        except PasswordResetOTP.DoesNotExist:
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, 'users/login.html', {
                'open_modal': 'verifyOtpModal',
            })

    return render(request, 'users/login.html', {
        'open_modal': 'verifyOtpModal',
    })

def reset_password(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'Please request password reset first.')
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password')
        if not password:
            messages.error(request, 'Password cannot be empty.')
            return render(request, 'users/login.html', {
                'open_modal': 'resetPasswordModal',
            })

        user = CustomUser.objects.get(id=user_id)
        user.password = make_password(password)
        user.save()

        del request.session['reset_user_id']

        messages.success(request, 'Password reset successful! You can now log in.')
        return redirect('login')

    return render(request, 'users/login.html', {
        'open_modal': 'resetPasswordModal',
    })

@login_required
def reset_password_on_profile(request):
    if request.method == "POST":
        current = request.POST.get('current_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')
        user = request.user

        if not user.check_password(current):
            messages.error(request, "Current password is incorrect.")
        elif new != confirm:
            messages.error(request, "New passwords do not match.")
        else:
            try:
                validate_password(new, user)
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
            else:
                user.set_password(new)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password successfully changed.")
                return redirect('profile')

    return redirect('profile')