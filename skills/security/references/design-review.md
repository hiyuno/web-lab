# Design review · phases 2, 3 and 4

You read, you do not execute. Every finding costs minutes here and weeks in phase 5.

## Phase 2 · sitemap, flows, wireframes

- [ ] Every form field has a written reason in the wireframe; without a reason, it is removed
- [ ] No personal data travels in a URL or parameters (`?email=`, `/user/<email>`)
- [ ] Legal pages in the sitemap: privacy, terms if there is a sale or account, cookies if there are non-essential ones, 404
- [ ] If there are accounts: login, recovery, profile and deletion as their own pages
- [ ] User-content surfaces marked in `flows.md` (🔒) and in the sitemap
- [ ] Sensitive flows (payment, deletion, email or password change) with a confirmation step
- [ ] Admin panel out of the public sitemap; an unguessable path is not security; it must have auth

## Phase 3 · content, editorial guide, legal pages

- [ ] Generic login and recovery messages in the editorial guide
- [ ] Privacy notice with the minimum content from `legal-mx.md`, real controller data, date
- [ ] Short notice next to every form
- [ ] Consent banner in plain language, reject as visible as accept, nothing loads before
- [ ] No security promise the architecture does not keep ("military-grade encryption")
- [ ] Testimonials with permission; figures with a source
- [ ] Legal pages not copied from another site (search for other company names)

## Phase 4 · components, templates, prototype

- [ ] Login on its own page, consistent look, correct `autocomplete`, show password, no paste blocking, second factor visible
- [ ] Generic login error also in the error state design
- [ ] Destructive actions: `danger` variant, confirmation, separated from frequent actions
- [ ] Consent without dark patterns; account deletion as easy as signup
- [ ] Session state visible (who I am, sign out) on every authenticated screen
- [ ] Components that show user content marked for escaping in the component spec
- [ ] Uploads: the component shows allowed types and size
- [ ] No personal data in the prototype's screenshots or sample copy

## Verdict

With `verdict.md`. The most common here is "approved with conditions": the condition is a
concrete change in a wireframe or component before phase 5.
