/**
 * LUMINA AI Creative Engine (Frontend Client)
 * High-agency reactive architecture with simulated synthesis pipeline
 */

document.addEventListener('DOMContentLoaded', () => {
  initRadialSpotlight();
  initPromptWorkbench();
  initSynthesisEngine();
  initCommunityGallery();
  initModalViewer();
});

/* --------------------------------------------------------------------------
 * 1. Ambient Radial Spotlight (Tracks touch and mouse)
 * -------------------------------------------------------------------------- */
function initRadialSpotlight() {
  const glow = document.getElementById('mouse-glow');
  if (!glow) return;

  window.addEventListener('mousemove', (e) => {
    glow.style.left = `${e.clientX}px`;
    glow.style.top = `${e.clientY}px`;
  });

  window.addEventListener('touchmove', (e) => {
    if (e.touches.length > 0) {
      glow.style.left = `${e.touches[0].clientX}px`;
      glow.style.top = `${e.touches[0].clientY}px`;
    }
  }, { passive: true });
}

/* --------------------------------------------------------------------------
 * 2. Prompt Workbench & Enhancer
 * -------------------------------------------------------------------------- */
let activeStyle = 'Cinematic 8K';
let activeRatio = '16:9';
let currentCredits = 250;

function initPromptWorkbench() {
  const promptInput = document.getElementById('prompt-input');
  const magicBtn = document.getElementById('btn-magic-enhance');
  const styleContainer = document.getElementById('style-chips-container');
  const ratioSelector = document.getElementById('ratio-selector');

  // Magic Prompt Enhancer
  const enhancementModifiers = [
    'cinematic volumetric fog, 35mm anamorphic lens, chromatic aberration, ray-traced reflections, 8k resolution, photorealistic masterpiece',
    'global illumination, subsurface scattering, Octane render 2026, hyper-detailed texture, award-winning shot',
    'golden hour rim light, atmospheric dust particles, shallow depth of field, Hasselblad medium format shot',
    'cyberpunk neon highlights, moody rain atmosphere, Blade Runner 2049 aesthetic, ultra-sharp focus'
  ];

  magicBtn.addEventListener('click', () => {
    const current = promptInput.value.trim();
    if (!current) {
      showToast('⚠️ Please write an initial idea first!');
      return;
    }
    const randomMod = enhancementModifiers[Math.floor(Math.random() * enhancementModifiers.length)];
    if (!current.includes(randomMod)) {
      promptInput.value = `${current}, ${randomMod}`;
      showToast('✨ Prompt Enhanced with Cinematic Attributes!');
    }
  });

  // Style Chips Click
  styleContainer.addEventListener('click', (e) => {
    const chip = e.target.closest('.style-chip');
    if (!chip) return;

    styleContainer.querySelectorAll('.style-chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    activeStyle = chip.getAttribute('data-style');
    showToast(`Style set to: ${activeStyle}`);
  });

  // Aspect Ratio Selection
  ratioSelector.addEventListener('click', (e) => {
    const btn = e.target.closest('.ratio-btn');
    if (!btn) return;

    ratioSelector.querySelectorAll('.ratio-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeRatio = btn.getAttribute('data-ratio');
    showToast(`Aspect ratio: ${activeRatio}`);
  });
}

/* --------------------------------------------------------------------------
 * 3. Synthesis Engine (Interactive Generation Pipeline)
 * -------------------------------------------------------------------------- */
function initSynthesisEngine() {
  const generateBtn = document.getElementById('btn-generate');
  const stageIdle = document.getElementById('stage-idle');
  const stageLoading = document.getElementById('stage-loading');
  const stageResult = document.getElementById('stage-result');
  
  const loadingStatusText = document.getElementById('loading-status-text');
  const progressFill = document.getElementById('progress-fill');
  const progressPercent = document.getElementById('progress-percent');
  
  const resultImg = document.getElementById('result-img');
  const resultBadgeStyle = document.getElementById('res-badge-style');
  const resultPromptText = document.getElementById('result-prompt-text');
  const creditsDisplay = document.getElementById('user-credits');

  const btnCopy = document.getElementById('btn-copy-prompt');
  const btnDownload = document.getElementById('btn-download');
  const btnFullscreen = document.getElementById('btn-fullscreen');

  // Curated High-End Visuals for Realistic Demo Render
  const aestheticRenders = {
    'Cinematic 8K': [
      'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1200&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&w=1200&auto=format&fit=crop'
    ],
    'Cyberpunk Neon': [
      'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=1200&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1578632767115-351597cf2477?q=80&w=1200&auto=format&fit=crop'
    ],
    'Studio Anime': [
      'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?q=80&w=1200&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1563089145-599997674d42?q=80&w=1200&auto=format&fit=crop'
    ],
    'Hyper Portrait': [
      'https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=1200&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1200&auto=format&fit=crop'
    ],
    'Surreal Sci-Fi': [
      'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1200&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?q=80&w=1200&auto=format&fit=crop'
    ],
    '3D Unreal 5': [
      'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1200&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?q=80&w=1200&auto=format&fit=crop'
    ]
  };

  const statusPhases = [
    { at: 15, text: 'Parsing semantic token embeddings...' },
    { at: 40, text: 'Synthesizing multi-scale latent diffusion grid...' },
    { at: 75, text: 'Refining ray-traced reflections & lighting...' },
    { at: 92, text: 'Applying 35mm anamorphic color grading...' },
    { at: 100, text: 'Scene generated successfully!' }
  ];

  generateBtn.addEventListener('click', () => {
    const prompt = document.getElementById('prompt-input').value.trim();
    if (!prompt) {
      showToast('⚠️ Please provide a prompt description.');
      return;
    }

    if (currentCredits < 5) {
      showToast('❌ Insufficient credits remaining!');
      return;
    }

    // Deduct credits
    currentCredits -= 5;
    creditsDisplay.textContent = currentCredits;

    // Switch UI states
    stageIdle.classList.add('hidden');
    stageResult.classList.add('hidden');
    stageLoading.classList.remove('hidden');

    // Smooth scroll to preview stage
    document.getElementById('stage-section').scrollIntoView({ behavior: 'smooth', block: 'center' });

    let progress = 0;
    progressFill.style.width = '0%';
    progressPercent.textContent = '0%';

    const interval = setInterval(() => {
      progress += Math.floor(Math.random() * 8) + 4;
      if (progress > 100) progress = 100;

      progressFill.style.width = `${progress}%`;
      progressPercent.textContent = `${progress}%`;

      // Update status phase
      const currentPhase = statusPhases.find(p => progress <= p.at) || statusPhases[statusPhases.length - 1];
      loadingStatusText.textContent = currentPhase.text;

      if (progress >= 100) {
        clearInterval(interval);
        setTimeout(() => {
          // Reveal result
          const pool = aestheticRenders[activeStyle] || aestheticRenders['Cinematic 8K'];
          const chosenImage = pool[Math.floor(Math.random() * pool.length)];

          resultImg.src = chosenImage;
          resultBadgeStyle.textContent = activeStyle;
          resultPromptText.textContent = prompt;

          stageLoading.classList.add('hidden');
          stageResult.classList.remove('hidden');
          showToast('🎉 Scene generation completed!');
        }, 300);
      }
    }, 120);
  });

  // Action Buttons
  btnCopy.addEventListener('click', () => {
    navigator.clipboard.writeText(resultPromptText.textContent).then(() => {
      showToast('📋 Prompt copied to clipboard!');
    });
  });

  btnDownload.addEventListener('click', () => {
    showToast('⬇ Preparing 4K high-resolution render download...');
    window.open(resultImg.src, '_blank');
  });

  btnFullscreen.addEventListener('click', () => {
    openModal(resultImg.src, resultPromptText.textContent, `${activeStyle} • ${activeRatio} • Flux 1.1 Pro`);
  });
}

/* --------------------------------------------------------------------------
 * 4. Trending Community Discovery Stream
 * -------------------------------------------------------------------------- */
const galleryItems = [
  {
    id: 1,
    title: 'Neon Ronin In Rain',
    prompt: 'Futuristic cyberpunk cyborg swordsman standing in rain-slicked alleyway, neon signage, volumetric purple backlighting, 8k',
    category: 'cyberpunk',
    style: 'Cyberpunk Neon',
    ratio: '16:9',
    likes: 1420,
    img: 'https://images.unsplash.com/photo-1578632767115-351597cf2477?q=80&w=800&auto=format&fit=crop'
  },
  {
    id: 2,
    title: 'Interstellar Nebula Gate',
    prompt: 'Cosmic celestial vortex gate emitting golden light over dark orbital ring, high-detail planetary dust, IMAX 70mm shot',
    category: 'cinematic',
    style: 'Cinematic 8K',
    ratio: '16:9',
    likes: 2890,
    img: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=800&auto=format&fit=crop'
  },
  {
    id: 3,
    title: 'Cherry Blossom Shrine Guardian',
    prompt: 'Anime spirit girl with luminous red kitsune mask under ethereal sakura trees, Studio Ghibli meets Makoto Shinkai aesthetic',
    category: 'anime',
    style: 'Studio Anime',
    ratio: '16:9',
    likes: 3120,
    img: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?q=80&w=800&auto=format&fit=crop'
  },
  {
    id: 4,
    title: 'Bionic Muse Portrait',
    prompt: 'Macro beauty portrait of female android with translucent ceramic skin, gold wiring micro-circuits, shallow depth of field',
    category: 'portrait',
    style: 'Hyper Portrait',
    ratio: '1:1',
    likes: 1845,
    img: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=800&auto=format&fit=crop'
  },
  {
    id: 5,
    title: 'Dune Sovereign Citadel',
    prompt: 'Brutalist monolith palace rising over endless desert dunes, dual suns, atmospheric dust haze, cinematic cinematography',
    category: 'cinematic',
    style: 'Cinematic 8K',
    ratio: '16:9',
    likes: 980,
    img: 'https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?q=80&w=800&auto=format&fit=crop'
  },
  {
    id: 6,
    title: 'Tokyo Synthesized Speed',
    prompt: 'High-speed motion blur through Shibuya crossing with hovering red laser trails, cyberpunk 2077 night lighting, anamorphic flare',
    category: 'cyberpunk',
    style: 'Cyberpunk Neon',
    ratio: '16:9',
    likes: 2410,
    img: 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=800&auto=format&fit=crop'
  }
];

function initCommunityGallery() {
  const container = document.getElementById('gallery-grid');
  const filtersContainer = document.getElementById('feed-filters');

  function renderGallery(filter = 'all') {
    container.innerHTML = '';
    const filtered = filter === 'all' ? galleryItems : galleryItems.filter(item => item.category === filter);

    filtered.forEach(item => {
      const card = document.createElement('div');
      card.className = 'gallery-card';
      card.innerHTML = `
        <div class="card-thumb-wrapper" data-img="${item.img}" data-prompt="${escapeHtml(item.prompt)}" data-meta="${item.style} • ${item.ratio}">
          <img src="${item.img}" alt="${item.title}" class="card-thumb" loading="lazy">
          <span class="card-chip">${item.style}</span>
        </div>
        <div class="card-info">
          <p class="card-prompt">${escapeHtml(item.prompt)}</p>
          <div class="card-footer">
            <div class="card-likes" data-id="${item.id}">
              <span class="heart-icon">🤍</span>
              <span class="likes-count">${item.likes}</span>
            </div>
            <button class="card-btn-use" data-prompt="${escapeHtml(item.prompt)}" data-style="${item.style}">
              Use Prompt ↗
            </button>
          </div>
        </div>
      `;
      container.appendChild(card);
    });
  }

  // Filter Buttons Click
  filtersContainer.addEventListener('click', (e) => {
    const btn = e.target.closest('.filter-btn');
    if (!btn) return;
    filtersContainer.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderGallery(btn.getAttribute('data-filter'));
  });

  // Delegate clicks on cards
  container.addEventListener('click', (e) => {
    // Like button
    const likeBtn = e.target.closest('.card-likes');
    if (likeBtn) {
      const icon = likeBtn.querySelector('.heart-icon');
      const count = likeBtn.querySelector('.likes-count');
      if (icon.textContent === '🤍') {
        icon.textContent = '❤️';
        count.textContent = parseInt(count.textContent) + 1;
        showToast('❤️ Added to your liked collection');
      } else {
        icon.textContent = '🤍';
        count.textContent = parseInt(count.textContent) - 1;
      }
      return;
    }

    // Use prompt button
    const useBtn = e.target.closest('.card-btn-use');
    if (useBtn) {
      const prompt = useBtn.getAttribute('data-prompt');
      const style = useBtn.getAttribute('data-style');
      
      const promptInput = document.getElementById('prompt-input');
      promptInput.value = prompt;

      // Select matching style chip if exists
      const matchingChip = document.querySelector(`.style-chip[data-style="${style}"]`);
      if (matchingChip) {
        matchingChip.click();
      }

      window.scrollTo({ top: 120, behavior: 'smooth' });
      showToast('📥 Prompt loaded into Workbench!');
      return;
    }

    // Click image thumbnail -> Open Modal
    const thumbWrapper = e.target.closest('.card-thumb-wrapper');
    if (thumbWrapper) {
      const img = thumbWrapper.getAttribute('data-img');
      const prompt = thumbWrapper.getAttribute('data-prompt');
      const meta = thumbWrapper.getAttribute('data-meta');
      openModal(img, prompt, meta);
    }
  });

  renderGallery('all');
}

/* --------------------------------------------------------------------------
 * 5. Fullscreen Modal Viewer
 * -------------------------------------------------------------------------- */
function initModalViewer() {
  const modal = document.getElementById('modal-viewer');
  const closeBtn = document.getElementById('modal-close');

  closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.add('hidden');
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') modal.classList.add('hidden');
  });
}

function openModal(imgSrc, promptText, metaText) {
  const modal = document.getElementById('modal-viewer');
  document.getElementById('modal-img').src = imgSrc;
  document.getElementById('modal-prompt').textContent = promptText;
  document.getElementById('modal-meta').textContent = metaText;
  modal.classList.remove('hidden');
}

/* --------------------------------------------------------------------------
 * Toast Notification Utility
 * -------------------------------------------------------------------------- */
let toastTimeout;
function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.remove('hidden');
  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    toast.classList.add('hidden');
  }, 2600);
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
