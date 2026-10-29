"""CM mobile-menu source contract, including wrapped text and short viewports.

This checks normal-flow layout and semantic controls; it is not a browser render.
WIRING: collectionsmanager/index.html and pages/collectionsmanager.css.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def block_after(text, marker):
    """Read a balanced CSS block, allowing nested selectors inside @media."""
    start = text.index('{', text.index(marker))
    depth = 1
    for index in range(start + 1, len(text)):
        depth += (text[index] == '{') - (text[index] == '}')
        if not depth:
            return text[start + 1:index]
    raise AssertionError(f'Unclosed CSS block: {marker}')


def declarations(block, selector):
    body = block_after(block, selector + ' {')
    return dict(re.findall(r'([\w-]+)\s*:\s*([^;{}]+)\s*;', body))


class Navigation(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.stack = []
        self.menus = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.stack.append((tag, values))
        if tag == 'details' and 'cm-nav-menu' in values.get('class', '').split():
            self.menus.append({'attrs': values, 'summaries': 0, 'links': 0})
        if self.menus and any(item[0] == 'details' for item in self.stack):
            if tag == 'summary':
                self.menus[-1]['summaries'] += 1
            elif tag == 'a':
                self.menus[-1]['links'] += 1

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                self.stack = self.stack[:index]
                break


class CollectionsManagerMobileNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        css = (ROOT / 'site/assets/css/pages/collectionsmanager.css').read_text(encoding='utf-8')
        cls.mobile = block_after(css, '@media (max-width: 680px)')
        cls.home = (ROOT / 'site/collectionsmanager/index.html').read_text(encoding='utf-8')

    def test_wrapped_menu_panels_expand_in_normal_flow(self):
        """A taller nav must push its menu content, never overlap later controls."""
        panel = declarations(self.mobile, '.cm-home .cm-nav-menu > div')
        self.assertEqual(panel['position'], 'static')
        for edge in ['top', 'left', 'right']:
            self.assertEqual(panel[edge], 'auto')
        self.assertEqual(panel['width'], 'auto')
        opened = declarations(self.mobile, '.cm-home .cm-nav-menu[open]')
        self.assertEqual(opened['flex-basis'], '100%')
        summary = declarations(self.mobile, '.cm-home .cm-nav-menu summary')
        self.assertEqual(summary['white-space'], 'normal')

    def test_short_viewport_keeps_all_navigation_controls_scrollable(self):
        nav = declarations(self.mobile, '.guide.cm-home #nav')
        self.assertRegex(nav['max-height'], r'^100d?vh$')
        self.assertEqual(nav['overflow-y'], 'auto')
        panel = declarations(self.mobile, '.cm-home .cm-nav-menu > div')
        self.assertEqual(panel['max-height'], 'none')
        self.assertEqual(panel['overflow'], 'visible')

    def test_expanded_mobile_navigation_scrolls_away_from_fragment_destinations(self):
        """Open native details must not pin their height above a section target."""
        nav = declarations(self.mobile, '.guide.cm-home #nav')
        self.assertEqual(nav.get('position'), 'static')
        target = declarations(self.mobile, '.guide.cm-home section')
        self.assertEqual(target['scroll-margin-top'], '24px')
        self.assertIn('href="#workflow"', self.home)

    def test_native_summary_controls_and_exclusive_menu_group_remain(self):
        nav = Navigation(self.home)
        self.assertEqual(len(nav.menus), 3)
        for menu in nav.menus:
            self.assertEqual(menu['summaries'], 1)
            self.assertGreater(menu['links'], 0)
            self.assertEqual(menu['attrs']['name'], 'cm-navigation')
            self.assertNotIn('open', menu['attrs'])


if __name__ == '__main__':
    unittest.main()
