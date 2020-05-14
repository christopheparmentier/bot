import unittest
from unittest import mock

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
