import unittest

class StartTemplate(unittest.TestCase):

    def test_action(self):
        self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")
