from django.test import TestCase
from django.contrib.auth import get_user_model

from hub.models import Card, Category, Collection

User = get_user_model()


def make_collection(name="Python", slug="python"):
    return Collection.objects.create(name=name, slug=slug, is_active=True)


def make_category(collection, name="OOP"):
    return Category.objects.create(name=name, collection=collection)


def make_user(username="testuser", collection=None):
    user = User.objects.create_user(username=username, password="Pass1234!")
    if collection:
        user.active_collection = collection
        user.save()
    return user


def make_card(owner, category, status=Card.Status.NEW):
    return Card.objects.create(
        owner=owner,
        category=category,
        level="junior",
        question="What is OOP?",
        answer="A paradigm.",
        status=status,
    )


class CollectionModelTest(TestCase):
    def test_str_returns_name(self):
        collection = make_collection()
        self.assertEqual(str(collection), "Python")

    def test_is_active_default_true(self):
        collection = make_collection(name="Go", slug="go")
        self.assertTrue(collection.is_active)


class CardModelTest(TestCase):
    def setUp(self):
        self.collection = make_collection()
        self.category = make_category(self.collection)
        self.user = make_user(collection=self.collection)

    def test_default_status_is_new(self):
        card = make_card(self.user, self.category)
        self.assertEqual(card.status, Card.Status.NEW)

    def test_is_custom_default_false(self):
        card = make_card(self.user, self.category)
        self.assertFalse(card.is_custom)

    def test_status_choices_exist(self):
        statuses = [s.value for s in Card.Status]
        self.assertIn("new", statuses)
        self.assertIn("learning", statuses)
        self.assertIn("known", statuses)
        self.assertIn("mastered", statuses)


class StatusTransitionTest(TestCase):
    def setUp(self):
        self.collection = make_collection()
        self.category = make_category(self.collection)
        self.user = make_user(collection=self.collection)

    def _post_status(self, card, action):
        self.client.force_login(self.user)
        self.client.post(
            f"/cards/{card.pk}/status/",
            {"action": action},
        )
        card.refresh_from_db()

    def test_know_from_new_gives_known(self):
        card = make_card(self.user, self.category, status=Card.Status.NEW)
        self._post_status(card, "know")
        self.assertEqual(card.status, Card.Status.KNOWN)

    def test_dont_know_from_new_gives_learning(self):
        card = make_card(self.user, self.category, status=Card.Status.NEW)
        self._post_status(card, "dont_know")
        self.assertEqual(card.status, Card.Status.LEARNING)

    def test_know_from_learning_gives_mastered(self):
        card = make_card(self.user, self.category, status=Card.Status.LEARNING)
        self._post_status(card, "know")
        self.assertEqual(card.status, Card.Status.MASTERED)


class CardListViewTest(TestCase):
    def setUp(self):
        self.collection = make_collection()
        self.category = make_category(self.collection)
        self.user = make_user(collection=self.collection)

    def test_redirects_anonymous_to_login(self):
        response = self.client.get("/cards/")
        self.assertRedirects(response, "/accounts/login/?next=/cards/")

    def test_redirects_to_track_if_no_collection(self):
        user = make_user(username="notrack")
        self.client.force_login(user)
        response = self.client.get("/cards/")
        self.assertRedirects(response, "/select_collection/")

    def test_shows_only_own_cards(self):
        other_user = make_user(username="other", collection=self.collection)
        make_card(self.user, self.category)
        make_card(other_user, self.category)
        self.client.force_login(self.user)
        response = self.client.get("/cards/")
        self.assertEqual(response.status_code, 200)
        cards = list(response.context["cards"])
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].owner, self.user)


class CardCreateViewTest(TestCase):
    def setUp(self):
        self.collection = make_collection()
        self.category = make_category(self.collection)
        self.user = make_user(collection=self.collection)
        self.client.force_login(self.user)

    def test_create_card_saves_to_db(self):
        self.client.post("/cards/create/", {
            "level": "junior",
            "category": self.category.pk,
            "question": "What is a decorator?",
            "answer": "A function wrapper.",
        })
        self.assertTrue(
            Card.objects.filter(
                owner=self.user,
                question="What is a decorator?",
            ).exists()
        )

    def test_created_card_is_custom(self):
        self.client.post("/cards/create/", {
            "level": "junior",
            "category": self.category.pk,
            "question": "What is a closure?",
            "answer": "A function with scope.",
        })
        card = Card.objects.get(owner=self.user, question="What is a closure?")
        self.assertTrue(card.is_custom)

    def test_created_card_status_is_new(self):
        self.client.post("/cards/create/", {
            "level": "junior",
            "category": self.category.pk,
            "question": "What is GIL?",
            "answer": "Global Interpreter Lock.",
        })
        card = Card.objects.get(owner=self.user, question="What is GIL?")
        self.assertEqual(card.status, Card.Status.NEW)
