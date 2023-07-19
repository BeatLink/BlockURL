"use strict";

var contextMenu = {
  id: "block-selected-link",
  title: "Block This Link",
  contexts: ["link"],
}

// Initialize Plugin Storage ------------------------------------------------------------------------------------------
function initialize() {
    var settings = {
        "headingText": "Blocked",
        "bodyText":  "This page is blocked by BlockURL",
        "buttonText": "Unblock"
    }
    var urls = new Set()
    browser.storage.local.set({settings, urls})
}

// Opens the settings page --------------------------------------------------------------------------------------------
function openSettingsPage() {
    browser.tabs.create({url: "/options.html"});
}

// Toggle Blocking For Page -------------------------------------------------------------------------------------------
function toggleBlockedState(page){
    browser.storage.local.get("urls").then((items) => {
        var urls = items.urls
        if (urls.has(page.url)) {
            console.log("Removing from Blocklist: " + page.url)
            urls.delete(page.url);
        } else {
            console.log("Adding to Blocklist: " + page.url)
            urls.add(page.url)
        }
        browser.storage.local.set({urls})
        browser.tabs.reload()
    })
}

// Respond to unblock requests from content script ----------------------------------------------------------------------
function onMessage(message) {
    if ("unblockRequested" in message) {
        var page = {url: message.unblockRequested}
        toggleBlockedState(page)
    }
}

// Checks for block status when tab is updated ---------------------------------------------------------------------------
function onTabUpdated(tabID, changeInfo){
    browser.storage.local.get("urls").then((items) => {
        if (items.urls.has(changeInfo.url)) {
            browser.tabs.executeScript(tabID, {file: "blocked.js"})
        }
    })
}


function onContextMenuClicked(info, tab){
    var page = {url: info.linkUrl}
    toggleBlockedState(page)
}

browser.runtime.onInstalled.addListener(initialize)
browser.pageAction.onClicked.addListener(toggleBlockedState);
browser.runtime.onMessage.addListener(onMessage)
browser.tabs.onUpdated.addListener(onTabUpdated, {properties: ["url"]})
browser.browserAction.onClicked.addListener(openSettingsPage);
browser.menus.create(contextMenu)
browser.menus.onClicked.addListener(onContextMenuClicked)