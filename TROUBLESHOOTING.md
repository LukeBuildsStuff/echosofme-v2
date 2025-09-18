# EchosOfMe Troubleshooting Guide

## 🚨 Common Production Issues

### 1. 401 Unauthorized Error on Vercel

**Symptoms:**
- Production site shows "401 Unauthorized"
- Site works locally but not on vercel.app URL
- Users cannot access the application

**Causes:**
- Vercel deployment protection enabled
- Password protection configured
- Team-only access restriction

**Solutions:**

1. **Disable Deployment Protection:**
   ```
   1. Go to Vercel Dashboard
   2. Select your project
   3. Settings → Security & Privacy
   4. Turn OFF "Password Protection"
   5. Turn OFF "Vercel Authentication"
   6. Set deployment visibility to "Public"
   ```

2. **Check Team Settings:**
   ```
   1. Project Settings → General
   2. Ensure "Deployment Protection" is disabled
   3. Verify deployment isn't restricted to team members
   ```

3. **Redeploy:**
   ```bash
   git push origin master
   ```

### 2. Environment Variables Not Working

**Symptoms:**
- App builds but features don't work
- Supabase connection errors
- API calls failing

**Causes:**
- Missing `VITE_` prefix for client-side variables
- Variables not set in Vercel dashboard
- Incorrect variable values

**Solutions:**

1. **Check Variable Names:**
   ```bash
   # Client-side variables MUST have VITE_ prefix
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_ANON_KEY=your-key

   # Server-side variables (backend only)
   SUPABASE_SERVICE_KEY=your-service-key
   ```

2. **Verify in Vercel:**
   ```
   1. Vercel Dashboard → Settings → Environment Variables
   2. Check all required variables are present
   3. Verify values are correct (no extra spaces)
   4. Redeploy after changes
   ```

3. **Test Locally:**
   ```bash
   # Create .env.local with production values
   npm run build
   npm run preview
   ```

### 3. Eleanor API Errors

**Symptoms:**
- "Eleanor API is disabled" messages
- AI features not working
- Timeout errors on API calls

**Causes:**
- Eleanor API not deployed to production
- Network connectivity issues
- API server down

**Solutions:**

1. **Disable Eleanor for Production:**
   ```bash
   # In Vercel environment variables
   VITE_ELEANOR_API_URL=disabled
   ```

2. **Check API Configuration:**
   ```typescript
   // src/utils/apiConfig.ts handles this automatically
   // Will fallback to localStorage when API disabled
   ```

3. **Deploy Eleanor API (Optional):**
   ```bash
   # Deploy to cloud service with GPU support
   # Update VITE_ELEANOR_API_URL to production URL
   ```

### 4. Supabase Connection Issues

**Symptoms:**
- Authentication not working
- Database queries failing
- "Invalid API key" errors

**Causes:**
- Wrong Supabase URL or key
- RLS policies blocking access
- Network restrictions

**Solutions:**

1. **Verify Credentials:**
   ```bash
   # Check in Supabase dashboard → Settings → API
   VITE_SUPABASE_URL=https://your-project-id.supabase.co
   VITE_SUPABASE_ANON_KEY=your-anon-key
   ```

2. **Check RLS Policies:**
   ```sql
   -- Ensure tables have proper RLS policies
   -- Example for reflections table:
   CREATE POLICY "Users can view own reflections"
   ON reflections FOR SELECT
   USING (auth.uid() = user_id);
   ```

3. **Test Connection:**
   ```bash
   # Use Supabase dashboard to test queries
   # Check API logs for errors
   ```

### 5. Build Failures

**Symptoms:**
- Vercel build fails
- TypeScript errors
- Missing dependencies

**Causes:**
- TypeScript compilation errors
- Missing environment variables during build
- Dependency conflicts

**Solutions:**

1. **Fix TypeScript Errors:**
   ```bash
   # Run locally to identify issues
   npm run build

   # Check for type errors
   npx tsc --noEmit
   ```

2. **Check Dependencies:**
   ```bash
   # Ensure all deps are in package.json
   npm install

   # Update lock file
   npm ci
   ```

3. **Review Build Logs:**
   ```
   1. Vercel Dashboard → Deployments
   2. Click on failed deployment
   3. Check "Build Logs" tab
   4. Fix identified issues
   ```

