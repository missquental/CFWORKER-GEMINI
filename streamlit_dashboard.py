import streamlit as st
import requests
import json
import os
from datetime import datetime
import base64
import markdown
import re
from utils import generate_post_id, extract_excerpt_from_content, truncate_text

# Import AI modules with error handling
try:
    from gemini import GeminiScraper
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    st.warning("⚠️ Gemini AI tidak tersedia. Install: pip install google-generativeai langdetect langcodes")

try:
    from bingimage import BingImageScraper
    BING_AVAILABLE = True
except ImportError:
    BING_AVAILABLE = False
    st.warning("⚠️ Bing Image scraper tidak tersedia. Install: pip install beautifulsoup4 pillow")

# Konfigurasi halaman
st.set_page_config(
    page_title="Blog Management Dashboard",
    page_icon="📝",
    layout="wide"
)

# CSS untuk styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .blog-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        background: #f9f9f9;
    }
    .success-msg {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .error-msg {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'posts' not in st.session_state:
        st.session_state.posts = []
    if 'cf_account_id' not in st.session_state:
        st.session_state.cf_account_id = ""
    if 'cf_api_token' not in st.session_state:
        st.session_state.cf_api_token = ""
    if 'worker_subdomain' not in st.session_state:
        st.session_state.worker_subdomain = ""
    if 'worker_name' not in st.session_state:
        st.session_state.worker_name = ""
    if 'account_name' not in st.session_state:
        st.session_state.account_name = ""

def get_account_name(account_id, api_token):
    """Ambil nama akun berdasarkan account_id"""
    try:
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        response = requests.get("https://api.cloudflare.com/client/v4/accounts", headers=headers)
        if response.status_code == 200:
            accounts = response.json().get("result", [])
            for acc in accounts:
                if acc["id"] == account_id:
                    return acc["name"]
        return None
    except Exception as e:
        return None

def format_account_name(account_name):
    """Format nama akun untuk subdomain yang valid"""
    if not account_name:
        return None
    
    # Hapus karakter yang tidak valid untuk subdomain
    # Hanya izinkan huruf, angka, dan dash
    import re
    
    # Ambil bagian sebelum @ jika ada email
    if '@' in account_name:
        account_name = account_name.split('@')[0]
    
    # Hapus 'saccount atau karakter serupa
    account_name = re.sub(r"'s?account", "", account_name, flags=re.IGNORECASE)
    
    # Ganti karakter tidak valid dengan dash atau hapus
    account_name = re.sub(r'[^a-zA-Z0-9-]', '', account_name)
    
    # Hapus dash berturut-turut dan di awal/akhir
    account_name = re.sub(r'-+', '-', account_name).strip('-')
    
    # Konversi ke lowercase
    account_name = account_name.lower()
    
    # Pastikan tidak kosong dan tidak terlalu panjang
    if not account_name or len(account_name) < 1:
        return "user"
    
    # Batasi panjang maksimal 63 karakter (standar DNS)
    return account_name[:63]
def authenticate():
    """Authentication form"""
    st.markdown('<div class="main-header"><h1>🚀 Blog Management System</h1><p>Kelola blog Cloudflare Worker Anda dengan mudah</p></div>', unsafe_allow_html=True)
    
    with st.form("auth_form"):
        st.subheader("🔐 Konfigurasi Cloudflare")
        
        account_id = st.text_input(
            "Account ID Cloudflare:",
            placeholder="Masukkan Account ID dari dashboard Cloudflare",
            help="Bisa ditemukan di dashboard Cloudflare bagian kanan bawah"
        )
        
        api_token = st.text_input(
            "API Token:",
            type="password",
            placeholder="Masukkan API Token dengan permission Workers:Edit",
            help="Buat di https://dash.cloudflare.com/profile/api-tokens"
        )

        subdomain = st.text_input(
            "Subdomain:",
            placeholder="contoh: blog",
            help="Subdomain unik untuk worker"
        )
        
        submit = st.form_submit_button("🔗 Connect", use_container_width=True)
        
        if submit:
            if account_id and api_token and subdomain:
                if test_cloudflare_connection(account_id, api_token):
                    account_name = get_account_name(account_id, api_token)
                    if account_name:
                        # Format: <WORKER_NAME>.<ACCOUNT_NAME>.workers.dev
                        worker_name = subdomain
                        account_subdomain = format_account_name(account_name)
                        full_worker_url = f"{worker_name}.{account_subdomain}.workers.dev"
                        
                        st.session_state.cf_account_id = account_id
                        st.session_state.cf_api_token = api_token
                        st.session_state.worker_name = worker_name
                        st.session_state.worker_subdomain = full_worker_url
                        st.session_state.account_name = account_name
                        st.session_state.authenticated = True
                        st.success(f"✅ Koneksi berhasil! Worker akan di-deploy ke: {full_worker_url}")
                        st.rerun()
                    else:
                        st.error("❌ Gagal mengambil nama akun. Periksa API Token dan Account ID.")
                else:
                    st.error("❌ Gagal terhubung ke Cloudflare. Periksa credentials Anda.")
            else:
                st.error("❌ Semua field harus diisi!")

def test_cloudflare_connection(account_id, api_token):
    """Test connection to Cloudflare API"""
    try:
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"https://api.cloudflare.com/client/v4/accounts/{account_id}", headers=headers)
        return response.status_code == 200
    except:
        return False

def deploy_worker(script_content):
    """Deploy worker to Cloudflare"""
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.cf_api_token}",
            "Content-Type": "application/javascript"
        }
        
        # Deploy worker dengan nama yang benar
        url = f"https://api.cloudflare.com/client/v4/accounts/{st.session_state.cf_account_id}/workers/scripts/{st.session_state.worker_name}"
        
        response = requests.put(url, headers=headers, data=script_content)
        
        if response.status_code == 200:
            # Enable subdomain untuk worker
            subdomain_url = f"https://api.cloudflare.com/client/v4/accounts/{st.session_state.cf_account_id}/workers/scripts/{st.session_state.worker_name}/subdomain"
            subdomain_data = {"enabled": True}
            
            subdomain_headers = {
                "Authorization": f"Bearer {st.session_state.cf_api_token}",
                "Content-Type": "application/json"
            }
            
            requests.post(subdomain_url, headers=subdomain_headers, json=subdomain_data)
            return True
        return False
    except Exception as e:
        st.error(f"Error deploying worker: {str(e)}")
        return False

