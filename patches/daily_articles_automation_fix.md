# Daily articles automation - root cause + fix (apply manually)

## Root cause (verified from Actions history)
The workflow runs every day at 08:00 UTC and reports SUCCESS, but each run
takes only ~14 seconds and produces NO article and NO commit. The generator
receives empty AI keys because GEMINI_API_KEY / GROQ_API_KEY / OPENAI_API_KEY
are set in Render env vars but NOT in GitHub repo Secrets. The generator
silently exits when keys are missing.

## Fix (2 things)

### 1. Add the AI key to GitHub Secrets (the actual fix)
GitHub repo > Settings > Secrets and variables > Actions > New repository secret:
- Name: GEMINI_API_KEY  Value: (same key you use on Render)
- optionally also GROQ_API_KEY

The existing .github/workflows/daily-articles.yml already passes
secrets.GEMINI_API_KEY / secrets.GROQ_API_KEY / secrets.OPENAI_API_KEY to the
generator, so no workflow change is required for it to work.

### 2. (recommended) Make the workflow fail loudly instead of silently
Add this step to .github/workflows/daily-articles.yml right after checkout,
so a missing key is visible as a red X instead of a fake green check:

      - name: Fail fast when no AI key
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          if [ -z "$GEMINI_API_KEY" ] && [ -z "$GROQ_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
            echo "::error::No AI API key in repo secrets - add one in Settings > Secrets > Actions"
            exit 1
          fi

## Why my tool could not push this directly
The GitHub connector token in this session cannot modify files under
.github/workflows/ (needs the extra workflow OAuth scope), so the workflow
edit itself is provided here as a patch to apply via the GitHub web editor.
