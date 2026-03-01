#!/usr/bin/env node

/**
 * Context7 API Helper Script (Security-Hardened)
 *
 * Provides CLI interface to Context7 API for external dependency verification.
 * Based on: https://github.com/BenedictKing/context7-auto-research
 *
 * Security design (6-layer):
 *   Storage:  Key from env var ONLY (no local .env reading)
 *   Exec:     No Authorization header when key is absent (not even empty)
 *   Artifact: Output contains libraryId/version/snippets only; never headers/curl/tokens
 *   Prompt:   REDACT RULE enforced by callers
 *   Flow:     .env.example is reference only; real key via shell/CI
 *   Fallback: Works without key (lower rate limits)
 *
 * Usage:
 *   node context7_api.cjs search <libraryName> <query>
 *   node context7_api.cjs context <libraryId> <query>
 */

const https = require('https');

const API_BASE = 'https://context7.com/api/v2';

// Security: Key from environment variable ONLY — never read local .env files
const API_KEY = (process.env.CONTEXT7_API_KEY || '').trim() || null;

function makeRequest(urlPath, params = {}) {
  return new Promise((resolve, reject) => {
    const queryString = new URLSearchParams(params).toString();
    const url = `${API_BASE}${urlPath}?${queryString}`;

    const headers = { 'User-Agent': 'Context7-Skill/1.0' };
    // Security: only add Authorization when key is present and non-empty
    if (API_KEY) {
      headers['Authorization'] = `Bearer ${API_KEY}`;
    }

    https.get(url, { headers }, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        if (res.statusCode === 200) {
          try { resolve(JSON.parse(data)); }
          catch (_) { resolve(data); }
        } else {
          // Security: only print status code, never full response body or headers
          reject(new Error(`Context7 API ${res.statusCode}`));
        }
      });
    }).on('error', (err) => {
      // Security: redact any URL that might contain sensitive params
      reject(new Error(`Context7 network error`));
    });
  });
}

async function searchLibrary(libraryName, query) {
  try {
    return await makeRequest('/libs/search', { libraryName, query });
  } catch (error) {
    console.error(`Error searching library: ${error.message}`);
    return null;
  }
}

async function getContext(libraryId, query) {
  try {
    return await makeRequest('/context', { libraryId, query, type: 'json' });
  } catch (error) {
    console.error(`Error getting context: ${error.message}`);
    return null;
  }
}

// CLI Interface
const command = process.argv[2];
const args = process.argv.slice(3);

(async () => {
  if (command === 'search') {
    const [libraryName, query] = args;
    if (!libraryName || !query) {
      console.error('Usage: context7_api.cjs search <libraryName> <query>');
      process.exit(1);
    }
    const result = await searchLibrary(libraryName, query);
    if (result) console.log(JSON.stringify(result, null, 2));
  } else if (command === 'context') {
    const [libraryId, query] = args;
    if (!libraryId || !query) {
      console.error('Usage: context7_api.cjs context <libraryId> <query>');
      process.exit(1);
    }
    const result = await getContext(libraryId, query);
    if (result) console.log(JSON.stringify(result, null, 2));
  } else {
    console.error('Usage: context7_api.cjs <search|context> <args...>');
    process.exit(1);
  }
})();
