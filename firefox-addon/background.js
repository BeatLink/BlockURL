"use strict";

import { queryURLs, blockURLs, unblockURLs, getSetting } from "/api.js"

var contextMenu = {
  id: "block-selected-link",
  title: "Block This Link",
  contexts: ["link"],
}

// Initialize Plugin Storage ------------------------------------------------------------------------------------------
async function initialize() {
    var settings = await browser.storage.sync.get("syncServerURL")
    if (!settings | !settings['syncServerURL']){
        browser.storage.sync.set({"syncServerURL": "http://127.0.0.1:8000"})
    }
}

// Opens the settings page --------------------------------------------------------------------------------------------
function openSettingsPage() {
    browser.tabs.create({url: "/options/options.html"});
}


// Toggle Blocking For Page -------------------------------------------------------------------------------------------
async function toggleBlockedState(page){
    var url = page.url
    var response = await queryURLs([url])
    if (response[url]) {
        console.log("Removing from Blocklist: " + url)
        await unblockURLs([url])
        browser.tabs.reload()
    } else {
        console.log("Adding to Blocklist: " + url)
        await blockURLs([url])
        browser.tabs.reload()
    }
}

// Respond to unblock requests from content script ----------------------------------------------------------------------
async function onMessage(message) {
    if ("unblockRequested" in message) {
        var urls = message.unblockRequested
        await unblockURLs(urls)
        browser.tabs.reload()
    }
    if ("queryURLs" in message) {
        var urls = message.queryURLs
        return await queryURLs(urls)
    }
    if ("getSetting" in message){
        var key = message.getSetting
        return await getSetting(key)
    }

}

// Blocks the page when the context menu is clicked -------------------------------------------------------------------
async function onContextMenuClicked(info, tab){
    console.log(`Blocking Link: ${url}`)
    var url = info.linkUrl
    await blockURLs([url])
    browser.tabs.reload()
}

browser.runtime.onInstalled.addListener(initialize)
//browser.pageAction.onClicked.addListener(toggleBlockedState);
browser.runtime.onMessage.addListener(onMessage)
browser.browserAction.onClicked.addListener(openSettingsPage);
browser.menus.create(contextMenu)
browser.menus.onClicked.addListener(onContextMenuClicked)