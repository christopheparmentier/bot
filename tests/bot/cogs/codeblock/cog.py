import unittest
from unittest import mock

import discord

from bot.cogs import codeblock
from bot.cogs.codeblock import CodeBlockCog
from tests import helpers


class CodeBlockExtensionTests(unittest.TestCase):
    """Tests for the codeblock extension."""

    @mock.patch("bot.cogs.codeblock.CodeBlockCog", spec_set=True, autospec=True)
    def test_extension_setup(self, cog):
        """The TokenRemover cog should be added."""
        bot = helpers.MockBot()
        codeblock.setup(bot)

        cog.assert_called_once_with(bot)
        bot.add_cog.assert_called_once()
        self.assertTrue(isinstance(bot.add_cog.call_args.args[0], CodeBlockCog))


class CodeBlockCogTests(unittest.IsolatedAsyncioTestCase):
    """Tests for the CodeBlock cog."""

    def setUp(self):
        self.bot = helpers.MockBot()

    @mock.patch("bot.constants.CodeBlock.cooldown_channels", new=[1, 2])
    def test_init(self):
        """Bot should be saved as an attribute and channel cooldowns should be set to 0."""
        cog = CodeBlockCog(self.bot)
        self.assertEqual(cog.bot, self.bot)
        self.assertDictEqual(cog.channel_cooldowns, {1: 0.0, 2: 0.0})

    def test_create_embed(self):
        """Should create an embed with the instructions as the description."""
        description = "foo"
        embed = CodeBlockCog.create_embed(description)
        self.assertEqual(embed.description, description)

    async def test_get_sent_instructions(self):
        """Should return the message associated with the event payload or None if not found."""
        cog = CodeBlockCog(self.bot)
        payload = discord.RawMessageUpdateEvent({"id": "123", "channel_id": "456"})

        cog.codeblock_message_ids = {payload.message_id: 555}
        channel = self.bot.get_channel.return_value = helpers.MockTextChannel()
        channel.fetch_message.side_effect = [8000, discord.NotFound(mock.Mock(), mock.MagicMock())]

        for expected in (8000, None):
            self.bot.get_channel.reset_mock()
            channel.fetch_message.reset_mock()  # Seems to work without this but let's be safe.

            with self.subTest(expected=expected):
                actual = await cog.get_sent_instructions(payload)

                # Ideally, there would only be a simple assert for the returned message's ID.
                # However, this is not feasible because it relies on discord.py's code working,
                # which in turn relies on mocking Discord API calls.
                self.assertEqual(expected, actual)

                # The payload channel should be retrieved.
                self.bot.get_channel.assert_called_once_with(payload.channel_id)

                # The message associated with the payload message should be retrieved.
                channel.fetch_message.assert_awaited_once_with(555)

    @mock.patch("bot.cogs.codeblock.cog.time.time", return_value=500)
    def test_is_on_cooldown(self, _):
        """Should return True if the difference between current time and cooldown time is < 300."""
        cog = CodeBlockCog(self.bot)
        cog.channel_cooldowns = {1: 500, 2: 300, 3: 200, 4: 100}

        # 5 doesn't exist, so it should have a cooldown of 0.
        subtests = ((1, True), (2, True), (3, False), (4, False), (5, False))

        for channel_id, expected in subtests:
            with self.subTest(channel_id=channel_id, expected=expected):
                channel = helpers.MockTextChannel(id=channel_id)
                actual = cog.is_on_cooldown(channel)
                self.assertIs(expected, actual)
