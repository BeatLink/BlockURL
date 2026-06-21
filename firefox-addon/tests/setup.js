// Minimal mock of the WebExtension `browser` API used across the addon's
// modules. Individual tests override specific methods as needed via
// `globalThis.browser.<namespace>.<method>.mockResolvedValue(...)`, etc.
import { vi, beforeEach } from 'vitest'

function buildBrowserMock() {
    return {
        storage: {
            sync: {
                get: vi.fn().mockResolvedValue({ syncServerURL: 'http://127.0.0.1:8000' }),
                set: vi.fn().mockResolvedValue(undefined),
            },
        },
        tabs: {
            create: vi.fn(),
            reload: vi.fn(),
        },
        runtime: {
            getURL: vi.fn((path) => `moz-extension://test-id/${path}`),
            sendMessage: vi.fn(),
            onMessage: { addListener: vi.fn() },
            onInstalled: { addListener: vi.fn() },
        },
        pageAction: { onClicked: { addListener: vi.fn() } },
        browserAction: { onClicked: { addListener: vi.fn() } },
        menus: { create: vi.fn(), onClicked: { addListener: vi.fn() } },
    }
}

beforeEach(() => {
    globalThis.browser = buildBrowserMock()
    globalThis.fetch = vi.fn()
})
