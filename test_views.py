from unittest import TestCase

from flask import Flask, request, render_template, redirect, flash, session

from app import app
from models import db, User, Feedback

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_test'
app.config['SQLALCHEMY_ECHO'] = False
# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()



class UserViewsTestCase(TestCase):
    """Tests for views for User."""
    def setUp(self):
        """Add sample User."""
        User.query.delete()
        
        username="John" 
        password="1234"
        email="test@test.com"
        first_name="John"
        last_name="Smith"
        is_admin=True

        user = User.register(username=username, pwd=password, email=email, first_name=first_name, last_name=last_name, is_admin=is_admin)

        db.session.add(user)
        db.session.commit()

        self.username = user.username



    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()



    def test_user_profile(self):
        """Test profile page"""

        with app.test_client() as client:
            resp = client.get(f"/users/{self.username}")
            html = resp.get_data(as_text=True)
      
            self.assertEqual(resp.status_code, 302)
            self.assertIn('Sign Up', html)
            self.assertIn('Smith', html)
            self.assertIn('test@test.com', html)
            self.assertIn('See all Users', html)
            self.assertIn('See all Feedback', html)

    

    def test_user_add_feedback(self):
        """Test add Feedback"""
        with app.test_client() as client:

            resp = client.get(f"/users/{self.username}/feedback/add")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            # Feedback from fields
            self.assertIn('Provide Feedback', html)
            self.assertIn('Title', html)
            self.assertIn('Content', html)


    def test_delete_user(self):
        """Delete this User"""
        with app.test_client() as client:
            resp = client.get(f"/users/{self.username}/delete")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)






class FeedbackViewsTestCase(TestCase):
    """Tests for views for Feedback."""

    def setUp(self):
        """Add sample User."""
        User.query.delete()
        Feedback.query.delete()

        username="Bob" 
        password="password"
        email="other@test.com"
        first_name="Bob"
        last_name="Smith"
        is_admin=True

        user = User.register(username, password, email, first_name, last_name, is_admin)
        
        db.session.add(user)
        db.session.commit()

      
        self.username = user.username

        feedback = Feedback(title="This is Feedback", content="This is some test post content. It should be longer than 50 characters to test shorten content method.", username="Bob")
        
        db.session.add(feedback)
        db.session.commit()

        self.id = feedback.id


    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()



    def test_update_feedback(self):
        """Update feedback view"""
        with app.test_client() as client:
            resp = client.post(f"/feedback/{self.id}/update", data={'title': 'Test', 'content': "hello there"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Feedback Updated.', html)
    
    

    def test_delete_feedback(self):
        """Delete this feedback"""
        with app.test_client() as client:
            resp = client.get(f"/feedback/{self.id}/delete")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)

