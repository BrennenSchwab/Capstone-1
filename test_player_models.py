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

        self.client = app.test_client()

        testplayer = Player(
            id = 1630224,
            first_name = "Jalen",
            last_name =  "Green",
            full_name = 'Jalen Green',
            player_img = img_url + str(1630224) + ".png",
        )
        db.session.add(testplayer)
        db.session.commit()

        testuser = User.signup(
            username="test",
            email="test@test.com",
            password="testpword",
            image_url=None)

        db.session.add(testuser)
        db.session.commit()

        self.testplayer = testplayer
        self.testuser = testuser
        self.player = Player.query.get(self.testplayer.id)
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_player_model(self):
        """does player model store player values"""

        p = Player(
            id = 201939,
            first_name = "Stephen",
            last_name =  "Curry",
            full_name = 'Stephen Curry',
            player_img = img_url + "201939" + ".png",
        )

        db.session.add(p)
        db.session.commit()

        self.assertEqual(p.player_img, "https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/201939.png")


    