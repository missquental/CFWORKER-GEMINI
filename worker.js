// Template Cloudflare Worker untuk Blog dengan Layout WordPress Style
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

// Sample posts - akan diganti dengan data dari Streamlit
const posts = [
  {
    id: "welcome",
    title: "Selamat Datang di Blog Saya",
    author: "Admin",
    date: "2024-01-15",
    excerpt: "Ini adalah post pertama di blog yang dibuat dengan Cloudflare Worker.",
    content: "Selamat datang di blog saya! <br><br>Blog ini dibuat menggunakan Cloudflare Worker dan dikelola melalui dashboard Streamlit. Anda dapat menambahkan, mengedit, dan menghapus postingan dengan mudah melalui interface yang user-friendly.<br><br>Fitur-fitur yang tersedia:<br>• 📝 Manajemen postingan yang mudah<br>• 🚀 Deploy otomatis ke Cloudflare Worker<br>• 📱 Responsive design<br>• ⚡ Loading yang cepat<br><br>Terima kasih telah mengunjungi blog saya!",
    category: "Umum",
    tags: ["welcome", "blog", "cloudflare"]
  },
  {
    id: "tutorial-cloudflare",
    title: "Tutorial Menggunakan Cloudflare Worker",
    author: "Admin", 
    date: "2024-01-16",
    excerpt: "Pelajari cara menggunakan Cloudflare Worker untuk membuat aplikasi web yang cepat dan scalable.",
    content: "Cloudflare Worker adalah platform serverless yang memungkinkan Anda menjalankan JavaScript di edge network Cloudflare.<br><br><strong>Keuntungan Cloudflare Worker:</strong><br>• ⚡ Latency rendah karena berjalan di edge<br>• 🌍 Global distribution<br>• 💰 Pricing yang terjangkau<br>• 🔧 Easy deployment<br><br><strong>Use Cases:</strong><br>• API endpoints<br>• Static site hosting<br>• Edge computing<br>• Request/response manipulation<br><br>Dengan kombinasi Cloudflare Worker dan Streamlit dashboard, Anda dapat membuat dan mengelola blog dengan mudah tanpa perlu server tradisional.",
    category: "Tutorial",
    tags: ["cloudflare", "worker", "tutorial"]
  }
];

// Konfigurasi blog
const BLOG_CONFIG = {
  title: "My Blog",
  subtitle: "Berbagi pemikiran dan pengalaman",
  description: "Blog pribadi yang membahas teknologi, tutorial, dan pengalaman sehari-hari",
  author: "Admin",
  social: {
    facebook: "https://facebook.com/yourusername",
    twitter: "https://twitter.com/yourusername",
    instagram: "https://instagram.com/yourusername",
    linkedin: "https://linkedin.com/in/yourusername"
  }
};

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
        
        .post-content img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 1rem 0;
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

            <!-- Sidebar -->
            <aside class="sidebar">
                <!-- Search Widget -->
                <div class="widget">
                    <h3>🔍 Pencarian</h3>
                    <div class="search-box">
                        <input type="text" placeholder="Cari artikel...">
                        <button type="submit">Cari</button>
                    </div>
                </div>

                <!-- Ad Space Sidebar -->
                <div class="widget">
                    <div class="ad-space ad-sidebar">
                        <div>
                            <h4>📢 Ruang Iklan</h4>
                            <p>300x250 pixels</p>
                            <small>Sidebar Advertisement</small>
                        </div>
                    </div>
                </div>

                <!-- Recent Posts Widget -->
                <div class="widget">
                    <h3>📚 Artikel Terbaru</h3>
                    <ul>
                        ${posts.slice(0, 5).map(post => `
                            <li><a href="/post/${post.id}">${post.title}</a></li>
                        `).join('')}
                    </ul>
                </div>

                <!-- Categories Widget -->
                <div class="widget">
                    <h3>📂 Kategori</h3>
                    <ul>
                        <li><a href="/category/tutorial">Tutorial (${posts.filter(p => p.category === 'Tutorial').length})</a></li>
                        <li><a href="/category/teknologi">Teknologi (${posts.filter(p => p.category === 'Teknologi').length})</a></li>
                        <li><a href="/category/umum">Umum (${posts.filter(p => p.category === 'Umum').length})</a></li>
                    </ul>
                </div>

                <!-- Tags Widget -->
                <div class="widget">
                    <h3>🏷️ Tags Populer</h3>
                    <div class="tags">
                        <a href="/tag/cloudflare" class="tag">cloudflare</a>
                        <a href="/tag/tutorial" class="tag">tutorial</a>
                        <a href="/tag/javascript" class="tag">javascript</a>
                        <a href="/tag/blog" class="tag">blog</a>
                        <a href="/tag/web" class="tag">web</a>
                    </div>
                </div>

                <!-- Social Media Widget -->
                <div class="widget">
                    <h3>🌐 Ikuti Kami</h3>
                    <div class="social-share">
                        <a href="${BLOG_CONFIG.social.facebook}" target="_blank">📘 Facebook</a>
                        <a href="${BLOG_CONFIG.social.twitter}" target="_blank">🐦 Twitter</a>
                        <a href="${BLOG_CONFIG.social.instagram}" target="_blank">📷 Instagram</a>
                    </div>
                </div>

                <!-- Newsletter Widget -->
                <div class="widget">
                    <h3>📧 Newsletter</h3>
                    <p>Dapatkan update artikel terbaru langsung ke email Anda!</p>
                    <div class="search-box">
                        <input type="email" placeholder="Email Anda...">
                        <button type="submit">Subscribe</button>
                    </div>
                </div>
            </aside>
        </div>
    </div>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>Tentang Blog</h3>
                    <p>${BLOG_CONFIG.description}</p>
                    <p>Dibuat dengan ❤️ menggunakan Cloudflare Worker dan Streamlit.</p>
                </div>
                <div class="footer-section">
                    <h3>Link Cepat</h3>
                    <ul style="list-style: none;">
                        <li><a href="/">Beranda</a></li>
                        <li><a href="/about">Tentang Kami</a></li>
                        <li><a href="/contact">Kontak</a></li>
                        <li><a href="/privacy">Kebijakan Privasi</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3>Kontak</h3>
                    <p>📧 Email: admin@bloganda.com</p>
                    <p>📱 WhatsApp: +62 812-3456-7890</p>
                    <p>🌍 Website: https://bloganda.com</p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2024 ${BLOG_CONFIG.title}. Semua hak dilindungi. | Powered by Cloudflare Worker</p>
            </div>
        </div>
    </footer>
</body>
</html>
`;

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

  return HTML_TEMPLATE
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
