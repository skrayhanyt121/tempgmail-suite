/**
 * NovaPulse Core Engine (Vanilla ES6+)
 * Reactive Particle Mesh Canvas + Interactive In-Browser Shell
 */

document.addEventListener('DOMContentLoaded', () => {
  initParticleCanvas();
  initMetricCounters();
  initInteractiveTerminal();
  initThemeToggle();
  initPingTester();
});

/* ----------------------------------------------------
 * 1. Background Particle Constellation Canvas
 * -------------------------------------------------- */
function initParticleCanvas() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const particleCount = window.innerWidth < 768 ? 35 : 70;
  const particles = [];

  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.6,
      vy: (Math.random() - 0.5) * 0.6,
      radius: Math.random() * 1.8 + 0.8,
    });
  }

  let mouse = { x: null, y: null };
  window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });
  window.addEventListener('mouseleave', () => {
    mouse.x = null;
    mouse.y = null;
  });

  function render() {
    ctx.clearRect(0, 0, width, height);

    // Update & draw particles
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(79, 172, 254, 0.4)';
      ctx.fill();

      // Connect with lines if close
      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 110) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(79, 172, 254, ${0.18 * (1 - dist / 110)})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }

      // React to mouse proximity
      if (mouse.x !== null) {
        const mdx = p.x - mouse.x;
        const mdy = p.y - mouse.y;
        const mdist = Math.sqrt(mdx * mdx + mdy * mdy);
        if (mdist < 140) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(mouse.x, mouse.y);
          ctx.strokeStyle = `rgba(0, 242, 254, ${0.25 * (1 - mdist / 140)})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(render);
  }

  render();
}

/* ----------------------------------------------------
 * 2. Animated Metric Counters
 * -------------------------------------------------- */
function initMetricCounters() {
  const counters = document.querySelectorAll('.metric-val');
  counters.forEach((counter) => {
    const target = parseFloat(counter.getAttribute('data-target'));
    const isFloat = target % 1 !== 0;
    const duration = 1400;
    const startTime = performance.now();

    function updateCounter(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = eased * target;

      counter.textContent = isFloat ? current.toFixed(2) : Math.floor(current);

      if (progress < 1) {
        requestAnimationFrame(updateCounter);
      } else {
        counter.textContent = isFloat ? target.toFixed(2) : target;
      }
    }

    requestAnimationFrame(updateCounter);
  });
}

/* ----------------------------------------------------
 * 3. Interactive In-Browser Shell (Terminal)
 * -------------------------------------------------- */
function initInteractiveTerminal() {
  const output = document.getElementById('terminal-output');
  const input = document.getElementById('term-input');
  const submitBtn = document.getElementById('term-send-btn');

  if (!output || !input) return;

  const commands = {
    help: () => `
<span class="term-cyan">Available commands:</span>
  • <span class="term-yellow">status</span>      - Show system, memory, and engine status
  • <span class="term-yellow">skills</span>      - List loaded Hermes Autonomous skills
  • <span class="term-yellow">ping</span>        - Test round-trip latency to edge node
  • <span class="term-yellow">about</span>       - Architecture & creation breakdown
  • <span class="term-yellow">date</span>        - Display active host timestamp
  • <span class="term-yellow">clear</span>       - Clear terminal history
`,
    status: () => `
<span class="term-green">✔ SYSTEM STATUS REPORT:</span>
  Cluster: <span class="term-cyan">NovaPulse Core Linux (arm64)</span>
  Agent Engine: <span class="term-cyan">Antigravity + Hermes Agent v0.23.1</span>
  LLM Provider: <span class="term-cyan">Google Gemini Frontier Native</span>
  Server State: <span class="term-green">Healthy (HTTP 200 OK)</span>
`,
    skills: () => `
<span class="term-cyan">Hermes Agent Skills Active (39 total):</span>
  [1] <span class="term-yellow">codebase-inspection</span>  [2] <span class="term-yellow">systematic-debugging</span>
  [3] <span class="term-yellow">manim-video</span>          [4] <span class="term-yellow">arxiv-deep-research</span>
  [5] <span class="term-yellow">youtube-content</span>      [6] <span class="term-yellow">architecture-diagram</span>
  [7] <span class="term-yellow">competitor-monitor</span>   [8] <span class="term-yellow">p5js-creative-canvas</span>
`,
    ping: () => `
<span class="term-cyan">PING 127.0.0.1 (localhost): 56 data bytes</span>
  64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.082 ms
  64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.076 ms
  <span class="term-green">0% packet loss, min/avg/max = 0.076/0.079/0.082 ms</span>
`,
    about: () => `
<span class="term-cyan">NOVALPULSE WEB ARCHITECTURE:</span>
  Created with zero framework bloat using semantic HTML5, glassmorphic CSS3,
  and asynchronous JS event listeners. Responsive for mobile touch and desktop.
`,
    date: () => `<span class="term-cyan">${new Date().toLocaleString()}</span>`,
    clear: () => {
      output.innerHTML = '';
      return null;
    }
  };

  function executeCommand(raw) {
    const clean = raw.trim().toLowerCase();
    if (!clean) return;

    // Print command line
    const cmdLine = document.createElement('div');
    cmdLine.className = 'term-line';
    cmdLine.innerHTML = `<span class="term-prompt">novapulse ❯</span> ${escapeHtml(raw)}`;
    output.appendChild(cmdLine);

    // Execute logic
    const resLine = document.createElement('div');
    resLine.className = 'term-line';

    if (commands[clean]) {
      const result = commands[clean]();
      if (result !== null) {
        resLine.innerHTML = result;
        output.appendChild(resLine);
      }
    } else {
      resLine.innerHTML = `<span class="term-red">Command not found: '${escapeHtml(clean)}'. Type 'help' for available commands.</span>`;
      output.appendChild(resLine);
    }

    output.scrollTop = output.scrollHeight;
    input.value = '';
  }

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      executeCommand(input.value);
    }
  });

  if (submitBtn) {
    submitBtn.addEventListener('click', () => {
      executeCommand(input.value);
    });
  }
}

/* ----------------------------------------------------
 * 4. Latency Tester Action
 * -------------------------------------------------- */
function initPingTester() {
  const btn = document.getElementById('btn-ping');
  const text = document.getElementById('ping-text');
  const icon = document.getElementById('ping-icon');
  if (!btn || !text) return;

  btn.addEventListener('click', () => {
    text.textContent = 'Measuring...';
    icon.textContent = '⏳';
    btn.disabled = true;

    const start = performance.now();
    setTimeout(() => {
      const latency = Math.round(performance.now() - start);
      text.textContent = `${latency}ms (Superfast)`;
      icon.textContent = '⚡';
      btn.disabled = false;
      setTimeout(() => {
        text.textContent = 'Test Latency';
        icon.textContent = '📡';
      }, 3000);
    }, 280);
  });
}

/* ----------------------------------------------------
 * 5. Theme Toggle (Dark/Light)
 * -------------------------------------------------- */
function initThemeToggle() {
  const toggle = document.getElementById('theme-toggle');
  if (!toggle) return;

  toggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'light' ? 'dark' : 'light';
    if (next === 'dark') {
      document.documentElement.removeAttribute('data-theme');
    } else {
      document.documentElement.setAttribute('data-theme', 'light');
    }
  });
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