def generate_worker_script():
    """Generate worker script dengan posts dari session state"""
    posts_json = json.dumps(st.session_state.posts, indent=2)
    
    return f"""
// Blog Worker untuk Cloudflare
addEventListener('fetch', event => {{
  event.respondWith(handleRequest(event.request))
}})

const posts = {posts_json};

const HTML_TEMPLATE = `
const HTML_TEMPLATE = `
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <meta name="description" content="{{description}}">
    <meta name="keywords" content="blog, teknologi, tutorial, tips">
    <meta name="author" content="${BLOG_CONFIG.author}">
    
    <!-- Open Graph Meta Tags -->
    <meta property="og:title" content="{{title}}">
    <meta property="og:description" content="{{description}}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{{url}}">
    
    <!-- Twitter Card Meta Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{{title}}">
    <meta name="twitter:description" content="{{description}}">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* Header Styles */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            text-decoration: none;
            color: white;
        }
        
        .nav-menu {
            display: flex;
            list-style: none;
            gap: 2rem;
        }
        
        .nav-menu a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: opacity 0.3s ease;
        }
        
        .nav-menu a:hover {
            opacity: 0.8;
        }
        
        /* Hero Section */
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 4rem 0;
        }
        
        .hero h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        
        .hero p {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }
        
        /* Main Layout */
        .main-layout {
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 2rem;
            margin: 2rem 0;
        }
        
        .content-area {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        /* Sidebar Styles */
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }
        
        .widget {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .widget h3 {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #2d3748;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5rem;
        }
        
        .widget ul {
            list-style: none;
        }
        
        .widget ul li {
            padding: 0.5rem 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .widget ul li:last-child {
            border-bottom: none;
        }
        
        .widget ul li a {
            color: #4a5568;
            text-decoration: none;
            transition: color 0.3s ease;
        }
        
        .widget ul li a:hover {
            color: #667eea;
        }
        
        /* Ad Spaces */
        .ad-space {
            background: linear-gradient(45deg, #f0f2f5, #e2e8f0);
            border: 2px dashed #cbd5e0;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            color: #718096;
            font-weight: 500;
            margin: 1rem 0;
        }
        
        .ad-banner {
            min-height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .ad-sidebar {
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Post Styles */
        .post-card {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            border-left: 4px solid #667eea;
        }
        
        .post-card:hover {
            transform: translateY(-2px);
        }
        
        .post-title {
            font-size: 1.6rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
            color: #2d3748;
            line-height: 1.3;
        }
        
        .post-title a {
            color: inherit;
            text-decoration: none;
        }
        
        .post-title a:hover {
            color: #667eea;
        }
        
        .post-meta {
            color: #718096;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            display: flex;
            gap: 1rem;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .post-meta span {
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }
        
        .post-content {
            color: #4a5568;
            line-height: 1.8;
            font-size: 1rem;
            margin-bottom: 1rem;
        }
        
        .post-content h1, .post-content h2, .post-content h3 {
            color: #2d3748;
            margin: 2rem 0 1rem 0;
            font-weight: 600;
        }
        
        .post-content h1 {
            font-size: 1.8rem;
            border-bottom: 3px solid #667eea;
            padding-bottom: 0.5rem;
        }
        
        .post-content h2 {
            font-size: 1.5rem;
            border-left: 4px solid #667eea;
            padding-left: 1rem;
        }
        
        .post-content h3 {
            font-size: 1.3rem;
            color: #667eea;
        }
        
        /* Styling untuk heading dengan format **Text:** */
        .post-content .section-heading {
            font-size: 1.4rem;
            font-weight: 700;
            color: #2d3748;
            margin: 2rem 0 1rem 0;
            padding: 0.8rem 1.2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            position: relative;
            display: block;
        }
        
        .post-content .section-heading::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 4px 0 0 4px;
        }
        
        .post-content strong {
            color: #2d3748;
            font-weight: 600;
        }
        
        .post-content p {
            margin-bottom: 1.2rem;
            text-align: justify;
        }
        
        .post-content img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 1.5rem 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        
        .read-more {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            transition: all 0.3s ease;
        }
        
        .read-more:hover {
            background: rgba(102, 126, 234, 0.1);
            transform: translateX(4px);
        }
        
        /* Social Share */
        .social-share {
            display: flex;
            gap: 1rem;
            margin: 2rem 0;
            padding: 1rem;
            background: #f7fafc;
            border-radius: 8px;
        }
        
        .social-share a {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: white;
            color: #4a5568;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .social-share a:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        /* Footer */
        .footer {
            background: #2d3748;
            color: white;
            padding: 3rem 0 1rem;
            margin-top: 4rem;
        }
        
        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .footer-section h3 {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #e2e8f0;
        }
        
        .footer-section p, .footer-section a {
            color: #a0aec0;
            text-decoration: none;
            line-height: 1.6;
        }
        
        .footer-section a:hover {
            color: #667eea;
        }
        
        .footer-bottom {
            border-top: 1px solid #4a5568;
            padding-top: 1rem;
            text-align: center;
            color: #a0aec0;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .main-layout {
                grid-template-columns: 1fr;
            }
            
            .sidebar {
                order: -1;
            }
            
            .hero h1 {
                font-size: 2rem;
            }
            
            .nav-menu {
                display: none;
            }
            
            .header-content {
                justify-content: center;
            }
            
            .social-share {
                flex-wrap: wrap;
            }
            
            .footer-content {
                grid-template-columns: 1fr;
                text-align: center;
            }
        }
        
        /* Pagination */
        .pagination {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin: 2rem 0;
        }
        
        .pagination a, .pagination span {
            padding: 0.5rem 1rem;
            background: white;
            color: #4a5568;
            text-decoration: none;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
        }
        
        .pagination a:hover {
            background: #667eea;
            color: white;
        }
        
        .pagination .current {
            background: #667eea;
            color: white;
        }
        
        /* Search Box */
        .search-box {
            display: flex;
            margin-bottom: 1rem;
        }
        
        .search-box input {
            flex: 1;
            padding: 0.5rem;
            border: 1px solid #e2e8f0;
            border-radius: 6px 0 0 6px;
            outline: none;
        }
        
        .search-box button {
            padding: 0.5rem 1rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 0 6px 6px 0;
            cursor: pointer;
        }
        
        /* Tags */
        .tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 1rem 0;
        }
        
        .tag {
            background: #e2e8f0;
            color: #4a5568;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            text-decoration: none;
            transition: all 0.3s ease;
        }
        
        .tag:hover {
            background: #667eea;
            color: white;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="container">
            <div class="header-content">
                <a href="/" class="logo">📝 ${BLOG_CONFIG.title}</a>
                <nav>
                    <ul class="nav-menu">
                        <li><a href="/">Beranda</a></li>
                        <li><a href="/category/tutorial">Tutorial</a></li>
                        <li><a href="/category/teknologi">Teknologi</a></li>
                        <li><a href="/about">Tentang</a></li>
                        <li><a href="/contact">Kontak</a></li>
                    </ul>
                </nav>
            </div>
        </div>
    </header>

    {{hero}}

    <!-- Main Content -->
    <div class="container">
        <div class="main-layout">
            <!-- Content Area -->
            <main class="content-area">
                {{content}}
                
                <!-- Ad Banner -->
                <div class="ad-space ad-banner">
                    <div>
                        <h4>📢 Ruang Iklan Banner</h4>
                        <p>728x90 atau 970x250 pixels</p>
                        <small>Hubungi kami untuk beriklan di sini</small>
                    </div>
                </div>
            </main>
const HTML_TEMPLATE = `
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <meta name="description" content="{{description}}">
    <meta name="keywords" content="blog, teknologi, tutorial, tips">
    <meta name="author" content="${BLOG_CONFIG.author}">
    
    <!-- Open Graph Meta Tags -->
    <meta property="og:title" content="{{title}}">
    <meta property="og:description" content="{{description}}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{{url}}">
    
    <!-- Twitter Card Meta Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{{title}}">
    <meta name="twitter:description" content="{{description}}">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* Header Styles */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .header-content {
            display: flex;

async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;

  // Handle CORS for API requests
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  }

  if (path === '/') {
    return new Response(getHomePage(), {
      headers: { 
        'Content-Type': 'text/html',
        'Cache-Control': 'public, max-age=300'
      }
    });
  }

  if (path.startsWith('/post/')) {
    const postId = path.replace('/post/', '');
    return new Response(getPostPage(postId), {
      headers: { 
        'Content-Type': 'text/html',
        'Cache-Control': 'public, max-age=300'
      }
    });
  }

  if (path.startsWith('/category/')) {
    const category = path.replace('/category/', '');
    return new Response(getCategoryPage(category), {
      headers: { 
        'Content-Type': 'text/html',
        'Cache-Control': 'public, max-age=300'
      }
    });
  }

  if (path.startsWith('/tag/')) {
    const tag = path.replace('/tag/', '');
    return new Response(getTagPage(tag), {
      headers: { 
        'Content-Type': 'text/html',
        'Cache-Control': 'public, max-age=300'
      }
    });
  }

  // API endpoint untuk mendapatkan posts (untuk debugging)
  if (path === '/api/posts') {
    return new Response(JSON.stringify(posts), {
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }

  return new Response('404 Not Found', { 
    status: 404,
    headers: { 'Content-Type': 'text/html' }
  });
}

function getHomePage() {
  const hero = `
    <div class="hero">
        <div class="container">
            <h1>${BLOG_CONFIG.title}</h1>
            <p>${BLOG_CONFIG.subtitle}</p>
        </div>
    </div>
  `;

  const postsHtml = posts.map(post => `
    <article class="post-card">
      <h2 class="post-title">
        <a href="/post/${post.id}">${post.title}</a>
      </h2>
      <div class="post-meta">
        <span>📅 ${post.date}</span>
        <span>✍️ ${post.author}</span>
        <span>📂 ${post.category}</span>
      </div>
      <div class="post-content">${post.excerpt}</div>
      <div class="tags">
        ${post.tags ? post.tags.map(tag => `<a href="/tag/${tag}" class="tag">${tag}</a>`).join('') : ''}
      </div>
      <a href="/post/${post.id}" class="read-more">
        Baca selengkapnya <span>→</span>
      </a>
    </article>
  `).join('');

  const content = `
    ${postsHtml}
    <div class="pagination">
      <span class="current">1</span>
      <a href="/page/2">2</a>
      <a href="/page/3">3</a>
      <a href="/page/2">Selanjutnya →</a>
    </div>
  `;

        <div class="post-content">${processedContent}</div>
    .replace('{{title}}', `${BLOG_CONFIG.title} - ${BLOG_CONFIG.subtitle}`)
    .replace('{{description}}', BLOG_CONFIG.description)
    .replace('{{url}}', 'https://yourdomain.workers.dev')
    .replace('{{hero}}', hero)
    .replace('{{content}}', content);
}

function getPostPage(postId) {
  const post = posts.find(p => p.id === postId);
  
  if (!post) {
    const content = `
      <article class="post-card">
        <h1>404 - Postingan Tidak Ditemukan</h1>
        <p>Maaf, postingan yang Anda cari tidak dapat ditemukan.</p>
        <a href="/" class="read-more">← Kembali ke Beranda</a>
      </article>
    `;
    
    return HTML_TEMPLATE
      .replace('{{title}}', '404 - Tidak Ditemukan')
      .replace('{{description}}', 'Halaman tidak ditemukan')
      .replace('{{url}}', 'https://yourdomain.workers.dev')
      .replace('{{hero}}', '')
      .replace('{{content}}', content);
  }

  // Process content to convert **Heading:** format to proper HTML
  let processedContent = post.content;
  
  // Convert **Text:** to section headings
  processedContent = processedContent.replace(
    /\*\*([^*]+):\*\*/g, 
    '<div class="section-heading">$1</div>'
  );
  
  // Convert remaining **text** to strong
  processedContent = processedContent.replace(
    /\*\*([^*]+)\*\*/g, 
    '<strong>$1</strong>'
  );
  
  // Convert line breaks to proper paragraphs
  processedContent = processedContent.replace(/\n\n/g, '</p><p>');
  processedContent = '<p>' + processedContent + '</p>';
  
  // Clean up empty paragraphs
  processedContent = processedContent.replace(/<p><\/p>/g, '');
  processedContent = processedContent.replace(/<p>\s*<div/g, '<div');
  processedContent = processedContent.replace(/<\/div>\s*<\/p>/g, '</div>');
  const content = `
    <article class="post-card">
      <h1 class="post-title">${post.title}</h1>
      <div class="post-meta">
        <span>📅 ${post.date}</span>
        <span>✍️ ${post.author}</span>
        <span>📂 ${post.category}</span>
      </div>
      <div class="post-content">${post.content}</div>
      <div class="tags">
        ${post.tags ? post.tags.map(tag => `<a href="/tag/${tag}" class="tag">${tag}</a>`).join('') : ''}
      </div>
    </article>

    <!-- Social Share -->
    <div class="social-share">
      <a href="https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent('https://yourdomain.workers.dev/post/' + post.id)}" target="_blank">
        📘 Share di Facebook
      </a>
      <a href="https://twitter.com/intent/tweet?text=${encodeURIComponent(post.title)}&url=${encodeURIComponent('https://yourdomain.workers.dev/post/' + post.id)}" target="_blank">
        🐦 Share di Twitter
      </a>
      <a href="https://wa.me/?text=${encodeURIComponent(post.title + ' - https://yourdomain.workers.dev/post/' + post.id)}" target="_blank">
        💬 Share di WhatsApp
      </a>
    </div>

    <!-- Navigation -->
    <div style="display: flex; justify-content: space-between; margin: 2rem 0;">
      <a href="/" class="read-more">← Kembali ke Beranda</a>
      <a href="#" class="read-more">Artikel Selanjutnya →</a>
    </div>
  `;

  return HTML_TEMPLATE
    .replace('{{title}}', `${post.title} - ${BLOG_CONFIG.title}`)
    .replace('{{description}}', post.excerpt)
    .replace('{{url}}', `https://yourdomain.workers.dev/post/${post.id}`)
    .replace('{{hero}}', '')
    .replace('{{content}}', content);
}

function getCategoryPage(category) {
  const categoryPosts = posts.filter(post => 
    post.category && post.category.toLowerCase() === category.toLowerCase()
  );

  const hero = `
    <div class="hero">
        <div class="container">
            <h1>Kategori: ${category.charAt(0).toUpperCase() + category.slice(1)}</h1>
            <p>Menampilkan ${categoryPosts.length} artikel dalam kategori ini</p>
        </div>
    </div>
  `;

  const postsHtml = categoryPosts.map(post => `
    <article class="post-card">
      <h2 class="post-title">
        <a href="/post/${post.id}">${post.title}</a>
      </h2>
      <div class="post-meta">
        <span>📅 ${post.date}</span>
        <span>✍️ ${post.author}</span>
      </div>
      <div class="post-content">${post.excerpt}</div>
      <a href="/post/${post.id}" class="read-more">
        Baca selengkapnya <span>→</span>
      </a>
    </article>
  `).join('');

  const content = categoryPosts.length > 0 ? postsHtml : `
    <div class="post-card">
      <h2>Tidak ada artikel dalam kategori ini</h2>
      <p>Belum ada artikel yang dipublikasikan dalam kategori "${category}".</p>
      <a href="/" class="read-more">← Kembali ke Beranda</a>
    </div>
  `;

  return HTML_TEMPLATE
    .replace('{{title}}', `Kategori ${category} - ${BLOG_CONFIG.title}`)
    .replace('{{description}}', `Artikel dalam kategori ${category}`)
    .replace('{{url}}', `https://yourdomain.workers.dev/category/${category}`)
    .replace('{{hero}}', hero)
    .replace('{{content}}', content);
}

function getTagPage(tag) {
  const tagPosts = posts.filter(post => 
    post.tags && post.tags.some(t => t.toLowerCase() === tag.toLowerCase())
  );

  const hero = `
    <div class="hero">
        <div class="container">
            <h1>Tag: ${tag}</h1>
            <p>Menampilkan ${tagPosts.length} artikel dengan tag ini</p>
        </div>
    </div>
  `;

  const postsHtml = tagPosts.map(post => `
    <article class="post-card">
      <h2 class="post-title">
        <a href="/post/${post.id}">${post.title}</a>
      </h2>
      <div class="post-meta">
        <span>📅 ${post.date}</span>
        <span>✍️ ${post.author}</span>
        <span>📂 ${post.category}</span>
      </div>
      <div class="post-content">${post.excerpt}</div>
      <a href="/post/${post.id}" class="read-more">
        Baca selengkapnya <span>→</span>
      </a>
    </article>
  `).join('');

  const content = tagPosts.length > 0 ? postsHtml : `
    <div class="post-card">
      <h2>Tidak ada artikel dengan tag ini</h2>
      <p>Belum ada artikel yang menggunakan tag "${tag}".</p>
      <a href="/" class="read-more">← Kembali ke Beranda</a>
    </div>
  `;

  return HTML_TEMPLATE
    .replace('{{title}}', `Tag ${tag} - ${BLOG_CONFIG.title}`)
    .replace('{{description}}', `Artikel dengan tag ${tag}`)
    .replace('{{url}}', `https://yourdomain.workers.dev/tag/${tag}`)
    .replace('{{hero}}', hero)
    .replace('{{content}}', content);
}
"""

