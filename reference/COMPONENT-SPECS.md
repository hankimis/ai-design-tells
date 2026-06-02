# Component specs from real top-tier sites

What 199 human-crafted, design-led sites actually ship, read straight off their live computed styles (light and dark). Use these as concrete targets, not vibes. Every number below is measured, not asserted.

> Method: headless Chrome renders each site, waits for CSS and webfonts, then reads computed styles per component, once under `prefers-color-scheme: light` and once under `dark`. Source: `src/scrape_detail.py`, aggregated by `scripts/build_spec_catalog.py`. Corpus: 199 sites.

## Buttons

| Role | Radius (non-pill median / range) | Pill % | Padding y x | Font size | Font weight | Has shadow | Uppercase |
|---|---|---|---|---|---|---|---|
| **primary** (164) | 8.0px / 0.0–32.0px | 24% | 7.9px 15.3px | 15.0px | 500.0 | 13% | 7% |
| **secondary** (79) | 6.0px / 0.0–16.0px | 28% | 8.0px 16.0px | 14.4px | 500 | 8% | 8% |
| **ghost** (182) | 0.0px / 0.0–10.0px | 12% | 0.0px 1.5px | 16.0px | 400.0 | 6% | 6% |

Primary-button radius shape: `pill` (39), `small (1-6)` (37), `medium (8-12)` (35), `large (14+)` (27), `sharp (0)` (17). So the field splits between a soft-rounded look (8-12px) and a full pill; sharp 0px corners are a deliberate minority. Font weight clusters at `400` (70), `500` (46), `600` (29), `700` (13), `300` (2), `660` (1) (note 400 is common, a heavy button label is not required).

Real primary buttons (bg / text / radius / padding):

- **about.gitlab.com**: `#ffffff` on `#171321`, radius `4px`, padding `11px 16px 11px 16px`, weight `660`
- **airtable.com**: `#181d26` on `#ffffff`, radius `12px`, padding `16px 24px 16px 24px`, weight `500`
- **arc.net**: `#ffffff` on `#2702c2`, radius `10px`, padding `8px 0px 8px 0px`, weight `600`
- **asana.com**: `#0d0d0d` on `#ffffff`, radius `100px`, padding `0px 16px 0px 16px`, weight `500`
- **astro.build**: `#61dafb` on `#030712`, radius `8px`, padding `8px 16px 8px 16px`, weight `400`
- **bun.sh**: `#282a35` on `#ffffff`, radius `9999px`, padding `12px 18px 12px 18px`, weight `500`
- **calendly.com**: `#006bff` on `#ffffff`, radius `8px`, padding `10px 16px 10px 16px`, weight `600`
- **carta.com**: `#1a1a1a` on `#ffffff`, radius `8px`, padding `8px 16px 10px 16px`, weight `500`

## Typography

| Element | Size (median / range) | Weight | Line-height ratio | Negative tracking |
|---|---|---|---|---|
| **h1** (163) | 64.0px / 28.8–94.0px | 500 | 1.1 (0.98–1.33) | 54% |
| **h2** (169) | 48.0px / 21.0–80.0px | 500 | 1.1 (1–1.33) | 46% |
| **h3** (143) | 32.0px / 16.0–48.0px | 500 | 1.2 (1–1.5) | 37% |
| **h4** (59) | 23.0px / 16.0–32.0px | 500 | 1.2 (1–1.6) | 34% |
| **body** (187) | 16.0px / 14.0–20.0px | 400 | 1.5 (1.2–1.63) | 13% |

Most common h1 typefaces: `inter` (13), `geist` (3), `poppins` (3), `system-ui` (2), `mona sans` (2), `inter variable` (2), `aeonik` (2), `neue montreal` (2).

Body text size clusters at `16px` (67), `14px` (41), `18px` (18), `15px` (13), `20px` (11), `13px` (7). Line-height ratio centers on 1.5.

## Layout

- **Content container max-width:** median `1200.0px`; common values `1440px` (33), `1280px` (27), `1200px` (15), `1600px` (12), `1920px` (10), `640px` (7).
- **Section vertical rhythm (padding-top):** median `64.0px`; common `64px` (44), `80px` (43), `48px` (41), `32px` (41), `24px` (35), `96px` (24), `40px` (24), `120px` (18).
- **Grid columns:** `1` (92), `2` (85), `3` (56), `12` (31), `4` (28), `6` (8), `5` (7), `16` (4).
- **Gaps:** `8px` (156), `16px` (145), `12px` (126), `4px` (123), `24px` (121), `32px` (95), `6px` (61), `10px` (59), `20px` (58), `40px` (52).

