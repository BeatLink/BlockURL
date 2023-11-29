"use strict";

var contextMenu = {
  id: "block-selected-link",
  title: "Block This Link",
  contexts: ["link"],
}


// API Functions ======================================================================================================
function queryURL(url, onDone){
    browser.storage.sync.get("syncServerURL").then((settings) => {
        url = url.endsWith('/') ? url.slice(0, -1) : url;
        const xhttp = new XMLHttpRequest();
        xhttp.onload = () => { onDone(xhttp) }
        xhttp.open("POST", `${settings["syncServerURL"]}/urls/check`, true);
        xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify({"url": url}));
    })
}

function blockURL(url, onDone) {
    browser.storage.sync.get("syncServerURL").then((settings) => {
        url = url.endsWith('/') ? url.slice(0, -1) : url;
        const xhttp = new XMLHttpRequest();
        xhttp.onload = () => { onDone(xhttp) }
        xhttp.open("POST", `${settings["syncServerURL"]}/urls/block`, true);
        xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify({"url": url}));
    })
}

function unblockURL(url, onDone){
    browser.storage.sync.get("syncServerURL").then((settings) => {
        url = url.endsWith('/') ? url.slice(0, -1) : url;
        const xhttp = new XMLHttpRequest();
        xhttp.onload = () => { onDone(xhttp) }
        xhttp.open("POST", `${settings["syncServerURL"]}/urls/unblock`, true);
        xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify({"url": url}));
    })
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
    queryURL(page.url, (xhttp) => {
        if (JSON.parse(xhttp.responseText)) {
            console.log("Removing from Blocklist: " + page.url)
            unblockURL(page.url, (xhttp) => {browser.tabs.reload()})
        } else {
            console.log("Adding to Blocklist: " + page.url)
            blockURL(page.url, (xhttp) => {browser.tabs.reload()})
        }
    })    
}

// Respond to unblock requests from content script ----------------------------------------------------------------------
function onMessage(message) {
    if ("unblockRequested" in message) {
        var page = {url: message.unblockRequested}
        toggleBlockedState(page)
    }
}

// Blocks the page when the context menu is clicked -------------------------------------------------------------------
function onContextMenuClicked(info, tab){
    var page = {url: info.linkUrl}
    toggleBlockedState(page)
}

browser.runtime.onInstalled.addListener(initialize)
browser.pageAction.onClicked.addListener(toggleBlockedState);
browser.runtime.onMessage.addListener(onMessage)
browser.browserAction.onClicked.addListener(openSettingsPage);
browser.menus.create(contextMenu)
browser.menus.onClicked.addListener(onContextMenuClicked)