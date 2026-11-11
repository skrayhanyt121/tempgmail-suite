/**
 * TikTok Automated Action Engine (Playwright Headless Chrome)
 * Performs Follow and Avatar updates with authentic browser Wasm execution.
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const COOKIES_PATH = process.env.COOKIES_PATH || './tiktok_cookies.json';
const BROWSER_PATH = process.env.PLAYWRIGHT_BROWSERS_PATH || '/tmp/pw-browsers';

async function main() {
    const action = process.argv[2] || 'status';
    const target = process.argv[3] || '';

    if (!fs.existsSync(COOKIES_PATH)) {
        console.error('Cookies file not found at:', COOKIES_PATH);
        process.exit(1);
    }

    const rawCookies = JSON.parse(fs.readFileSync(COOKIES_PATH, 'utf8'));
    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled']
    });

    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport: { width: 1280, height: 800 }
    });

    // Format cookies for Playwright
    const formattedCookies = rawCookies.map(c => ({
        name: c.name,
        value: c.value,
        domain: c.domain.startsWith('.') ? c.domain : '.' + c.domain,
        path: c.path || '/',
        secure: c.secure !== undefined ? c.secure : true,
        httpOnly: c.httpOnly !== undefined ? c.httpOnly : false
    }));

    await context.addCookies(formattedCookies);
    const page = await context.newPage();

    if (action === 'follow') {
        const url = target.startsWith('http') ? target : `https://www.tiktok.com/@${target.replace('@', '')}`;
        console.log(`[+] Navigating to ${url}...`);
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(4000);

        console.log('[+] Looking for Follow button...');
        // TikTok follow button selectors
        const followBtn = await page.$('button[data-e2e="follow-button"], button:has-text("Follow"), button:has-text("Subscribe")');
        if (followBtn) {
            const btnText = await followBtn.innerText();
            console.log(`[+] Button found: "${btnText}"`);
            if (btnText.trim().toLowerCase() === 'follow') {
                await followBtn.click();
                await page.waitForTimeout(3000);
                console.log('[+] Successfully clicked Follow!');
            } else {
                console.log(`[*] Already following or button state is: ${btnText}`);
            }
        } else {
            console.log('[-] Follow button not found on page.');
        }

        await page.screenshot({ path: '/tmp/follow_result.png' });
        console.log('[+] Screenshot saved to /tmp/follow_result.png');

    } else if (action === 'avatar') {
        console.log('[+] Navigating to TikTok profile...');
        await page.goto('https://www.tiktok.com/@kemonaso24', { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(4000);

        // Check for Edit Profile
        const editBtn = await page.$('button:has-text("Edit profile"), a:has-text("Edit profile")');
        if (editBtn) {
            console.log('[+] Clicking Edit Profile...');
            await editBtn.click();
            await page.waitForTimeout(2000);

            // Upload image
            const imgPath = target || '/tmp/random_avatar.png';
            const fileInput = await page.$('input[type="file"]');
            if (fileInput) {
                console.log(`[+] Uploading avatar from ${imgPath}...`);
                await fileInput.setInputFiles(imgPath);
                await page.waitForTimeout(3000);

                const saveBtn = await page.$('button:has-text("Save"), button:has-text("Apply")');
                if (saveBtn) {
                    await saveBtn.click();
                    await page.waitForTimeout(5000);
                    console.log('[+] Avatar saved successfully!');
                }
            } else {
                console.log('[-] File input not found.');
            }
        } else {
            console.log('[-] Edit profile button not found.');
        }

        await page.screenshot({ path: '/tmp/avatar_result.png' });
        console.log('[+] Screenshot saved to /tmp/avatar_result.png');
    }

    await browser.close();
}

main().catch(err => {
    console.error('Fatal Error:', err);
    process.exit(1);
});