## Spacing scale

Padding values are 47% multiples of 8 and 70% multiples of 4. The 4/8 px grid is real, but note it is not absolute, designers break it deliberately.

- **Padding scale (most used):** `16px` (181), `8px` (178), `24px` (167), `12px` (164), `4px` (142), `32px` (136), `10px` (126), `20px` (125), `6px` (108), `40px` (95), `48px` (86), `2px` (79), `64px` (61), `1px` (55).
- **Margin scale (most used):** `16px` (153), `8px` (142), `24px` (123), `32px` (113), `12px` (112), `20px` (93), `4px` (91), `48px` (84), `40px` (78), `10px` (64), `2px` (52), `64px` (51), `6px` (42), `80px` (35).

## Color, light mode

- **Page background:** `#ffffff` (84), `#000000` (12), `#121212` (3), `#fafafa` (2), `#f7f7f7` (2), `#f7f6f5` (2), `#f6f4ee` (1), `#ebeaec` (1).
- **Primary text:** `#000000` (65), `#ffffff` (29), `#212121` (4), `#333333` (3), `#0d0d0d` (3), `#1a1a1a` (3), `#121212` (3), `#1b1b1b` (3).
- **Accent (primary action) colors:** `#7c3aed` (2), `#1868db` (2), `#171321` (1), `#fcab79` (1), `#2702c2` (1), `#222875` (1), `#0c0f19` (1), `#f472b6` (1), `#006bff` (1), `#6c47ff` (1), `#edf6fd` (1), `#eaff96` (1).

Note the accent spread: there is no single "correct" brand color. The tell is never the hue itself, it is reaching for the framework-default indigo with nothing else decided.

## Color, dark mode

30 of 199 sites repaint automatically when the OS asks for dark (`prefers-color-scheme: dark`). The rest either ship light-only, are dark by default, or gate dark behind a manual in-page toggle this scrape did not click, so treat 30 as a floor, not the share of sites that support dark at all.

- **Dark page background:** `#000000` (3), `#111111` (2), `#18181b` (1), `#14120b` (1), `#0b0f19` (1), `#07060d` (1), `#1d1f27` (1), `#101010` (1), `#23272f` (1), `#0d0d0d` (1).
- **Dark primary text:** `#ffffff` (10), `#fafafa` (2), `#eeeeee` (2), `#edecec` (1), `#e1e1e1` (1), `#eaecf6` (1), `#e3e2e9` (1), `#f6f7f9` (1).
- **Dark surface (raised panel):** `#ffffff` (3), `#1f1f1f` (2), `#26272b` (1), `#1b1913` (1), `#fafafa` (1), `#670de5` (1), `#25262b` (1), `#ac7ef4` (1).

Dark backgrounds are almost never pure `#000000`; the norm is a near-black with a faint cool or warm tint, and surfaces are a step lighter, not a border away. Pure black on pure white text is itself a tell.

## Appendix: per-site primary button + headline

