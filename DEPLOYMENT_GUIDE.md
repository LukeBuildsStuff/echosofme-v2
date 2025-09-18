# Echoes of Me - Vercel Deployment Guide

## WSL Deployment Instructions

Since you're using WSL, deploy via the Vercel web dashboard instead of CLI.

### Step 1: Prepare Files for Upload

Your project is ready! Key files created:
- ✅ `vercel.json` - Vercel configuration
- ✅ `.env.production` - Production environment variables
- ✅ `dist/` folder - Built application (run `npm run build` if needed)

### Step 2: Deploy via Vercel Dashboard

1. **Go to [vercel.com](https://vercel.com)** and sign in
2. **Click "New Project"**
3. **Choose deployment method:**

#### Option A: GitHub Import (Recommended)
- Push your code to GitHub first
- Import the repository in Vercel
- Auto-detection will work

#### Option B: Manual Upload
- Click "Browse" and select your project folder
- Or drag and drop the entire `/home/luke/echosofme-v2` folder

### Step 3: Configure Environment Variables

In Vercel dashboard, add these environment variables:

```
VITE_SUPABASE_URL=https://cbaudsvlidzfxvmzdvcg.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNiYXVkc3ZsaWR6Znh2bXpkdmNnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgwNzEzNzYsImV4cCI6MjA3MzY0NzM3Nn0.I8JpWNqUlhWUkAdAbmRnHxYY0sFOXgyPFgvBSnerNt4
VITE_ELEANOR_API_URL=disabled
VITE_ELEVENLABS_API_KEY=sk_8d0ee2601bd93668e845171f52b4b0e3e0069fe0cc226bc9
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
VITE_ENABLE_PROFILE_SYNC=true
NODE_ENV=production
```

### Step 4: Deploy

- Click "Deploy"
- Wait for build to complete
- Get your live URL (something like `https://echosofme-v2-abc123.vercel.app`)

### Step 5: Configure Custom Domain

1. In Vercel dashboard → Settings → Domains
2. Add `echosofme.io` and `www.echosofme.io`
3. Update DNS at your domain registrar:
   - A record: Point to Vercel's IP
   - CNAME for www: Point to `cname.vercel-dns.com`

### Step 6: Test

- ✅ Login works
- ✅ All 137 reflections load
- ✅ Creating new reflections works
- ✅ Responsive design on mobile

## WSL File Path Access

If uploading manually, your project is at:
```
\\wsl$\Ubuntu\home\luke\echosofme-v2
```

You can copy this to Windows if needed via File Explorer.