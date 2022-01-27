from unittest import TestCase
from sqlalchemy import exc
from app import app
from models import db, User, Player, UserTeam



app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///nba_stats-test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]

db.drop_all()
db.create_all()

img_url = ("https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/")

class ModelsTestCase(TestCase):
    """ Test player search, player and stat calls, display for player and stats."""


    def setUp(self):
        """Create test player and add sample data."""
        db.drop_all()
        db.create_all()
        
        self.client = app.test_client()

        self.testuser1 = User.signup(
            username="test",
            email="test@test.com",
            password="testpword",
            image_url=None)

        self.testuser1_id = 2
        self.testuser1.id = self.testuser1_id

        db.session.commit()

        self.testuser2 = User.signup(
            username="test2",
            email="test@aol.com",
            password="passwrdtest2",
            image_url=None)

        self.testuser2_id = 100
        self.testuser2.id = self.testuser2_id

        db.session.commit()

        

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does user model work"""

        u = User(
            email="email@test.ca",
            username="testname",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit() 

        self.assertEqual(u.username, "testname")
    
    def test_valid_signup(self):
        u_test = User.signup(username="testtesttest", email="testtest@test.com", password="password", image_url="")
        uid = 109
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertEqual(u_test.email, "testtest@test.com")
        self.assertNotEqual(u_test.password, "password")
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "testagain@test.com", "password", None)
        uid = 123
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "password", None)
        uid = 1111
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)
    
    def test_valid_authentication(self):
        u = User.authenticate(self.testuser1.username, "testpword")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.testuser1.id)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "testpword"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.testuser1.username, "badpassword"))