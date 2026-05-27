"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.fetchData = fetchData;
async function fetchData(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.text();
}