def main_dashboard():
    """Main dashboard interface"""
    st.markdown('<div class="main-header"><h1>📝 Blog Management</h1></div>', unsafe_allow_html=True)
    
    # Sidebar untuk navigasi
    with st.sidebar:
        st.header("🎛️ Menu")
        page = st.selectbox("Pilih Halaman:", ["📋 Kelola Post", "🚀 Deploy", "⚙️ Settings"])
        
        st.markdown("---")
        # Format ulang URL untuk display yang benar
        if 'worker_name' in st.session_state and 'account_name' in st.session_state:
            clean_account = format_account_name(st.session_state.account_name)
            display_url = f"{st.session_state.worker_name}.{clean_account}.workers.dev"
            st.markdown(f"**Worker URL:**  \n`https://{display_url}`")
        else:
            st.markdown(f"**Worker URL:**  \n`https://{st.session_state.worker_subdomain}`")
        st.markdown(f"**Account:** {st.session_state.account_name}")
        st.markdown(f"**Worker Name:** {st.session_state.worker_name}")
        
        if st.button("🔓 Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    if page == "📋 Kelola Post":
        manage_posts()
    elif page == "🚀 Deploy":
        deploy_page()
    elif page == "⚙️ Settings":
        settings_page()

def manage_posts():
    """Interface untuk mengelola posts"""
    st.header("📋 Kelola Postingan")
    
    # Tab untuk manual dan AI generation
    tab1, tab2 = st.tabs(["✍️ Manual Post", "🤖 AI Generated Post"])
    
    with tab2:
        ai_post_generator()
    
    with tab1:
        manual_post_form()
    
    # Daftar posts yang ada
    st.subheader("📚 Daftar Postingan")
    
    if st.session_state.posts:
        for i, post in enumerate(st.session_state.posts):
            with st.container():
                st.markdown(f"""
                <div class="blog-card">
                    <h3>{post['title']}</h3>
                    <p><strong>ID:</strong> {post['id']} | <strong>Tanggal:</strong> {post['date']} | <strong>Penulis:</strong> {post['author']}</p>
                    <p>{post['excerpt'][:100]}...</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    if st.button(f"🗑️ Hapus", key=f"delete_{i}"):
                        st.session_state.posts.pop(i)
                        st.rerun()
                with col2:
                    if st.button(f"👁️ Preview", key=f"preview_{i}"):
                        st.session_state[f"show_preview_{i}"] = not st.session_state.get(f"show_preview_{i}", False)
                
                # Show preview if toggled
                if st.session_state.get(f"show_preview_{i}", False):
                    st.markdown("**Preview Konten:**")
                    # Convert markdown to HTML for preview
                    html_content = markdown.markdown(post['content'])
                    st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.info("📝 Belum ada postingan. Tambahkan post pertama Anda!")

def ai_post_generator():
    """Interface untuk generate post menggunakan AI"""
    st.subheader("🤖 Generate Post dengan AI")
    
    if not GEMINI_AVAILABLE:
        st.error("❌ Gemini AI tidak tersedia. Install dependencies yang diperlukan.")
        return
    
    with st.form("ai_post_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            keyword = st.text_input(
                "🔍 Keyword/Topik:",
                placeholder="Contoh: teknologi AI, resep masakan, tips kesehatan",
                help="Masukkan topik yang ingin dijadikan artikel"
            )
            
            language = st.selectbox(
                "🌐 Bahasa:",
                options=["id", "en"],
                format_func=lambda x: "🇮🇩 Indonesia" if x == "id" else "🇺🇸 English"
            )
            
            author = st.text_input("✍️ Penulis:", value="AI Assistant")
        
        with col2:
            include_images = st.checkbox("🖼️ Sertakan Gambar", value=True)
            
            if include_images:
                max_images = st.slider("Jumlah Gambar:", 1, 5, 3)
                image_keyword = st.text_input(
                    "🔍 Keyword Gambar (opsional):",
                    placeholder="Kosongkan untuk menggunakan keyword utama"
                )
            
            custom_post_id = st.text_input(
                "🆔 Custom Post ID (opsional):",
                placeholder="Akan di-generate otomatis jika kosong"
            )
        
        generate_btn = st.form_submit_button("🚀 Generate Post", use_container_width=True)
        
        if generate_btn:
            if keyword:
                generate_ai_post(keyword, language, author, include_images, 
                               max_images if include_images else 0, 
                               image_keyword if include_images else "", 
                               custom_post_id)
            else:
                st.error("❌ Keyword/topik harus diisi!")

def generate_ai_post(keyword, language, author, include_images, max_images, image_keyword, custom_post_id):
    """Generate post menggunakan AI"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Initialize Gemini
        status_text.text("🤖 Menginisialisasi Gemini AI...")
        progress_bar.progress(10)
        
        gemini = GeminiScraper()
        
        # Step 2: Generate content
        status_text.text("✍️ Menghasilkan konten artikel...")
        progress_bar.progress(30)
        
        article_content = gemini.generate_article(keyword, language)
        
        if not article_content:
            st.error("❌ Gagal menghasilkan konten artikel. Coba lagi.")
            return
        
        # Step 3: Extract title and content
        status_text.text("📝 Memproses konten...")
        progress_bar.progress(50)
        
        # Extract title from content (first line or first heading)
        lines = article_content.split('\n')
        title = keyword  # Default title
        content_start = 0
        
        for i, line in enumerate(lines):
            if line.strip():
                # Check if it's a heading
                if line.startswith('#'):
                    title = line.replace('#', '').strip()
                    content_start = i + 1
                    break
                elif len(line.strip()) < 100:  # Likely a title
                    title = line.strip()
                    content_start = i + 1
                    break
        
        # Get content without title
        content = '\n'.join(lines[content_start:]).strip()
        
        # Generate post ID
        post_id = custom_post_id if custom_post_id else generate_post_id(title)
        
        # Step 4: Get images if requested
        image_urls = []
        if include_images and BING_AVAILABLE:
            status_text.text("🖼️ Mencari gambar...")
            progress_bar.progress(70)
            
            try:
                bing_scraper = BingImageScraper()
                search_query = image_keyword if image_keyword else keyword
                image_urls = bing_scraper.get_image_urls(search_query, max_images)
                bing_scraper.close()
                
                if image_urls:
                    st.success(f"✅ Ditemukan {len(image_urls)} gambar")
                else:
                    st.warning("⚠️ Tidak ada gambar yang ditemukan")
                    
            except Exception as e:
                st.warning(f"⚠️ Error saat mencari gambar: {str(e)}")
        
        # Step 5: Insert images into content
        if image_urls:
            status_text.text("🎨 Menyisipkan gambar ke konten...")
            progress_bar.progress(85)
            
            content = insert_images_to_content(content, image_urls, keyword)
        
        # Step 6: Create post
        status_text.text("💾 Menyimpan post...")
        progress_bar.progress(95)
        
        # Extract excerpt
        excerpt = extract_excerpt_from_content(content)
        
        new_post = {
            "id": post_id,
            "title": title,
            "author": author,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "excerpt": excerpt,
            "content": content,
            "generated_by": "AI",
            "keyword": keyword,
            "language": language
        }
        
        st.session_state.posts.append(new_post)
        
        # Step 7: Complete
        progress_bar.progress(100)
        status_text.text("✅ Post berhasil di-generate!")
        
        st.success("🎉 Post AI berhasil dibuat!")
        st.balloons()
        
        # Show preview
        with st.expander("👁️ Preview Post", expanded=True):
            st.markdown(f"**Judul:** {title}")
            st.markdown(f"**ID:** {post_id}")
            st.markdown(f"**Excerpt:** {excerpt}")
            st.markdown("**Konten:**")
            st.markdown(content[:500] + "..." if len(content) > 500 else content)
        
        gemini.close()
        
    except Exception as e:
        st.error(f"❌ Error saat generate post: {str(e)}")
        progress_bar.empty()
        status_text.empty()

def insert_images_to_content(content, image_urls, keyword):
    """Insert images into content at strategic positions"""
    if not image_urls:
        return content
    
    lines = content.split('\n')
    new_lines = []
    image_index = 0
    
    # Insert images after headings and between sections
    heading_count = 0
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Check if this line is a heading (starts with **)
        if line.strip().startswith('**') and line.strip().endswith(':**'):
            heading_count += 1
            
            # Insert image after every 2nd heading (skip first heading)
            if heading_count > 1 and heading_count % 2 == 0 and image_index < len(image_urls):
                new_lines.append("")  # Empty line
                new_lines.append(f'<img src="{image_urls[image_index]}" alt="{keyword}" style="width: 100%; max-width: 600px; height: auto; border-radius: 8px; margin: 1.5rem 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">')
                new_lines.append(f'<p style="text-align: center; font-size: 0.9rem; color: #666; margin-top: 0.5rem;"><em>{keyword.title()}</em></p>')
                new_lines.append("")  # Empty line
                image_index += 1
    
    return '\n'.join(new_lines)

def manual_post_form():
    """Form untuk membuat post manual"""
    st.subheader("✍️ Buat Post Manual")
    
    # Form untuk post baru
    with st.expander("➕ Tambah Post Baru", expanded=False):
        with st.form("new_post"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Judul Post:")
                author = st.text_input("Penulis:", value="Admin")
            
            with col2:
                post_id = st.text_input("ID Post:", placeholder="contoh: post-1")
                date = st.date_input("Tanggal:", value=datetime.now())
            
            excerpt = st.text_area("Excerpt/Ringkasan:", height=100)
            content = st.text_area("Konten Post:", height=300)
            
            if st.form_submit_button("💾 Simpan Post", use_container_width=True):
                if title and post_id and content:
                    new_post = {
                        "id": post_id,
                        "title": title,
                        "author": author,
                        "date": date.strftime("%Y-%m-%d"),
                        "excerpt": excerpt,
                        "content": content.replace("\n", "<br>")
                    }
                    st.session_state.posts.append(new_post)
                    st.success("✅ Post berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.error("❌ Judul, ID, dan Konten wajib diisi!")

def deploy_page():
    """Halaman untuk deploy worker"""
    st.header("🚀 Deploy Blog")
    
    st.info(f"Worker akan di-deploy ke: **https://{st.session_state.worker_subdomain}**")
    
    # Preview posts
    if st.session_state.posts:
        st.subheader("📋 Preview Posts")
        for post in st.session_state.posts:
            st.markdown(f"• **{post['title']}** (ID: {post['id']})")
        
        st.markdown("---")
        
        if st.button("🚀 Deploy Sekarang", type="primary", use_container_width=True):
            with st.spinner("⏳ Deploying worker..."):
                worker_script = generate_worker_script()
                
                if deploy_worker(worker_script):
                    st.success("✅ Worker berhasil di-deploy!")
                    st.balloons()
                    st.markdown(f"🌍 Blog Anda live di: https://{st.session_state.worker_subdomain}")
                else:
                    st.error("❌ Deploy gagal! Periksa konfigurasi Cloudflare.")
    else:
        st.warning("⚠️ Tidak ada postingan untuk di-deploy. Tambahkan post terlebih dahulu.")

def settings_page():
    """Halaman pengaturan"""
    st.header("⚙️ Pengaturan")
    
    with st.form("settings_form"):
        st.subheader("🔧 Konfigurasi Cloudflare")
        
        new_account_id = st.text_input("Account ID:", value=st.session_state.cf_account_id)
        new_api_token = st.text_input("API Token:", value=st.session_state.cf_api_token, type="password")
        new_worker_name = st.text_input("Worker Name:", value=st.session_state.worker_name)
        
        if st.form_submit_button("💾 Update Konfigurasi"):
            if new_account_id and new_api_token and new_worker_name:
                if test_cloudflare_connection(new_account_id, new_api_token):
                    account_name = get_account_name(new_account_id, new_api_token)
                    if account_name:
                        account_subdomain = format_account_name(account_name)
                        full_worker_url = f"{new_worker_name}.{account_subdomain}.workers.dev"
                        
                        st.session_state.cf_account_id = new_account_id
                        st.session_state.cf_api_token = new_api_token
                        st.session_state.worker_name = new_worker_name
                        st.session_state.worker_subdomain = full_worker_url
                        st.session_state.account_name = account_name
                        st.success("✅ Konfigurasi berhasil diupdate!")
                    else:
                        st.error("❌ Gagal mengambil nama akun.")
                else:
                    st.error("❌ Koneksi ke Cloudflare gagal.")
            else:
                st.error("❌ Semua field harus diisi!")
    
    st.markdown("---")
    
    # Export/Import data
    st.subheader("📤 Export/Import Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export Posts"):
            if st.session_state.posts:
                posts_json = json.dumps(st.session_state.posts, indent=2)
                st.download_button(
                    label="💾 Download posts.json",
                    data=posts_json,
                    file_name="posts.json",
                    mime="application/json"
                )
            else:
                st.warning("Tidak ada posts untuk di-export")
    
    with col2:
        uploaded_file = st.file_uploader("📤 Import Posts", type="json")
        if uploaded_file:
            try:
                imported_posts = json.load(uploaded_file)
                st.session_state.posts = imported_posts
                st.success("✅ Posts berhasil di-import!")
                st.rerun()
            except:
                st.error("❌ File JSON tidak valid!")
    
    st.markdown("---")
    
    # AI Configuration
    st.subheader("🤖 Konfigurasi AI")
    
    with st.form("ai_config_form"):
        gemini_api_key = st.text_input(
            "Gemini API Key:",
            type="password",
            help="Dapatkan dari https://makersuite.google.com/app/apikey"
        )
        
        if st.form_submit_button("💾 Simpan Konfigurasi AI"):
            if gemini_api_key:
                # Save to environment or session state
                os.environ['GEMINI_API_KEY'] = gemini_api_key
                st.success("✅ Konfigurasi AI berhasil disimpan!")
            else:
                st.error("❌ API Key harus diisi!")

# Main app logic
def main():
    init_session_state()
    
    if not st.session_state.authenticated:
        authenticate()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()
