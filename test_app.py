from unittest import TestCase
from sqlalchemy import exc
from app import app, CURR_USER_KEY
from models import db, User, Player, UserTeam



app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///nba_stats-test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

img_url = ("https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/")

class AppTestCase(TestCase):
    """ Test player search, player and stat calls, display for player and stats."""


    def setUp(self):
        """Create test player and add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        testplayer1 = Player(
            id = 1630224,
            first_name = "Jalen",
            last_name =  "Green",
            full_name = 'Jalen Green',
            player_img = img_url + str(1630224) + ".png",
        )
        db.session.add(testplayer1)
        db.session.commit()

        testuser = User.signup(
            username="test",
            email="test@test.com",
            password="testpword",
            image_url=None)

        db.session.add(testuser)
        db.session.commit()



        self.testplayer1 = testplayer1
        self.testuser = testuser
        self.player1 = Player.query.get(self.testplayer1.id)
        self.userid = User.query.get(self.testuser.id)


        userteam = UserTeam(
            player_id=self.testplayer1.id,
            user_id=self.testuser.id,
        )

        db.session.add(userteam)
        db.session.commit()
    
        self.userteam = userteam

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_home_page(self):
        """Check if home page renders properly"""
        with self.client as c:
            resp = c.get("/home")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Enter Player Name", html)


    def test_user_signup_page(self):

        with self.client as c:
            resp = c.get("/signup")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("signup_form", html)

    def test_signup_form(self):
        """check if signup redirect is a success"""
        with self.client as c:
            data={"username": "theGrinch", "email": "grinch@yahoo.com", "password": "whoville123", "image_url":""}
            resp = c.post("/signup", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("image-user", html)


    def test_user_login_page(self):
        with self.client as c:
            resp = c.get("/login")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("login_form", html)

    def test_login_form(self):
        """check if signup redirect is a success"""
        with self.client as c:
            data={"username":"test", "email": "test@test.com", "password": "testpword", "image_url": ""}
            resp = c.post("/login", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("image-user", html)


    def test_player_page(self):
        """test that the player's stat page renders and displays tables"""
        with self.client as c:
            resp = c.get(f"/stats/{ self.testplayer1.id }")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("thead", html)
            self.assertIn("FPTS", html)



    def test_user_createteam_submit(self):
        """test the rendering of the createteam page"""
        with self.client as c:
            data={"user_id": "1", "player_id": "1630224"}
            resp = c.post(f"/users/{ self.testuser.id }/team/new", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Search For NBA Player's Here:", html)
    
            