import { describe, it, expect, vi, beforeEach } from 'vitest'

// background.js imports from api.js and registers listeners at module load
// time, so we mock api.js and re-import background.js fresh for each test.
vi.mock('../api.js', () => ({
    queryURLs: vi.fn(),
    blockURLs: vi.fn(),
    unblockURLs: vi.fn(),
    getSetting: vi.fn(),
    removeTrailingSlashes: (urls) => urls,
}))

describe('background.js', () => {
    let api
    let onMessageHandler
    let onContextMenuHandler

    beforeEach(async () => {
        vi.resetModules()
        api = await import('../api.js')

        await import('../background.js')

        onMessageHandler = globalThis.browser.runtime.onMessage.addListener.mock.calls[0][0]
        onContextMenuHandler = globalThis.browser.menus.onClicked.addListener.mock.calls[0][0]
    })

    it('registers the "Block This Link" context menu item', () => {
        expect(globalThis.browser.menus.create).toHaveBeenCalledWith(
            expect.objectContaining({ id: 'block-selected-link', contexts: ['link'] }),
        )
    })

    it('unblockRequested message normalizes URL and reloads the sender tab', async () => {
        api.unblockURLs.mockResolvedValue(true)
        const sender = { tab: { id: 42 } }

        await onMessageHandler({ unblockRequested: ['https://example.com/'] }, sender)

        expect(api.unblockURLs).toHaveBeenCalledWith(['https://example.com'])
        expect(globalThis.browser.tabs.reload).toHaveBeenCalledWith(42)
    })

    it('queryURLs message normalizes URLs and returns the api response', async () => {
        api.queryURLs.mockResolvedValue({ 'https://example.com': true })

        const result = await onMessageHandler({ queryURLs: ['https://example.com/'] }, {})

        expect(api.queryURLs).toHaveBeenCalledWith(['https://example.com'])
        expect(result).toEqual({ 'https://example.com': true })
    })

    it('getSetting message delegates to api.getSetting', async () => {
        api.getSetting.mockResolvedValue('Blocked')

        const result = await onMessageHandler({ getSetting: 'blocked_page_heading_text' }, {})

        expect(api.getSetting).toHaveBeenCalledWith('blocked_page_heading_text')
        expect(result).toBe('Blocked')
    })

    it('context menu click blocks the linked URL and reloads the tab', async () => {
        api.blockURLs.mockResolvedValue(true)

        await onContextMenuHandler({ linkUrl: 'https://example.com/page/' }, { id: 7 })

        expect(api.blockURLs).toHaveBeenCalledWith(['https://example.com/page'])
        expect(globalThis.browser.tabs.reload).toHaveBeenCalledWith(7)
    })
})