### 6. Custom Domain Issues

**Symptoms:**
- Domain not resolving
- SSL certificate errors
- Redirecting to wrong site

**Causes:**
- DNS records not configured
- Domain not added to Vercel
- SSL certificate pending

**Solutions:**

1. **Configure DNS:**
   ```
   Type: CNAME
   Name: echosofme.io (or @)
   Value: cname.vercel-dns.com
   TTL: Auto or 300
   ```

2. **Verify in Vercel:**
   ```
   1. Vercel Dashboard → Domains
   2. Add echosofme.io
   3. Wait for SSL certificate (5-30 min)
   4. Check domain status
   ```

3. **Test DNS Propagation:**
   ```bash
   # Use online tools or command line
   dig echosofme.io
   nslookup echosofme.io
   ```

### 7. Performance Issues

**Symptoms:**
- Slow loading times
- Large bundle sizes
- Memory usage warnings

**Causes:**
- Large JavaScript bundles
- Unoptimized images
- Too many dependencies

**Solutions:**

1. **Analyze Bundle:**
   ```bash
   # Install bundle analyzer
   npm install --save-dev rollup-plugin-visualizer

   # Add to vite.config.ts
   import { visualizer } from 'rollup-plugin-visualizer';
   ```

2. **Optimize Images:**
   ```bash
   # Compress favicon.png (1.47MB is too large)
   # Use WebP format for better compression
   # Consider using Vercel Image Optimization
   ```

3. **Code Splitting:**
   ```typescript
   // Use dynamic imports for large components
   const LazyComponent = lazy(() => import('./LargeComponent'));
   ```

## 🔧 Development Issues

### Local Development Not Starting

**Symptoms:**
- `npm run dev` fails
- Port conflicts
- Dependency errors

**Solutions:**

1. **Clear Dependencies:**
   ```bash
   rm -rf node_modules
   rm package-lock.json
   npm install
   ```

2. **Check Port:**
   ```bash
   # Default port 5173
   # Change in vite.config.ts if needed
   lsof -ti:5173
   ```

3. **Check Node Version:**
   ```bash
   node --version  # Should be 16+
   npm --version   # Should be 8+
   ```

### Eleanor API Not Starting

**Symptoms:**
- API server crashes
- CUDA errors
- Model loading failures

**Solutions:**

1. **Check GPU:**
   ```bash
   nvidia-smi  # Verify GPU is available
   ```

2. **Check Model Path:**
   ```bash
   # Ensure model files exist
   ls -la ./models/Eleanor/
   ```

3. **Check Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 📊 Monitoring & Debugging

### Production Monitoring

1. **Vercel Analytics:**
   - Function logs
   - Error tracking
   - Performance metrics

2. **Supabase Dashboard:**
   - API logs
   - Database metrics
   - Authentication events

3. **Browser DevTools:**
   - Console errors
   - Network requests
   - Performance profiling

### Debug Information

Add this to your app for debugging:

```typescript
// src/utils/debug.ts
export const getDebugInfo = () => {
  return {
    hostname: window.location.hostname,
    href: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString(),
    env: {
      supabaseUrl: import.meta.env.VITE_SUPABASE_URL,
      eleanorApiUrl: import.meta.env.VITE_ELEANOR_API_URL,
      nodeEnv: import.meta.env.NODE_ENV,
    }
  };
};

// Log in console for debugging
console.log('Debug Info:', getDebugInfo());
```

## 🆘 Getting Help

1. **Check Logs:**
   - Vercel build logs
   - Browser console
   - Supabase logs

2. **Verify Configuration:**
   - Environment variables
   - DNS settings
   - Build settings

3. **Test Locally:**
   - Run production build locally
   - Test with production data
   - Verify all features work

4. **Community Support:**
   - Vercel Discord
   - Supabase Discord
   - Stack Overflow

## 📝 Reporting Issues

When reporting issues, include:

1. **Environment Details:**
   - Browser and version
   - Device type
   - Network connection

2. **Steps to Reproduce:**
   - Exact actions taken
   - Expected vs actual behavior
   - Screenshots if helpful

3. **Error Information:**
   - Console errors
   - Network requests
   - Build logs

4. **Configuration:**
   - Environment variables (sanitized)
   - Deployment settings
   - Recent changes