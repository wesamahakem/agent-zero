

import * as device from "./device.js";
import { callJsonApi } from "./api.js";
import { updateThoughtKeys } from "./messages.js";

export async function initialize(){
    // set device class to body tag
    setDeviceClass();
    loadSettings();
    document.addEventListener("settings-updated", (e) => {
        if(e.detail && e.detail.ui_thought_keys) {
            updateThoughtKeys(e.detail.ui_thought_keys);
        }
    });
}

async function loadSettings() {
    try {
        const response = await callJsonApi("/settings_get", {});
        if (response.settings && response.settings.ui_thought_keys) {
            updateThoughtKeys(response.settings.ui_thought_keys);
        }
    } catch (e) {
        console.error("Failed to load settings", e);
    }
}

function setDeviceClass(){
    device.determineInputType().then((type) => {
        // Remove any class starting with 'device-' from <body>
        const body = document.body;
        body.classList.forEach(cls => {
            if (cls.startsWith('device-')) {
                body.classList.remove(cls);
            }
        });
        // Add the new device class
        body.classList.add(`device-${type}`);
    });
}
