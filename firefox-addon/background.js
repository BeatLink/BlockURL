"use strict";

import { queryURLs, blockURLs, unblockURLs } from "/api.js"

var contextMenu = {
  id: "block-selected-link",
  title: "Block This Link",
  contexts: ["link"],
}

// Initialize Plugin Storage ------------------------------------------------------------------------------------------
function initialize() {
    browser.storage.sync.get("syncServerURL").then((settings) => {
        if (!settings | !settings['syncServerURL']){
            browser.storage.sync.set({"syncServerURL": "http://127.0.0.1:8000"})
        }
    })
}

// Opens the settings page --------------------------------------------------------------------------------------------
function openSettingsPage() {
    browser.tabs.create({url: "/options.html"});
}


// Toggle Blocking For Page -------------------------------------------------------------------------------------------
function toggleBlockedState(page){
    var url = page.url
    url = url.endsWith('/') ? url.slice(0, -1) : url;
    queryURLs([url], (xhttp) => {
        var response = JSON.parse(xhttp.responseText)
        if (response[url]) {
            console.log("Removing from Blocklist: " + url)
            unblockURLs([url], (xhttp) => {browser.tabs.reload()})
        } else {
            console.log("Adding to Blocklist: " + url)
            blockURLs([url], (xhttp) => {browser.tabs.reload()})
        }
    })    
}

// Respond to unblock requests from content script ----------------------------------------------------------------------
function onMessage(message) {
    if ("unblockRequested" in message) {
        var url = message.unblockRequested
        url = url.endsWith('/') ? url.slice(0, -1) : url;
        unblockURLs([url], (xhttp) => {browser.tabs.reload()})
    }
}

// Blocks the page when the context menu is clicked -------------------------------------------------------------------
function onContextMenuClicked(info, tab){
    var url = info.linkUrl
    url = url.endsWith('/') ? url.slice(0, -1) : url;
    console.log(`Blocking Link: ${url}`)
    blockURLs([url], (xhttp) => {browser.tabs.reload()})
}

browser.runtime.onInstalled.addListener(initialize)
browser.pageAction.onClicked.addListener(toggleBlockedState);
browser.runtime.onMessage.addListener(onMessage)
browser.browserAction.onClicked.addListener(openSettingsPage);
browser.menus.create(contextMenu)
browser.menus.onClicked.addListener(onContextMenuClicked)