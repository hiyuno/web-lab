# Discovery add-on · app site with feature forum

Twelve extra questions for `/discovery`, on top of the seven rounds in
`skills/discovery/references/interview.md`. Four short rounds. Ask them woven into the rounds
they extend, not as a separate interrogation: round A after round 1, round B after round 2,
round C after round 5, round D after round 6. At most four questions per turn; summarize and
confirm before moving on.

Each question says what it decides. If an answer does not decide anything downstream, do not ask
it.

If the user brings a filled `app-web-intake.md` from AppleAppLab (his app-development project),
treat every field in it as an answer already given: read it first and only ask the questions
below whose corresponding field is missing or still marked `TBD`. Do not re-ask what the file
already answers. The forum questions in Round C (7 and 8) are never in that file on purpose —
forum planning happens here, not in AppleAppLab — so always ask them live.

## Round A · The app and its platform

Extends round 1. Feeds: brief, architecture decision, hero brief.

1. **Which platforms does the app run on: iPhone, iPad, Mac, Vision, web?**
   Decides which App Store badges the hero carries, which screenshot sizes go in `assets.md`, and
   whether "Download on the App Store" or "Download for Mac" is the right label. A Mac app
   distributed outside the App Store gets a direct download plus a notarization note, not a badge.

2. **Is it already in the App Store? Give me the listing URL, since when, and its rating and
   install count if you have them.**
   Decides the primary CTA and the proof. No listing means no badge and no fake placeholder: the
   CTA becomes a waitlist or TestFlight. A listing with real numbers means the install count and
   rating are usable proof on the home.
   *Follow-up if there is a listing:* "What does the App Store description say today?" It is
   usually the closest thing to existing copy.

3. **Someone downloads the app right now. What happens in the first two minutes, and when do
   they get something useful out of it?**
   This is the time-to-first-value question and it decides the primary CTA wording. Instant value
   → "Download". Setup, an import or an account first → "Try it" or "Get started", with the setup
   named honestly on the page.
   *Warning:* an answer longer than three steps means the site has to sell the setup too, not
   hide it.

4. **If you could only show three things the app does, which three, and which one would you demo
   first?**
   Decides the feature showcase: three to six claim-plus-visual blocks, and which one gets the
   interactive demo or looping video. More than six pillars means the app has no positioning yet;
   push back before the site inherits the confusion.

## Round B · Money and proof

Extends round 2. Feeds: brief metrics, `/pricing`, key messages.

5. **Free, paid once, freemium or subscription? What are the tiers and prices, and is there a
   trial?**
   Decides whether `/pricing` exists as a page or collapses into a section on the home, and what
   the pricing pattern has to show. A single price with no tiers does not need a comparison table.

6. **Who already uses it that you can name? Reviews you can quote, people or companies, press,
   install count, anything with a source.**
   Decides the proof block. Named quotes, logos and real counts convert; "loved by thousands"
   does not and, per the `/content` rule, a claim without a source is not published. If there is
   nothing yet, the proof block is deferred, not faked.
   *Warning:* proof that exists only as a screenshot with no permission to quote it.

## Round C · Accounts, the forum and its moderation

Extends round 5. Feeds: threat model, architecture decision, `skills/build/references/forum.md`.

7. **Does the app already have accounts and sign-in? Which provider, and roughly how many
   people have one?**
   Decides the biggest build question in this project type: whether Hopper reuses the app's
   existing auth for forum sign-in — cheap, abuse-resistant, and the reason we build the forum
   instead of paying a SaaS tool — or provisions a minimal one. Votes are always authenticated;
   anonymous or fingerprinted voting is not on the table.

8. **Who moderates the forum, and how fast do they answer? What happens to spam, to something
   off-topic, and to the fifth copy of the same request?**
   Decides the moderation queue, the duplicate-merge flow and the status labels. Schneier treats
   an unnamed moderator on a public-write surface as a launch blocker, so a name and a response
   time are required, not aspirational.
   *Follow-up:* "Do you want comments on requests, or votes only?" Comments roughly double the
   moderation load and the personal-data surface.

9. **Where do release notes live today: App Store what's-new, a Notion page, commit messages,
   nowhere?**
   Decides how `/changelog` gets fed and whether it is a page Yuno writes or a feed generated
   from something that already exists. A changelog nobody updates is worse than no changelog:
   if there is no source and no habit, propose dropping the page.

## Round D · Data, support and domain

Extends round 6. Feeds: threat model, `/security`, `/docs`, `/launch`.

10. **What does the app itself collect about the people who use it, and where is it stored?**
    Feeds Schneier directly and is the raw material for the `/security` page, which this project
    type requires. Under the 2025 LFPDPPP (`skills/security/references/legal-mx.md`) this also
    sets what the privacy notice has to say. Note that the forum adds its own collection on top:
    names, avatars and whatever people paste into request titles and comments.

11. **Do docs or a support channel already exist somewhere: a help site, a Notion page, an email
    address, a Discord?**
    Decides whether `/docs` is a real section, a single page that links out, or just a support
    email in the footer. Do not build a docs section for an app whose documentation is four
    paragraphs.

12. **What domain does this app's site use, and do you own it already?**
    One site per app, so this is per-app, not shared. Decides what Allspaw sets up in phase 7 and
    whether a domain purchase is on the critical path. A subdomain of an existing domain is fine
    and is decided here, not on launch day.

## Warning signs across the add-on

- The app is described by its features and never by the problem it solves. The home will inherit
  that and will not convert; go back to round 1.
- Every feature is "the main one". Ask which single screen a new user should see in a
  screenshot.
- The forum is wanted because a competitor has one, with nobody to read it. A forum nobody
  answers is worse than an email address.
- Personal data mentioned in passing while talking about the forum. Stop and hand it to Schneier.
