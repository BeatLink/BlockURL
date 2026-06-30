import { describe, it, expect, vi } from 'vitest'
import {
    removeTrailingSlashes,
    getSetting,
    getAllURLs,
    queryURLs,
    blockURLs,
    unblockURLs,
} from '../api.js'

function mockJsonResponse(body, ok = true, status = 200) {
    return {
        ok,
        status,
        json: vi.fn().mockResolvedValue(body),
    }
}

describe('removeTrailingSlashes', () => {
    it('strips a single trailing slash', () => {
        expect(removeTrailingSlashes(['https://example.com/'])).toEqual(['https://example.com'])
    })

    it('leaves URLs without a trailing slash untouched', () => {
        expect(removeTrailingSlashes(['https://example.com/page'])).toEqual([
            'https://example.com/page',
        ])
    })

    it('mutates and returns the same array', () => {
        const input = ['https://example.com/']
        const output = removeTrailingSlashes(input)
        expect(output).toBe(input)
    })
})

describe('getSetting', () => {
    it('POSTs to settings/get with the key and returns the value', async () => {
        globalThis.fetch.mockResolvedValue(mockJsonResponse('Blocked'))

        const result = await getSetting('blocked_page_heading_text')

        expect(result).toBe('Blocked')
        const [request] = globalThis.fetch.mock.calls[0]
        expect(request.url).toBe('http://127.0.0.1:8000/settings/get')
        expect(request.method).toBe('POST')
    })
})

describe('getAllURLs', () => {
    it('GETs urls/all', async () => {
        globalThis.fetch.mockResolvedValue(mockJsonResponse(['https://example.com/a']))

        const result = await getAllURLs()

        expect(result).toEqual(['https://example.com/a'])
        const [request] = globalThis.fetch.mock.calls[0]
        expect(request.url).toBe('http://127.0.0.1:8000/urls/all')
        expect(request.method).toBe('GET')
    })
})

describe('queryURLs', () => {
    it('normalizes trailing slashes before sending', async () => {
        globalThis.fetch.mockResolvedValue(mockJsonResponse({ 'https://example.com/a': true }))

        await queryURLs(['https://example.com/a/'])

        const [request] = globalThis.fetch.mock.calls[0]
        const body = JSON.parse(await request.clone().text())
        expect(body.urls).toEqual(['https://example.com/a'])
    })
})

describe('blockURLs / unblockURLs', () => {
    it('blockURLs posts to urls/block', async () => {
        globalThis.fetch.mockResolvedValue(mockJsonResponse(true))
        await blockURLs(['https://example.com/a'])
        const [request] = globalThis.fetch.mock.calls[0]
        expect(request.url).toBe('http://127.0.0.1:8000/urls/block')
    })

    it('unblockURLs posts to urls/unblock', async () => {
        globalThis.fetch.mockResolvedValue(mockJsonResponse(true))
        await unblockURLs(['https://example.com/a'])
        const [request] = globalThis.fetch.mock.calls[0]
        expect(request.url).toBe('http://127.0.0.1:8000/urls/unblock')
    })
})

describe('API key auth', () => {
    it('includes X-API-Key header when apiKey is configured', async () => {
        globalThis.browser.storage.sync.get.mockResolvedValue({
            syncServerURL: 'http://127.0.0.1:8000',
            apiKey: 'my-secret',
        })
        globalThis.fetch.mockResolvedValue(mockJsonResponse([]))

        await getAllURLs()

        const [request] = globalThis.fetch.mock.calls[0]
        expect(request.headers.get('X-API-Key')).toBe('my-secret')
    })

    it('omits X-API-Key header when apiKey is not set', async () => {
        globalThis.browser.storage.sync.get.mockResolvedValue({
            syncServerURL: 'http://127.0.0.1:8000',
        })
        globalThis.fetch.mockResolvedValue(mockJsonResponse([]))

        await getAllURLs()

        const [request] = globalThis.fetch.mock.calls[0]
        expect(request.headers.get('X-API-Key')).toBeNull()
    })
})

describe('error handling', () => {
    it('throws when syncServerURL is not configured', async () => {
        globalThis.browser.storage.sync.get.mockResolvedValue({})
        await expect(getAllURLs()).rejects.toThrow('syncServerURL is not configured')
    })

    it('throws when the server responds with a non-OK status', async () => {
        globalThis.fetch.mockResolvedValue(mockJsonResponse({}, false, 500))
        await expect(getAllURLs()).rejects.toThrow('Sync server error: 500')
    })

    it('strips trailing slash from a configured syncServerURL', async () => {
        globalThis.browser.storage.sync.get.mockResolvedValue({
            syncServerURL: 'http://127.0.0.1:8000/',
        })
        globalThis.fetch.mockResolvedValue(mockJsonResponse([]))

        await getAllURLs()

        const [request] = globalThis.fetch.mock.calls[0]
        expect(request.url).toBe('http://127.0.0.1:8000/urls/all')
    })
})
