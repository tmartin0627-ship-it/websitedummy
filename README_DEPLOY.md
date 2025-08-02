# Market Indices Tracker - Deployment Guide

A modern, real-time market indices tracker showing S&P 500, NASDAQ, and Dow Jones with interactive historical charts.

## 🚀 Quick Deploy (5 minutes)

### Option 1: Render (Recommended - Free)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/market-indices.git
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Use these settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python market_indices.py`
     - **Instance Type**: Free

3. **Done!** Your site will be live at `https://yourapp.onrender.com`

### Option 2: Railway (Fastest)

1. **Push to GitHub** (same as above)
2. **Deploy**: Go to [railway.app](https://railway.app) → "Deploy from GitHub"
3. **Select your repo** → Railway auto-deploys!

### Option 3: Vercel (Frontend Focus)

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```
2. **Deploy**:
   ```bash
   vercel
   ```
3. **Follow prompts** → Site live instantly!

## 📁 Required Files (Already Created)

- ✅ `market_indices.py` - Main Flask app
- ✅ `requirements.txt` - Dependencies  
- ✅ `Procfile` - Process config
- ✅ `README_DEPLOY.md` - This guide

## 🌐 Live Demo Features

- 📊 **S&P 500, NASDAQ, Dow Jones** real-time display
- 📈 **Interactive charts** with 6 timeframes (1D to 10Y)
- 💫 **Modern glassmorphism** design
- 📱 **Mobile responsive**
- ⚡ **No external APIs** - works everywhere

## 💰 Hosting Costs

| Platform | Free Tier | Paid |
|----------|-----------|------|
| **Render** | ✅ 750 hours/month | $7/month |
| **Railway** | ✅ $5 credit/month | $0.01/hour |
| **Vercel** | ✅ Unlimited | $20/month pro |
| **Heroku** | ❌ No free tier | $7/month |

## 🔧 Custom Domain

Most platforms allow custom domains:
- **Render**: Settings → Custom Domains
- **Vercel**: Project → Domains → Add
- **Railway**: Project → Settings → Domains

## 🚀 Pro Tips

1. **Use Render** for simplicity - best free tier
2. **Use Railway** for fastest deployment
3. **Use Vercel** if you want edge functions later
4. **GitHub Actions** can auto-deploy on commits

Your market tracker will be live and accessible worldwide in minutes!
