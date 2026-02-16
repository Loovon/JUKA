from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from messaging.models import Message, Conversation, Notification
from sellers.models import Shop, Advert
from categories.models import Category
from django.core.files.uploadedfile import SimpleUploadedFile



User = get_user_model()


# ============================================================
# OPTION A — PURE MESSAGING UNIT TESTS (NO ADVERT DEPENDENCY)
# ============================================================

class MessageModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username="sender", email="sender@test.com", password="pass1234"
        )
        self.receiver = User.objects.create_user(
            username="receiver", email="receiver@test.com", password="pass1234"
        )

        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, is this still available?",
            advert=None,  # ✅ explicitly no advert
        )

    def test_message_creation(self):
        self.assertEqual(self.message.sender, self.sender)
        self.assertEqual(self.message.receiver, self.receiver)
        self.assertFalse(self.message.is_read)

    def test_message_str(self):
        value = str(self.message)
        self.assertIn("sender", value)
        self.assertIn("receiver", value)

    def test_message_absolute_url(self):
        self.assertEqual(
            self.message.get_absolute_url(),
            f"/messages/conversation/{self.sender.id}/"
        )


class ConversationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="u1@test.com", password="pass1234"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="u2@test.com", password="pass1234"
        )

        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def test_conversation_participants(self):
        self.assertEqual(self.conversation.participants.count(), 2)

    def test_conversation_str(self):
        self.assertEqual(str(self.conversation), f"Conversation {self.conversation.id}")


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="notify", email="notify@test.com", password="pass1234"
        )

        self.message = Message.objects.create(
            sender=self.user,
            receiver=self.user,
            content="Notification source",
        )

    def test_notification_for_user(self):
        notification = Notification.objects.create(
            user=self.user,
            message="You have a new message",
        )
        self.assertFalse(notification.is_read)

    def test_broadcast_notification(self):
        notification = Notification.objects.create(
            user=None,
            message="System announcement",
        )
        self.assertIn("Broadcast", str(notification))

    def test_notification_with_content_object(self):
        content_type = ContentType.objects.get_for_model(Message)

        notification = Notification.objects.create(
            user=self.user,
            message="Linked notification",
            content_type=content_type,
            object_id=self.message.id,
        )

        self.assertEqual(
            notification.get_link(),
            self.message.get_absolute_url()
        )

    def test_notification_get_link_none(self):
        notification = Notification.objects.create(
            user=self.user,
            message="No link",
        )
        self.assertIsNone(notification.get_link())


# ============================================================
# OPTION B — INTEGRATION TEST (SHOP → ADVERT → MESSAGE)
# ============================================================

class MessageWithAdvertIntegrationTest(TestCase):
    def setUp(self):
        # Users
        self.seller = User.objects.create_user(
            username="seller", email="seller@test.com", password="pass1234"
        )
        self.buyer = User.objects.create_user(
            username="buyer", email="buyer@test.com", password="pass1234"
        )

        # Category (REQUIRED)
        self.category = Category.objects.create(
            name="Electronics"
        )

        # Shop (REQUIRED)
        self.shop = Shop.objects.create(
            seller=self.seller,
            shop_name="Seller Shop",
            description="Test shop",
        )

        # Fake image (REQUIRED for ImageField)
        self.image = SimpleUploadedFile(
            name="test.jpg",
            content=b"\x47\x49\x46\x38\x39\x61",  # minimal valid image header
            content_type="image/jpeg",
        )

        # Advert (ALL REQUIRED FIELDS SATISFIED)
        self.advert = Advert.objects.create(
            shop=self.shop,
            seller=self.seller,
            title="Test Advert",
            category=self.category,
            price=1000.00,
            image=self.image,
            description="Advert description",
        )

        # Message
        self.message = Message.objects.create(
            sender=self.buyer,
            receiver=self.seller,
            advert=self.advert,
            content="Is this still available?",
        )

    def test_message_links_to_advert(self):
        self.assertEqual(self.message.advert, self.advert)

    def test_advert_shop_relationship(self):
        self.assertEqual(self.advert.shop, self.shop)
        self.assertEqual(self.advert.seller, self.seller)
        self.assertEqual(self.advert.category, self.category)

    def test_message_flow(self):
        self.assertEqual(self.message.sender, self.buyer)
        self.assertEqual(self.message.receiver, self.seller)
