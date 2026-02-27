# TranscriptX

Instant video transcripts as a SaaS. Groq Whisper + Polar payments + SQLite.

## Architecture

```
User → TranscriptX (Flask on Railway)
         ├── yt-dlp (downloads audio from URL)
         ├── Groq Whisper API (transcribes audio)
         ├── SQLite (tracks credits per user)
         └── Polar (handles payments + customer accounts)
```

## Pricing Model

- **Free:** 3 transcripts/month (no signup needed)
- **Starter ($2/mo):** 50 transcripts + batch + export
- **Pro ($4/mo):** Unlimited + batch + export

## Files

| File | Purpose |
|------|---------|
| `app.py` | Flask app — routes, UI, Polar webhooks |
| `transcribe.py` | yt-dlp + Groq Whisper engine |
| `database.py` | SQLite — users + credit tracking |
| `Dockerfile` | Container config for Railway |
| `railway.json` | Railway deployment config |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variables template |

## Step-by-Step Deployment

### 1. Get your API keys

**Groq (transcription):**
- Go to https://console.groq.com
- Create account → API Keys → Create key
- Save the key

**Polar (payments):**
- Go to https://sandbox.polar.sh (use sandbox first for testing)
- Create an organization
- Create two products:
  - "Starter" — $2/month recurring
  - "Pro" — $4/month recurring
- For each product, note the Product ID
- Go to Settings → Webhooks → Add endpoint:
  - URL: `https://your-app.railway.app/webhooks/polar`
  - Events: `subscription.created`, `subscription.updated`, `subscription.canceled`, `subscription.revoked`, `subscription.active`
  - Copy the webhook secret
- Create checkout links for each product:
  - Set success URL to: `https://your-app.railway.app/auth/polar/callback?customer_id={CUSTOMER_ID}`

### 2. Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project
railway init

# Add a volume for SQLite (IMPORTANT)
# In Railway dashboard: Service → Settings → Volumes → Add Volume
# Mount path: /data

# Set environment variables
railway variables set GROQ_API_KEY=your_key
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set POLAR_WEBHOOK_SECRET=your_webhook_secret
railway variables set POLAR_STARTER_PRODUCT_ID=your_starter_id
railway variables set POLAR_PRO_PRODUCT_ID=your_pro_id
railway variables set POLAR_CHECKOUT_STARTER=https://polar.sh/checkout/your-starter
railway variables set POLAR_CHECKOUT_PRO=https://polar.sh/checkout/your-pro
railway variables set POLAR_CUSTOMER_PORTAL=https://polar.sh/your-org/portal
railway variables set DB_PATH=/data/transcriptx.db

# Deploy
railway up
```

Or just push to GitHub and connect the repo in Railway's dashboard — it auto-deploys on every push.

### 3. Add custom domain (optional)

In Railway dashboard: Service → Settings → Networking → Add custom domain.

### 4. Go live with Polar

Once tested on sandbox, switch to production:
- Create the same products on https://polar.sh (not sandbox)
- Update the environment variables with production IDs
- Update webhook URL to your production domain

## Local Development

```bash
# Create venv
python3 -m venv .venv
source .venv/bin/activate

# Install deps
pip install -r requirements.txt

# Also need ffmpeg
brew install ffmpeg  # Mac
sudo apt install ffmpeg  # Linux

# Set env vars
cp .env.example .env
# Edit .env with your keys

# Run
python app.py
# Open http://localhost:5000
```

## Cost Breakdown

| Service | Cost |
|---------|------|
| Railway | ~$5/month |
| Groq Whisper | $0.04/hour of audio (~$0.001 per reel) |
| Polar | 4% + $0.40 per transaction (only when you earn) |
| SQLite | Free (file on disk) |
| Instagram API | Free |
| **Total fixed cost** | **~$5/month** |

Profitable from user #2.

## Troubleshooting

**yt-dlp fails on Instagram:** Run `pip install -U yt-dlp` — Instagram changes their site frequently and yt-dlp updates to match.

**Groq returns error:** Check your API key is valid and you haven't hit rate limits. Free tier has generous limits.

**Credits not resetting:** Credits reset 30 days after the user's first use. Check the `credits_reset_at` field in the SQLite database.

**Webhook not working:** Make sure the webhook URL is correct and the endpoint URL in Polar matches your Railway URL exactly including `/webhooks/polar`.
