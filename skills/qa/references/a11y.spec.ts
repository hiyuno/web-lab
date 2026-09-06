// tests/e2e/a11y.spec.ts · web-lab phase 6
// axe per template in light and dark, on states after interacting, plus what axe does not cover.
// Button and link name patterns accept English and Spanish; adjust to the project's language.
import { test, expect, fingerprint } from './fixtures/axe'

// One representative URL per sitemap template
const templates: Record<string, string> = {
  home: '/',
  interior: '/about',
  listing: '/blog',
  detail: '/blog/first-post',
  form: '/contact',
  legal: '/privacy-notice',
}

for (const [name, path] of Object.entries(templates)) {
  for (const scheme of ['light', 'dark'] as const) {
    test(`a11y · ${name} · ${scheme}`, async ({ page, makeAxeBuilder }) => {
      await page.emulateMedia({ colorScheme: scheme })
      await page.goto(path)
      const results = await makeAxeBuilder().analyze()
      expect(fingerprint(results)).toEqual([])
    })
  }
}

test('a11y · open mobile menu', async ({ page, makeAxeBuilder }) => {
  await page.setViewportSize({ width: 375, height: 812 })
  await page.goto('/')
  await page.getByRole('button', { name: /menu|menú/i }).click()
  const results = await makeAxeBuilder().include('header').analyze()
  expect(fingerprint(results)).toEqual([])
})

test('a11y · form with errors', async ({ page, makeAxeBuilder }) => {
  await page.goto('/contact')
  await page.getByRole('button', { name: /send|submit|request|enviar|pedir|solicitar/i }).click()
  await expect(page.getByRole('alert').first()).toBeVisible()
  const results = await makeAxeBuilder().analyze()
  expect(fingerprint(results)).toEqual([])
})

test('a11y · primary button hover keeps contrast', async ({ page, makeAxeBuilder }) => {
  await page.goto('/')
  await page.getByRole('link', { name: /get started|request|contact|pedir|empezar|contactar/i }).first().hover()
  const results = await makeAxeBuilder().analyze()
  expect(fingerprint(results)).toEqual([])
})

// What axe cannot evaluate

test('skip to content is the first focus and works', async ({ page }) => {
  await page.goto('/')
  await page.keyboard.press('Tab')
  const skip = page.getByRole('link', { name: /skip|saltar/i })
  await expect(skip).toBeFocused()
  await page.keyboard.press('Enter')
  const inMain = await page.evaluate(() => document.activeElement?.closest('main') !== null)
  expect(inMain).toBe(true)
})

test('modal traps focus and closes with Escape', async ({ page }) => {
  await page.goto('/')
  const opener = page.getByRole('button', { name: /open|see more|abrir|ver más/i }).first()
  if (!(await opener.isVisible())) test.skip()
  await opener.click()
  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  for (let i = 0; i < 12; i++) {
    await page.keyboard.press('Tab')
    expect(await page.evaluate(() => document.activeElement?.closest('[role="dialog"]') !== null)).toBe(true)
  }
  await page.keyboard.press('Escape')
  await expect(dialog).toBeHidden()
  await expect(opener).toBeFocused()
})

test('no links with ambiguous text', async ({ page }) => {
  await page.goto('/')
  const ambiguous = ['read more', 'click here', 'here', 'see more', 'more', 'leer más', 'clic aquí', 'aquí', 'ver más', 'más']
  for (const link of await page.getByRole('link').all()) {
    const text = (await link.innerText()).trim().toLowerCase()
    const name = ((await link.getAttribute('aria-label')) ?? '').trim().toLowerCase()
    expect(ambiguous, `ambiguous link: "${text}"`).not.toContain(name || text)
  }
})

test('the theme toggle announces its current state', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'light' })
  await page.goto('/')
  const toggle = page.getByRole('button', { name: /mode|theme|modo|tema/i })
  if (!(await toggle.isVisible())) test.skip()
  const before = await toggle.getAttribute('aria-label')
  await toggle.click()
  const after = await toggle.getAttribute('aria-label')
  expect(after).not.toEqual(before)
})
