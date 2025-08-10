# Deployment Guide

This guide covers deploying the Satellite Embeddings Similarity Search application to various hosting platforms.

## Prerequisites

Before deploying, ensure you have:

1. **Google Maps API Key** with billing enabled
2. **Google Earth Engine Account** (for the backend functionality)
3. **Git repository** with your code
4. **Modern web browser** for testing

## Quick Start

### 1. Prepare Your Code

1. Replace `YOUR_GOOGLE_MAPS_API_KEY` in `index.html` with your actual API key
2. Test locally: `python3 -m http.server 8000`
3. Commit your changes: `git add . && git commit -m "Ready for deployment"`

### 2. Choose Your Platform

Select one of the deployment options below based on your needs:

## Deployment Options

### GitHub Pages (Free, Recommended for Demo)

**Best for**: Personal projects, demos, portfolios

**Steps**:
1. Push your code to a GitHub repository
2. Go to repository Settings → Pages
3. Set Source to "Deploy from a branch"
4. Select "main" branch and "/ (root)" folder
5. Click "Save"
6. Your site will be available at `https://username.github.io/repository-name`

**Pros**: Free, automatic deployments, custom domains
**Cons**: Limited to static content, no server-side processing

### Netlify (Free Tier Available)

**Best for**: Professional projects, team collaboration

**Steps**:
1. Sign up at [netlify.com](https://netlify.com)
2. Click "New site from Git"
3. Connect your GitHub repository
4. Set build settings:
   - Build command: `echo "Static site"`
   - Publish directory: `.`
5. Click "Deploy site"
6. Add your custom domain (optional)

**Pros**: Free tier, automatic deployments, form handling, serverless functions
**Cons**: Limited free tier features

### Vercel (Free Tier Available)

**Best for**: Modern web apps, React/Vue projects

**Steps**:
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Follow the prompts to connect your repository
4. Deploy with: `vercel --prod`

**Pros**: Excellent performance, automatic deployments, edge functions
**Cons**: More complex for simple static sites

### AWS S3 + CloudFront

**Best for**: Enterprise, high-traffic applications

**Steps**:
1. Create an S3 bucket
2. Enable static website hosting
3. Upload your files
4. Create CloudFront distribution
5. Configure custom domain and SSL

**Pros**: Highly scalable, global CDN, enterprise features
**Cons**: More complex setup, costs for high traffic

## Environment Configuration

### API Keys

For production, use environment variables instead of hardcoding API keys:

```javascript
// In app.js
const MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY || 'fallback-key';
```

### Platform-Specific Configuration

#### Netlify
Create `netlify.toml`:
```toml
[build]
  publish = "."
  command = "echo 'Static site'"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
```

#### Vercel
Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static"
    }
  ]
}
```

## Post-Deployment Checklist

### 1. Test Functionality
- [ ] Map loads correctly
- [ ] Click interactions work
- [ ] Responsive design on mobile
- [ ] Loading states display properly
- [ ] Error handling works

### 2. Performance Optimization
- [ ] Enable gzip compression
- [ ] Set appropriate cache headers
- [ ] Optimize images (if any)
- [ ] Minify CSS/JS (optional)

### 3. Security
- [ ] HTTPS enabled
- [ ] API keys secured
- [ ] CORS configured (if needed)
- [ ] Content Security Policy (optional)

### 4. Monitoring
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Configure analytics (Google Analytics, etc.)
- [ ] Monitor API usage and costs

## Troubleshooting

### Common Issues

1. **Map Not Loading**
   - Check API key is correct
   - Verify billing is enabled
   - Check browser console for errors

2. **CORS Errors**
   - Ensure your domain is whitelisted in Google Cloud Console
   - Check API key restrictions

3. **Performance Issues**
   - Enable CDN caching
   - Optimize bundle size
   - Use lazy loading for non-critical resources

### Debug Mode

Enable debug mode in production:
```javascript
// Add to URL: ?debug=true
if (new URLSearchParams(window.location.search).get('debug')) {
    window.app.debug = true;
}
```

## Cost Optimization

### Google Maps API
- Set up billing alerts
- Use appropriate API restrictions
- Consider caching strategies

### Hosting Costs
- Use free tiers when possible
- Monitor usage and scale appropriately
- Consider CDN for global performance

## Maintenance

### Regular Tasks
- [ ] Update dependencies monthly
- [ ] Monitor API usage
- [ ] Check for security updates
- [ ] Review performance metrics

### Backup Strategy
- [ ] Version control (Git)
- [ ] Database backups (if applicable)
- [ ] Configuration backups

## Support Resources

- [Google Maps Platform Documentation](https://developers.google.com/maps)
- [Google Earth Engine Documentation](https://developers.google.com/earth-engine)
- [Netlify Documentation](https://docs.netlify.com)
- [Vercel Documentation](https://vercel.com/docs)
- [GitHub Pages Documentation](https://pages.github.com)

---

**Need Help?** Open an issue on GitHub or check the troubleshooting section above.
