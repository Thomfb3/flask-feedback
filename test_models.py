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


class UserModelTestCase(TestCase):
    """Tests for model for Users."""

    def setUp(self): 
        """Clean up any existing users."""
        User.query.delete()

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()


    def test_user_properties(self):
        username="John" 
        password="password"
        email="test@test.com"
        first_name="John"
        last_name="Smith"
        is_admin=True

        user = User.register(username, password, email, first_name, last_name, is_admin)

        db.session.add(user)
        db.session.commit()

        self.assertEqual(user.username, "John")
        self.assertNotEqual(user.password, "password")
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Smith")
        self.assertEqual(user.is_admin, True)

    


class FeedbackModelTestCase(TestCase):
    """Tests for model for Feedback."""

    def setUp(self): 
        """Clean up any existing Feedback."""
        Feedback.query.delete()

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()


    def test_post_properties(self):

        username="Bob" 
        password="password"
        email="other@test.com"
        first_name="Bob"
        last_name="Smith"
        is_admin=True

        user = User.register(username, password, email, first_name, last_name, is_admin)
        
        feedback = Feedback(title="This is Feedback", content="This is some test post content. It should be longer than 50 characters to test shorten content method.", username="Bob")

        self.assertEqual(feedback.title, "This is Feedback")
        self.assertEqual(feedback.content, "This is some test post content. It should be longer than 50 characters to test shorten content method.")
        self.assertEqual(feedback.username, "Bob")


