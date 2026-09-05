// tests/e2e/a11y.spec.ts · web-lab fase 6
// axe por plantilla en claro y oscuro, sobre estados tras interactuar, más lo que axe no cubre.
import { test, expect, fingerprint } from './fixtures/axe'

// Una URL representativa por plantilla del sitemap
const templates: Record<string, string> = {
  home: '/',
  interior: '/sobre',
  listado: '/blog',
  detalle: '/blog/primer-articulo',
  formulario: '/contacto',
  legal: '/aviso-de-privacidad',
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

test('a11y · menú móvil abierto', async ({ page, makeAxeBuilder }) => {
  await page.setViewportSize({ width: 375, height: 812 })
  await page.goto('/')
  await page.getByRole('button', { name: /menú|menu/i }).click()
  const results = await makeAxeBuilder().include('header').analyze()
  expect(fingerprint(results)).toEqual([])
})

test('a11y · formulario con errores', async ({ page, makeAxeBuilder }) => {
  await page.goto('/contacto')
  await page.getByRole('button', { name: /enviar|pedir|solicitar/i }).click()
  await expect(page.getByRole('alert').first()).toBeVisible()
  const results = await makeAxeBuilder().analyze()
  expect(fingerprint(results)).toEqual([])
})

test('a11y · hover del botón primario mantiene contraste', async ({ page, makeAxeBuilder }) => {
  await page.goto('/')
  await page.getByRole('link', { name: /pedir|empezar|contactar/i }).first().hover()
  const results = await makeAxeBuilder().analyze()
  expect(fingerprint(results)).toEqual([])
})

// Lo que axe no puede evaluar

test('saltar al contenido es el primer foco y funciona', async ({ page }) => {
  await page.goto('/')
  await page.keyboard.press('Tab')
  const skip = page.getByRole('link', { name: /saltar|skip/i })
  await expect(skip).toBeFocused()
  await page.keyboard.press('Enter')
  const inMain = await page.evaluate(() => document.activeElement?.closest('main') !== null)
  expect(inMain).toBe(true)
})

test('modal atrapa el foco y cierra con Escape', async ({ page }) => {
  await page.goto('/')
  const opener = page.getByRole('button', { name: /abrir|ver más/i }).first()
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

test('sin enlaces con texto ambiguo', async ({ page }) => {
  await page.goto('/')
  const ambiguous = ['leer más', 'clic aquí', 'aquí', 'ver más', 'read more', 'click here', 'más']
  for (const link of await page.getByRole('link').all()) {
    const text = (await link.innerText()).trim().toLowerCase()
    const name = ((await link.getAttribute('aria-label')) ?? '').trim().toLowerCase()
    expect(ambiguous, `enlace ambiguo: "${text}"`).not.toContain(name || text)
  }
})

test('el conmutador de tema anuncia su estado actual', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'light' })
  await page.goto('/')
  const toggle = page.getByRole('button', { name: /modo|tema|theme/i })
  if (!(await toggle.isVisible())) test.skip()
  const before = await toggle.getAttribute('aria-label')
  await toggle.click()
  const after = await toggle.getAttribute('aria-label')
  expect(after).not.toEqual(before)
})
