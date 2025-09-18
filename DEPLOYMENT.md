# EchosOfMe Production Deployment Guide

## 🚀 Overview

This guide covers deploying the EchosOfMe application to production using Vercel with Supabase backend.

## 📋 Prerequisites

- Vercel account
- Supabase project setup
- Domain name (echosofme.io)
- Google OAuth client (optional)
- ElevenLabs API key (optional)

## 🔑 Environment Variables

### Required for Production

Set these in your Vercel project settings → Environment Variables:

```bash
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here

# Eleanor API (Optional - for AI features)
VITE_ELEANOR_API_URL=disabled  # or your production API URL

# Google OAuth (Optional)
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# ElevenLabs Voice (Optional)
VITE_ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Development Settings
VITE_ENABLE_PROFILE_SYNC=true
NODE_ENV=production
```

## 📁 Project Structure

```
echosofme-v2/
├── src/
│   ├── utils/apiConfig.ts         # Dynamic API configuration
│   ├── contexts/                  # React contexts
│   └── ...
├── vercel.json                    # Vercel configuration
├── .env.example                   # Environment variable template
├── package.json                   # Dependencies and scripts
└── DEPLOYMENT.md                  # This file
```

## 🔧 Deployment Steps

### 1. Vercel Setup

1. **Connect Repository:**
   ```bash
   # Push to GitHub
   git push origin master
   ```

2. **Import to Vercel:**
   - Go to vercel.com → New Project
   - Import from GitHub
   - Select echosofme-v2 repository

3. **Configure Build Settings:**
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

### 2. Environment Variables

1. **In Vercel Dashboard:**
   - Go to Settings → Environment Variables
   - Add all required variables from the list above
   - Set appropriate values for production

2. **Important Notes:**
   - `VITE_ELEANOR_API_URL` should be set to `disabled` unless you have a production AI API
   - All `VITE_` prefixed variables are exposed to the client
   - Never commit actual secrets to the repository

### 3. Domain Configuration

1. **Add Custom Domain:**
   - In Vercel Dashboard → Domains
   - Add `echosofme.io`
   - Follow DNS configuration instructions

2. **DNS Records:**
   ```
   Type: CNAME
   Name: echosofme.io (or @)
   Value: cname.vercel-dns.com
   ```

3. **SSL Certificate:**
   - Automatically issued by Vercel
   - Usually takes 5-30 minutes

### 4. Deployment Protection

**Important:** Ensure your deployment is publicly accessible:

1. **In Vercel Dashboard → Security & Privacy:**
   - Disable "Password Protection"
   - Disable "Vercel Authentication"
   - Set deployment visibility to "Public"

2. **Team Settings:**
   - Ensure deployment isn't restricted to team members only

## 🧪 Testing Production Build Locally

```bash
# Build the project
npm run build

# Preview the production build
npm run preview
```

## 🚨 Troubleshooting

### Common Issues

#### 401 Unauthorized Error
- **Cause:** Vercel deployment protection enabled
- **Solution:**
  1. Go to Vercel Dashboard → Settings → Security & Privacy
  2. Disable Password Protection and Vercel Authentication
  3. Ensure deployment is public

#### Environment Variables Not Working
- **Cause:** Missing `VITE_` prefix or not set in Vercel
- **Solution:**
  1. Check all client-side variables have `VITE_` prefix
  2. Verify variables are set in Vercel dashboard
  3. Redeploy after adding variables

#### Eleanor API Errors
- **Cause:** Eleanor API not available in production
- **Solution:**
  1. Set `VITE_ELEANOR_API_URL=disabled` in Vercel
  2. App will fallback to localStorage
  3. Users won't see AI features but core functionality works

#### Supabase Connection Issues
- **Cause:** Incorrect Supabase credentials
- **Solution:**
  1. Verify `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`
  2. Check Supabase project settings
  3. Ensure RLS policies allow public access for authentication

#### Build Failures
- **Cause:** TypeScript errors or missing dependencies
- **Solution:**
  1. Run `npm run build` locally first
  2. Fix any TypeScript errors
  3. Ensure all dependencies are in package.json

### Deployment Checklist

- [ ] All environment variables set in Vercel
- [ ] Deployment protection disabled
- [ ] Custom domain configured
- [ ] SSL certificate issued
- [ ] Build succeeds without errors
- [ ] Authentication works
- [ ] Core features functional
- [ ] Eleanor API fallback working

## 📊 Production Monitoring

### Key URLs
- **Production Site:** https://echosofme.io
- **Vercel Dashboard:** https://vercel.com/dashboard
- **Supabase Dashboard:** https://supabase.com/dashboard

### Health Checks
- Authentication flow
- Reflection creation/viewing
- Data export/import
- Mobile responsiveness

## 🔄 Updating Production

```bash
# Make changes locally
git add .
git commit -m "Your changes"

# Deploy to production
git push origin master
```

Vercel will automatically deploy on push to master branch.

## 🔐 Security Considerations

1. **Environment Variables:**
   - Never commit secrets to repository
   - Use Vercel environment variables for sensitive data
   - Rotate API keys regularly

2. **Supabase Security:**
   - Configure Row Level Security (RLS) policies
   - Use anon key for client-side access
   - Keep service key secure (server-side only)

3. **Domain Security:**
   - Enable HTTPS (automatic with Vercel)
   - Configure CORS policies in Supabase
   - Use secure headers in vercel.json

## 📞 Support

If you encounter issues:

1. Check Vercel build logs
2. Review Supabase logs
3. Verify environment variables
4. Test locally with production build

## 🔗 Related Files

- `src/utils/apiConfig.ts` - API configuration logic
- `vercel.json` - Vercel deployment configuration
- `.env.example` - Environment variable template
- `src/contexts/SupabaseAuthContext.tsx` - Authentication logic