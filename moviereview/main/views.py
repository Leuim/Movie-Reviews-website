from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.urls import reverse
from django.views import View
from main.models import User, Session, Review, Comment


# Create your views here.
class HomeView(View):
    def get(self, request):
        user = Session.get_user_data(session_id=request.COOKIES.get('sid'))
        email = user.email if user else None

        reviews = Review.objects.all()

        return render(request, 'home.html', context={'title': 'Home', 'reviews': reviews, 'user': email})


class SignupView(View):
    def get(self, request):
        user = Session.get_user_data(session_id=request.COOKIES.get('sid'))
        email = user.email if user else None
        
        exists = request.GET.get('exists')

        return render(request, 'signup.html', context={'title': 'Sign Up', 'exists': exists, 'user': email})

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects(email=email):
            return redirect(reverse('signup') + '?exists=true')

        user = User(email=email)
        user.set_password(password)
        user.save()

        session = Session(user=user)
        session.generate_session_id()
        session.save()

        # Redirect the user to the home page after saving his session ID as a cookie on the client side.
        content = render_to_string('home.html', context={'title': 'Home', 'user': user.email})
        response = HttpResponse(content)
        response.set_cookie('sid', session.session_id)
        return response


class LoginView(View):
    def get(self, request):
        user = Session.get_user_data(session_id=request.COOKIES.get('sid'))
        email = user.email if user else None

        valid = request.GET.get('valid')
        return render(request, 'login.html', context={'title': 'Log In', 'valid': valid, 'user': email})

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        query = User.objects(email=email)
        if not query:
            return redirect(reverse('login') + '?valid=false')

        user: User = query.first()
        if not user.verify_password(password):
            return redirect(reverse('login') + '?valid=false')

        Session.objects(user=user).all().delete() # Delete any previous sessions.

        session = Session(user=user)
        session.generate_session_id()
        session.save()

        content = render_to_string('home.html', context={'title': 'Home', 'user': user.email})
        response = HttpResponse(content)
        response.set_cookie('sid', session.session_id)
        return response


class LogoutView(View):
    def get(self, request):
        content = render_to_string('home.html', context={'title': 'Home'})
        response = HttpResponse(content)
        response.delete_cookie('sid')
        return response


class PostReviewView(View):
    def get(self, request):
        user = Session.get_user_data(session_id=request.COOKIES.get('sid'))
        email = user.email if user else None

        success = request.GET.get('success')

        return render(request, 'post_review.html', context={'title': 'Post A Review', 'success': success, 'user': email})

    def post(self, request):
        user = Session.get_user_data(session_id=request.COOKIES.get('sid'))
        
        movie = request.POST.get('movie')
        text = request.POST.get('text')

        review = Review(movie=movie, text=text, author=user)
        review.save()

        return redirect(reverse('post-review') + '?success=true')


class ReviewView(View):
    def get(self, request, id):
        user = Session.get_user_data(session_id=request.COOKIES.get('sid'))
        email = user.email if user else None

        review = Review.objects(id=id).first()

        return render(request, 'review.html', context={'title': review.movie + ' - Review', 'review': review, 'user': email})


class PostCommentView(View):
    def post(self, request, review_id):
        user = Session.get_user_data(session_id=request.COOKIES.get('sid'))
        
        review: Review = Review.objects(id=review_id).first()

        text = request.POST.get('text')
        comment = Comment(review=review, text=text, author=user)
        comment.save()

        review.comments.append(comment)
        review.save()
        
        return redirect('review', id=str(review.id))
