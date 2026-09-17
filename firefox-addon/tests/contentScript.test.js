import { describe, it, expect, vi } from 'vitest'

// contentScript.js runs as soon as it is imported, so each test builds the page
// it should find, then imports the script fresh.
async function runContentScriptOn(html, blocked = {}) {
    const parsed = new DOMParser().parseFromString(html, 'text/html')
    document.body.replaceChildren(...parsed.body.childNodes)
    globalThis.browser.runtime.sendMessage.mockImplementation(async (message) => {
        if ("queryURLs" in message) {
            return Object.fromEntries(message.queryURLs.map((url) => [url, blocked[url] === true]))
        }
        return undefined
    })
    vi.resetModules()
    await import('../contentScript.js')
    await vi.waitFor(() => expect(globalThis.browser.runtime.sendMessage).toHaveBeenCalled())
    await new Promise((resolve) => setTimeout(resolve, 0))
}

function queriedURLs() {
    return globalThis.browser.runtime.sendMessage.mock.calls
        .filter(([message]) => "queryURLs" in message)
        .flatMap(([message]) => message.queryURLs)
}

describe('contentScript.js', () => {
    it('checks embedded media, not just links and images', async () => {
        await runContentScriptOn(`
            <a href="https://example.com/link"></a>
            <img src="https://example.com/image.png">
            <iframe src="https://redgifs.com/ifr/ablegoat"></iframe>
            <video src="https://media.redgifs.com/AbleGoat.mp4"></video>
            <video><source src="https://media.redgifs.com/OtherGoat.mp4"></video>
        `)
        expect(queriedURLs()).toEqual(expect.arrayContaining([
            'https://example.com/link',
            'https://example.com/image.png',
            'https://redgifs.com/ifr/ablegoat',
            'https://media.redgifs.com/AbleGoat.mp4',
            'https://media.redgifs.com/OtherGoat.mp4',
        ]))
    })

    it('hides a blocked embed', async () => {
        await runContentScriptOn(
            '<iframe src="https://redgifs.com/ifr/ablegoat"></iframe>',
            { 'https://redgifs.com/ifr/ablegoat': true },
        )
        expect(document.querySelector('iframe').style.display).toBe('none')
    })

    it('hides the player around a blocked source, since a source has no box of its own', async () => {
        await runContentScriptOn(
            '<video><source src="https://media.redgifs.com/AbleGoat.mp4"></video>',
            { 'https://media.redgifs.com/AbleGoat.mp4': true },
        )
        expect(document.querySelector('video').style.display).toBe('none')
        expect(document.querySelector('source').style.display).toBe('')
    })

    it('leaves an embed that is not blocked alone', async () => {
        await runContentScriptOn('<iframe src="https://redgifs.com/ifr/ablegoat"></iframe>')
        expect(document.querySelector('iframe').style.display).toBe('')
    })

    it('never asks the server about blob: or data: sources', async () => {
        await runContentScriptOn(`
            <video src="blob:https://reddit.com/1234"></video>
            <img src="data:image/gif;base64,R0lGOD">
        `)
        expect(queriedURLs()).not.toContain('blob:https://reddit.com/1234')
        expect(queriedURLs().some((url) => url.startsWith('data:'))).toBe(false)
    })
})
