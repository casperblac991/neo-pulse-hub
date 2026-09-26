# NEO PULSE HUB

**Global smart technology marketplace with AI-assisted discovery, customer support, and growth automation.**

NEO PULSE HUB is an Arabic-first, English-ready technology marketplace for smartwatches, earbuds, smart-home devices, AI tools, and connected accessories. The public storefront supports Arabic and English, multiple currencies, responsive browsing, product comparison, and affiliate purchase links.

## Current architecture

The repository has two delivery layers with clear responsibilities:

- **Public storefront:** static HTML pages served by GitHub Pages at [neo-pulse-hub.it.com](https://neo-pulse-hub.it.com). It loads the canonical `products.json` catalog directly and remains available without login.
- **Dynamic application:** React 19 + Express/tRPC under `client/` and `server/`. It provides the operations dashboard, protected Copilot, automation views, and typed server procedures.
- **AI services:** `backend/ai_engine.py` supports Gemini, Groq, and OpenAI with local fallbacks. `backend/ai_orchestrator.py` is the Python facade, while `server/ai-orchestrator.ts` is the Node/React Copilot facade.
- **Catalog:** `products.json` is the public canonical catalog. `scripts/normalize_catalog.py` validates and normalizes it without creating fictional prices, ratings, or product claims.

## Global experience

The public pages include Arabic/English switching, RTL/LTR direction changes, USD/SAR/AED/EUR display, SEO metadata, responsive layouts, product search, category filtering, image fallbacks, and affiliate links. The storefront never requires an admin session to display products.

## Local development

### Python checks

```bash
python3 scripts/normalize_catalog.py --check
python3 -m py_compile backend/ai_engine.py backend/ai_orchestrator.py
python3 -m unittest discover -s backend -p 'test_ai_engine.py' -v
```

### React and server build

The repository uses the lockfile in `pnpm-lock.yaml`:

```bash
npm exec --yes pnpm@10.15.1 -- install --frozen-lockfile
npm exec --yes pnpm@10.15.1 -- run dev
```

For a production build:

```bash
npm exec --yes pnpm@10.15.1 -- run build
```

## Environment variables

Copy `.env.example` to a local, untracked `.env` file. Never commit real credentials.

Important optional variables include:

```text
GEMINI_API_KEY=
GROQ_API_KEY=
OPENAI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash
GROQ_MODEL=llama-3.3-70b-versatile
OPENAI_MODEL=gpt-4o-mini
STORE_SHIPPING_DAYS=3-7 أيام عمل
STORE_FREE_SHIPPING_MINIMUM=150
STORE_RETURN_DAYS=30
```

## Automation and deployment

- `deploy.yml` validates the canonical catalog, runs Python tests, builds the React application, and verifies the GitHub Pages custom domain.
- `catalog-sync.yml` runs every six hours and applies deterministic catalog normalization. It does not use random mock products or fabricated prices.
- `daily-articles.yml` runs the separate article generator once per day.

GitHub Pages is suitable for the public static storefront. It cannot run Express, MySQL, Telegram webhooks, or a persistent AI server. The React/Node application therefore requires a Node-capable host before it can replace the public static storefront at the domain.

## Data quality policy

The project does not treat generated text as verified commercial data. Product prices, ratings, specifications, images, and affiliate URLs must come from a configured source. If no trusted source is available, the system uses a visible fallback or reports that the information is unavailable rather than inventing it.

## Security policy

Real API keys and bot tokens belong only in environment variables or GitHub Actions secrets. Historical documentation is redacted and CI should fail if credential patterns are reintroduced.

## License

MIT. Product names, images, trademarks, and affiliate links remain the property of their respective owners.
