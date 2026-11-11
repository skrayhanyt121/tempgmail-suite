// Nexus AI Studio - 2026 Logic
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    lucide.createIcons();

    // DOM Elements
    const generateBtn = document.getElementById('generateBtn');
    const promptInput = document.getElementById('promptInput');
    const galleryGrid = document.getElementById('galleryGrid');
    const styleChips = document.querySelectorAll('.style-chip');
    const workbench = document.querySelector('.workbench');

    // State
    let selectedStyle = 'cinematic';
    const mockData = [
        { id: 1, prompt: "Neon cyberpunk city in rain", url: "https://images.unsplash.com/photo-1614728263952-84ea206f99b6?auto=format&fit=crop&q=80&w=800" },
        { id: 2, prompt: "Surreal desert landscape with floating rocks", url: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=800" },
        { id: 3, prompt: "Hyper-realistic portrait of a cyborg", url: "https://images.unsplash.com/photo-1589254065878-42c9da997008?auto=format&fit=crop&q=80&w=800" },
        { id: 4, prompt: "Abstract 3D architectural flows", url: "https://images.unsplash.com/photo-1633167606207-d840b5070fc2?auto=format&fit=crop&q=80&w=800" }
    ];

    // Functions
    const initGallery = () => {
        mockData.forEach(item => addGalleryItem(item));
    };

    const addGalleryItem = (item) => {
        const div = document.createElement('div');
        div.className = 'gallery-item';
        div.innerHTML = `
            <img src="${item.url}" alt="${item.prompt}">
            <div class="item-overlay">
                <p class="overlay-text">${item.prompt}</p>
            </div>
        `;
        galleryGrid.prepend(div);
    };

    const handleGenerate = async () => {
        const prompt = promptInput.value.trim();
        if (!prompt) {
            alert('Please enter a prompt');
            return;
        }

        // Update UI to "Generating"
        generateBtn.disabled = true;
        generateBtn.innerHTML = `<span>Synthesizing...</span> <div class="spinner"></div>`;
        workbench.classList.add('generating');

        // Simulate AI processing delay
        await new Promise(resolve => setTimeout(resolve, 3000));

        // Create new item (using random image for demo)
        const newItem = {
            id: Date.now(),
            prompt: prompt,
            url: `https://picsum.photos/seed/${Math.random()}/800/500`
        };

        addGalleryItem(newItem);

        // Reset UI
        generateBtn.disabled = false;
        generateBtn.innerHTML = `<span>Generate</span> <i data-lucide="zap"></i>`;
        workbench.classList.remove('generating');
        promptInput.value = '';
        lucide.createIcons();
    };

    // Event Listeners
    generateBtn.addEventListener('click', handleGenerate);

    styleChips.forEach(chip => {
        chip.addEventListener('click', () => {
            styleChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            selectedStyle = chip.dataset.style;
        });
    });

    // Handle Enter to generate
    promptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            handleGenerate();
        }
    });

    // Add spinner style to document
    const style = document.createElement('style');
    style.textContent = `
        .spinner {
            width: 16px;
            height: 16px;
            border: 2px solid rgba(0,0,0,0.1);
            border-top: 2px solid #000;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);

    // Bootstrap
    initGallery();
});