| Site | Primary btn bg | Radius | h1 size | h1 weight | Dark mode |
|---|---|---|---|---|---|
| a16z.com | `-` | - | - | - | no |
| about.gitlab.com | `#ffffff` | 4px | 96px | 660 | no |
| activetheory.net | `-` | - | - | - | no |
| airtable.com | `#181d26` | 12px | 40px | 400 | no |
| arc.net | `#ffffff` | 10px | 45.51px | 700 | no |
| asana.com | `#0d0d0d` | 100px | 64px | 300 | no |
| astro.build | `#61dafb` | 8px | 48px | 700 | no |
| basement.studio | `-` | - | 87px | 600 | no |
| bear.app | `-` | - | 51.2px | 400 | no |
| bere.al | `-` | - | - | - | no |
| bun.sh | `#282a35` | 9999px | 53.3333px | 800 | no |
| calendly.com | `#006bff` | 8px | 68px | 700 | no |
| carta.com | `#1a1a1a` | 8px | 84px | 400 | no |
| character.ai | `#202024` | 30px | 36px | 600 | yes |
| clerk.com | `#ffffff` | 6px | 64px | 700 | no |
| clickup.com | `#f0f0f0` | 8px | 52px | 700 | no |
| coda.io | `#ffffff` | 8px | 72px | 700 | no |
| codesandbox.io | `#eaff96` | 4px | 120px | 500 | no |
| cohere.com | `#17171c` | 9999px | 96px | 400 | no |
| cursor.com | `#26251e` | 3.35544e+07px | 26px | 400 | yes |
| deno.com | `#66c2ff` | 8px | 72px | 700 | no |
| discord.com | `#ffffff` | 16px | 56px | 700 | no |
| elevenlabs.io | `#f5f3f1` | 9999px | 48px | 300 | no |
| ethereum.org | `#6c24e0` | 8px | 64px | 900 | no |
| every.to | `#ffffff` | 9999px | 52px | 400 | no |
| family.co | `#f6f4ef` | 32px | 68px | 500 | no |
| fly.io | `#7c3aed` | 8px | 64px | 500 | no |
| ghost.org | `#15171a` | 6px | 96px | 700 | no |
| github.com | `#08872b` | 6px | 64px | 425 | no |
| godly.website | `#000000` | 3.35544e+07px | 20px | 500 | no |
| grafana.com | `#ffffff` | 6px | 60px | 600 | no |
| greylock.com | `#6db3c4` | 2.4px | 80px | 400 | no |
| gusto.com | `#0a8080` | 8px | 56px | 600 | no |
| huggingface.co | `#ffffff` | 3.35544e+07px | 48px | 700 | yes |
| igloo.inc | `-` | - | - | - | no |
| linear.app | `-` | - | 64px | 510 | no |
| locomotive.ca | `#ffffff` | 0px | 70px | 400 | no |
| lusion.co | `#2b2e3a` | 87.5px | 36px | 400 | no |
| mailchimp.com | `#ffe01b` | 26px | 48px | 400 | no |
| make.com | `#ff009a` | 10px | 48px | 700 | no |
| mercury.com | `#5266eb` | 32px | 49.3472px | 480 | no |
| metamask.io | `#ffffff` | 50% | 160px | 400 | no |
| miro.com | `#ffffff` | 50% | 56px | 500 | no |
| monday.com | `#6161ff` | 40px | 36px | 400 | no |
| monzo.com | `#091723` | 500px | - | - | no |
| n26.com | `#088177` | 6px | 80px | 400 | no |
| neon.tech | `#e4f1eb` | 0px | 68px | 400 | no |
| nuxt.com | `#ffffff` | 3.35544e+07px | 72px | 700 | no |
| obsidian.md | `#7c3aed` | 8px | 60px | 600 | no |
| offset.com | `-` | - | - | - | no |
| openai.com | `#000000` | 40px | - | - | yes |
| opensea.io | `#ffffff` | 6px | - | - | no |
| paulgraham.com | `-` | - | - | - | no |
| pentagram.com | `#ffffff` | 9999px | 19px | 500 | no |
| phantom.app | `#fdfcfe` | 32px | 80px | 400 | no |
| pitch.com | `#ebe3fe` | 100px | 180px | 700 | no |
| plaid.com | `#ffffff` | 999px | 76px | 500 | no |
| planetscale.com | `#f35815` | 0px | 16px | 700 | yes |
| polygon.technology | `#670de5` | 3px | - | - | yes |
| posthog.com | `#cd8407` | 6px | 24px | 800 | yes |
| qwik.dev | `#ebedf0` | 40px | - | - | yes |
| railway.app | `#13111c` | 50% | 54px | 500 | no |
| rainbow.me | `-` | - | 96px | 400 | no |
| ramp.com | `-` | - | 64px | 400 | no |
| react.dev | `#ebecef` | 9999px | 52px | 600 | yes |
| readwise.io | `#478cd0` | 10px | 50px | 600 | no |
| redis.io | `#351d22` | 200px | 100px | 400 | no |
| remix.run | `#ffffff` | 999px | 84px | 700 | no |
| render.com | `#0d0d0d` | 0px | 80px | 300 | yes |
| replicate.com | `#000000` | 0px | 24px | 400 | yes |
| replit.com | `#f6f5f4` | 6px | 68.92px | 400 | no |
| resend.com | `#d6ebfd` | 16px | 96px | 400 | no |
| robinhood.com | `-` | - | 72px | 400 | no |
| runwayml.com | `-` | - | 48px | 400 | no |
| sentry.io | `#ffffff` | 12px | 88px | 700 | no |
| signal.org | `#ffffff` | 8px | 60px | 800 | no |
| slack.com | `#611f69` | 4px | 64px | 400 | no |
| squareup.com | `-` | - | 64px | 400 | no |
| stackblitz.com | `-` | - | 94px | 600 | no |
| strapi.io | `-` | - | 53px | 700 | no |
| stripe.com | `#533afd` | 4px | 48px | 300 | no |
| stripe.press | `#0d121f` | 0px | 17.6px | 600 | no |
| substack.com | `#ffffff` | 12px | - | - | yes |
| suno.com | `#f7f4ef` | 3.35544e+07px | 72px | 500 | no |
| supabase.com | `#fdfdfd` | 6px | 72px | 400 | yes |
| svelte.dev | `-` | - | 54px | 500 | yes |
| tailwindcss.com | `-` | - | 96px | 400 | no |
| telegram.org | `-` | - | - | - | no |
| temporal.io | `-` | - | 68px | 300 | no |
| todoist.com | `#e34432` | 8px | 55px | 600 | no |
| ui.shadcn.com | `-` | - | 48px | 600 | no |
| uniswap.org | `#ff37c7` | 12px | 64px | 485 | yes |
| unseen.co | `-` | - | 28.8px | 700 | no |
| upstash.com | `#ffffff` | 16px | 128px | 700 | yes |
| vercel.com | `#ffffff` | 6px | 48px | 600 | yes |
| vuejs.org | `#f1f1f1` | 11px | 76px | 900 | yes |
| waitbutwhy.com | `-` | - | 32px | 500 | yes |
| weaviate.io | `#130c49` | 5px | 72px | 400 | no |
| webflow.com | `#146ef5` | 4px | 80px | 600 | yes |
| wise.com | `#9fe870` | 9999px | 105.428px | 900 | no |
| www.adyen.com | `#00112c` | 2px | 32px | 484 | no |
| www.aesop.com | `#000000` | 0px | 30px | 400 | no |
| www.airbnb.com | `#f2f2f2` | 50% | - | - | no |
| www.allbirds.com | `#212121` | 3.35544e+07px | 24px | 400 | no |
| www.anthropic.com | `-` | - | 60.8653px | 700 | no |
| www.apple.com | `#161617` | 11px | - | - | no |
| www.atlassian.com | `#101214` | 100% | 84px | 600 | no |
| www.awwwards.com | `#222222` | 8px | - | - | no |
| www.behance.net | `#f5f8ff` | 100px | 80px | 600 | no |
| www.bloomberg.com | `#000000` | 0px | - | - | no |
| www.brex.com | `#ff5900` | 8px | 72px | 500 | no |
| www.calm.com | `#ffffff` | 100px | 49.5px | 700 | no |
| www.canva.com | `#ffffff` | 16px | 24px | 600 | no |
| www.checkout.com | `#186aff` | 6px | 80px | 700 | no |
| www.cloudflare.com | `#ff5e1f` | 8px | 56px | 500 | yes |
| www.cockroachlabs.com | `#000000` | 9999px | 50px | 400 | no |
| www.cognition.ai | `#191919` | 0px | 36px | 400 | no |
| www.coinbase.com | `#eef0f3` | 0px | 80px | 400 | no |
| www.contentful.com | `#3c80cf` | 42px | 72px | 600 | no |
| www.craft.do | `#030302` | 24px | 66px | 400 | no |
| www.cuberto.com | `-` | - | 81px | 500 | no |
| www.datadoghq.com | `#ffffff` | 4px | 52px | 300 | no |
| www.deel.com | `-` | - | 60px | 500 | no |
| www.descript.com | `#390a1a` | 9999px | 18px | 400 | no |
| www.docker.com | `#ffffff` | 4px | 48px | 500 | no |
| www.doordash.com | `-` | - | 40px | 600 | yes |
| www.dribbble.com | `#ea4c89` | 2px | 48px | 600 | no |
| www.dropbox.com | `#0061fe` | 12px | 40px | 500 | no |
| www.dropbox.com_paper | `#0061fe` | 12px | 40px | 400 | no |
| www.duolingo.com | `-` | - | 64px | 700 | no |
| www.economist.com | `#efefef` | 0px | - | - | no |
| www.fastcompany.com | `#a3afff` | 3px | - | - | no |
| www.fey.com | `#ffffff` | 50% | 54px | 600 | no |
| www.figma.com | `#000000` | 50% | - | - | no |
| www.figma.com_community | `#ffffff` | 6px | 24px | 500 | no |
| www.firstround.com | `-` | - | 135px | 500 | no |
| www.framer.com | `#ffffff` | 40px | 110px | 500 | no |
| www.glossier.com | `#000000` | 0px | - | - | no |
| www.godaddy.com | `-` | - | 32px | 700 | no |
| www.hashicorp.com | `#ffffff` | 4px | 82px | 600 | no |
| www.headspace.com | `#ffffff` | 8px | - | - | no |
| www.hubspot.com | `#ffffff` | 8px | 65px | 500 | no |
| www.ideo.com | `#d9ff00` | 0px | 90px | 300 | no |
| www.instrument.com | `#ffffff` | 32px | - | - | no |
| www.intercom.com | `#000000` | 6px | 80px | 400 | no |
| www.klaviyo.com | `#ffffff` | 2px | 80px | 400 | no |
| www.land-book.com | `#ffffff` | 800px | 24.5px | 600 | no |
| www.langchain.com | `#e5f4ff` | 6px | 56px | 300 | no |
| www.lennysnewsletter.com | `#f47c55` | 8px | 24px | 700 | no |
| www.loom.com | `#1868db` | 9999px | 63.2692px | 700 | no |
| www.lyft.com | `#820076` | 48px | 60px | 600 | no |
| www.medium.com | `#191919` | 1386px | - | - | no |
| www.midjourney.com | `#0f1c36` | 9999px | 30px | 400 | yes |
| www.mintlify.com | `-` | - | 57.6px | 600 | no |
| www.mistral.ai | `#151524` | 32px | - | - | no |
| www.mongodb.com | `#00ed64` | 4px | 64px | 400 | no |
| www.netlify.com | `#32e6e2` | 4px | 64px | 800 | yes |
| www.nike.com | `#111111` | 30px | 16px | 500 | no |
| www.notion.so | `#455dd3` | 8px | 64px | 700 | no |
| www.nytimes.com | `#ffffff` | 0px | - | - | no |
| www.on.com | `#ffffff` | 40px | 39.232px | 700 | no |
| www.onepeloton.com | `#181a1d` | 28px | 48px | 600 | no |
| www.ouraring.com | `#f7f1e8` | 3.35544e+07px | 84px | 300 | no |
| www.patagonia.com | `#000000` | 0px | 64px | 500 | no |
| www.perplexity.ai | `#fdfbfa` | 8px | - | - | yes |
| www.pinecone.io | `#000000` | 50% | 44px | 700 | yes |
| www.postman.com | `#e0531f` | 5px | 55px | 600 | no |
| www.prisma.io | `#5a67d8` | 2px | 64px | 400 | yes |
| www.producthunt.com | `#ff6154` | 9999px | 24px | 600 | no |
| www.radix-ui.com | `#1c2024` | 8px | 78px | 400 | yes |
| www.raycast.com | `-` | - | 64px | 600 | no |
| www.reddit.com | `#0a449b` | 999px | - | - | yes |
| www.retool.com | `#e9ebdf` | 9999px | 72px | 300 | no |
| www.revolut.com | `#f4f4f4` | 9999px | 89.216px | 500 | no |
| www.rippling.com | `#ffa81d` | 4px | 48px | 500 | no |
| www.salesforce.com | `#0176d3` | 4px | 70px | 400 | no |
| www.sanity.io | `#ffffff` | 9999px | 112px | 400 | yes |
| www.sequoiacap.com | `#fbf7f0` | 990px | 52px | 400 | no |
| www.shopify.com | `#ffffff` | 9999px | - | - | no |
| www.solana.com | `#ffffff` | 9999px | 88px | 500 | no |
| www.solidjs.com | `#446b9e` | 6px | - | - | no |
| www.spotify.com | `#1f1f1f` | 50% | 16px | 700 | no |
| www.squarespace.com | `#ffffff` | 0px | 64px | 300 | no |
| www.sunsama.com | `#000000` | 3px | - | - | no |
| www.superhuman.com | `#d4c7ff` | 8px | 64px | 540 | no |
| www.tesla.com | `-` | - | 32px | 700 | no |
| www.theverge.com | `#3cffd0` | 24px | - | - | no |
| www.toss.im | `#000c1e` | 7px | 66px | 700 | no |
| www.twilio.com | `#1866ee` | 50px | 56px | 700 | no |
| www.typeform.com | `#faf9fb` | 12px | - | - | no |
| www.uber.com | `#000000` | 999px | 52px | 700 | no |
| www.warp.dev | `-` | - | 64px | 400 | no |
| www.whoop.com | `#4a53ff` | 16px | 120px | 400 | no |
| www.wired.com | `-` | - | - | - | no |
| www.wix.com | `#166aea` | 50px | 82.5px | 400 | no |
| www.ycombinator.com | `#000000` | 3.35544e+07px | - | - | no |
| www.zapier.com | `#ff4f00` | 18px | 56px | 500 | no |
| zoom.us | `#0b5cff` | 0px | 54px | 500 | no |
| zora.co | `#121212` | 999px | - | - | no |

<!-- generated by scripts/build_spec_catalog.py from 199 sites -->