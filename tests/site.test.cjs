// Exercise actual shared page utilities without installing a browser framework.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../site/assets/js/site.js'), 'utf8');

function environment(options = {}) {
    function panel(open = false) {
        const values = new Set(open ? ['show'] : []);
        return { classList: { contains: x => values.has(x), add: x => values.add(x), remove: x => values.delete(x) } };
    }
    const first = panel(true), second = panel(false);
    const button = { tagName: 'BUTTON', textContent: 'Copy' };
    const field = { value: 'https://supertron42.github.io/wiki/', nextElementSibling: button, select() { this.selected = true; } };
    const elements = { first, second, field };
    const doc = { getElementById: id => elements[id], querySelectorAll: () => [first, second], execCommand: () => options.fallbackSuccess !== false };
    const window = { isSecureContext: !!options.clipboard, navigator: { clipboard: options.clipboard }, setTimeout() {} };
    vm.runInNewContext(source, { window, document: doc });
    return { window, first, second, field, button };
}

test('opening a spoiler closes the old panel and toggling again closes it', () => {
    const e = environment();
    e.window.toggleSpoiler('second');
    assert.equal(e.first.classList.contains('show'), false);
    assert.equal(e.second.classList.contains('show'), true);
    e.window.toggleSpoiler('second');
    assert.equal(e.second.classList.contains('show'), false);
    assert.doesNotThrow(() => e.window.toggleSpoiler('missing'));
});

test('secure clipboard copies the real field value and reports success', async () => {
    let value;
    const e = environment({ clipboard: { async writeText(text) { value = text; } } });
    assert.equal(await e.window.copyText('field'), true);
    assert.equal(value, e.field.value);
    assert.equal(e.button.textContent, 'Copied!');
});

test('clipboard refusal falls back to selection; copyLink remains compatible', async () => {
    const e = environment({ clipboard: { async writeText() { throw Error('denied'); } } });
    assert.equal(await e.window.copyLink('field'), true);
    assert.equal(e.field.selected, true);
});

test('failed copying never falsely labels the button as copied', async () => {
    const e = environment({ fallbackSuccess: false });
    assert.equal(await e.window.copyText('field'), false);
    assert.equal(e.button.textContent, 'Copy');
    assert.equal(await e.window.copyText('missing'), false);
});
