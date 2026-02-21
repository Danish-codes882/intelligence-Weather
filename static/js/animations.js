/**
 * animations.js — Weather Intelligence Platform
 * Canvas-based particle systems for weather themes.
 * GPU-optimized with requestAnimationFrame.
 */

const ParticleEngine = (() => {
  let canvas, ctx, animId, particles = [];
  let currentMode = null;
  let lastTime = 0;

  // ── Init ─────────────────────────────────────────────────────────────────
  function init() {
    canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    ctx = canvas.getContext('2d');
    resize();
    window.addEventListener('resize', resize);
  }

  function resize() {
    if (!canvas) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  // ── Set Mode ─────────────────────────────────────────────────────────────
  function setMode(mode) {
    if (mode === currentMode) return;
    currentMode = mode;
    particles = [];
    cancelAnimationFrame(animId);
    if (canvas) ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!mode || mode === 'none') return;

    const builders = {
      snow:      buildSnow,
      rain:      buildRain,
      wind:      buildWind,
      float:     buildFloat,
      glow:      buildGlow,
      shimmer:   buildShimmer,
      heatwave:  buildHeatwave,
      lightning: buildLightning,
    };

    const builder = builders[mode] || buildFloat;
    builder();
    loop(0);
  }

  // ── Particle Loop ─────────────────────────────────────────────────────────
  function loop(ts) {
    if (!ctx) return;
    const dt = Math.min((ts - lastTime) / 16.67, 3); // cap at 3 frames
    lastTime = ts;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles = particles.filter(p => {
      p.update(dt);
      p.draw(ctx);
      return p.alive;
    });

    // Respawn
    if (currentMode === 'snow' && particles.length < 120)  spawnSnow(1);
    if (currentMode === 'rain' && particles.length < 200)  spawnRain(4);
    if (currentMode === 'wind' && particles.length < 60)   spawnWind(1);
    if (currentMode === 'float' && particles.length < 50)  spawnFloat(1);
    if (currentMode === 'glow' && particles.length < 40)   spawnGlow(1);
    if (currentMode === 'shimmer' && particles.length < 30) spawnShimmer(1);
    if (currentMode === 'lightning')                       maybeLightning();

    animId = requestAnimationFrame(loop);
  }

  // ── SNOW ─────────────────────────────────────────────────────────────────
  function buildSnow() {
    for (let i = 0; i < 100; i++) spawnSnow(0);
  }

  function spawnSnow(fromTop = 1) {
    const w = canvas.width, h = canvas.height;
    particles.push({
      x: Math.random() * w,
      y: fromTop ? -10 : Math.random() * h,
      r: Math.random() * 3 + 1,
      vx: Math.random() * 0.8 - 0.4,
      vy: Math.random() * 1.2 + 0.6,
      alpha: Math.random() * 0.5 + 0.3,
      alive: true,
      update(dt) {
        this.x += this.vx * dt + Math.sin(Date.now() * 0.001 + this.y * 0.01) * 0.3;
        this.y += this.vy * dt;
        if (this.y > canvas.height + 10) this.alive = false;
      },
      draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(200, 230, 255, ${this.alpha})`;
        ctx.fill();
      },
    });
  }

  // ── RAIN ─────────────────────────────────────────────────────────────────
  function buildRain() {
    for (let i = 0; i < 180; i++) spawnRain(0);
  }

  function spawnRain(fromTop = 1) {
    const w = canvas.width, h = canvas.height;
    particles.push({
      x: Math.random() * w,
      y: fromTop ? -Math.random() * 50 : Math.random() * h,
      length: Math.random() * 12 + 8,
      speed: Math.random() * 8 + 10,
      alpha: Math.random() * 0.3 + 0.15,
      alive: true,
      update(dt) {
        this.y += this.speed * dt;
        this.x += 1.5 * dt;
        if (this.y > canvas.height + 20) this.alive = false;
      },
      draw(ctx) {
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.lineTo(this.x - 2, this.y + this.length);
        ctx.strokeStyle = `rgba(125, 211, 252, ${this.alpha})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      },
    });
  }

  // ── WIND ─────────────────────────────────────────────────────────────────
  function buildWind() {
    for (let i = 0; i < 40; i++) spawnWind();
  }

  function spawnWind() {
    const h = canvas.height;
    const y = Math.random() * h;
    const len = Math.random() * 120 + 60;
    particles.push({
      x: -len,
      y,
      len,
      speed: Math.random() * 6 + 4,
      alpha: Math.random() * 0.3 + 0.05,
      alive: true,
      update(dt) {
        this.x += this.speed * dt;
        if (this.x > canvas.width + 20) this.alive = false;
      },
      draw(ctx) {
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.lineTo(this.x + this.len, this.y);
        ctx.strokeStyle = `rgba(147, 197, 253, ${this.alpha})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      },
    });
  }

  // ── FLOAT ─────────────────────────────────────────────────────────────────
  function buildFloat() {
    for (let i = 0; i < 40; i++) spawnFloat(0);
  }

  function spawnFloat(fromBottom = 1) {
    const w = canvas.width, h = canvas.height;
    particles.push({
      x: Math.random() * w,
      y: fromBottom ? h + 10 : Math.random() * h,
      r: Math.random() * 2 + 0.5,
      vx: Math.random() * 0.6 - 0.3,
      vy: -(Math.random() * 0.8 + 0.3),
      alpha: 0,
      maxAlpha: Math.random() * 0.4 + 0.1,
      alive: true,
      life: 0,
      maxLife: Math.random() * 200 + 100,
      update(dt) {
        this.life += dt;
        this.x += this.vx * dt;
        this.y += this.vy * dt;
        const progress = this.life / this.maxLife;
        this.alpha = progress < 0.2
          ? this.maxAlpha * (progress / 0.2)
          : this.maxAlpha * (1 - (progress - 0.2) / 0.8);
        if (this.life >= this.maxLife) this.alive = false;
      },
      draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(74, 222, 128, ${this.alpha})`;
        ctx.fill();
      },
    });
  }

  // ── GLOW ─────────────────────────────────────────────────────────────────
  function buildGlow() {
    for (let i = 0; i < 30; i++) spawnGlow();
  }

  function spawnGlow() {
    const w = canvas.width, h = canvas.height;
    const r = Math.random() * 60 + 20;
    particles.push({
      x: Math.random() * w,
      y: Math.random() * h,
      r,
      alpha: 0,
      maxAlpha: Math.random() * 0.08 + 0.03,
      life: 0,
      maxLife: Math.random() * 300 + 150,
      alive: true,
      update(dt) {
        this.life += dt;
        const p = this.life / this.maxLife;
        this.alpha = p < 0.3
          ? this.maxAlpha * (p / 0.3)
          : this.maxAlpha * (1 - (p - 0.3) / 0.7);
        if (this.life >= this.maxLife) this.alive = false;
      },
      draw(ctx) {
        const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.r);
        grad.addColorStop(0, `rgba(251, 146, 60, ${this.alpha})`);
        grad.addColorStop(1, 'rgba(251, 146, 60, 0)');
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
        ctx.fillStyle = grad;
        ctx.fill();
      },
    });
  }

  // ── SHIMMER (Heat) ────────────────────────────────────────────────────────
  function buildShimmer() {
    for (let i = 0; i < 20; i++) spawnShimmer();
  }

  function spawnShimmer() {
    const w = canvas.width;
    const h = canvas.height;
    particles.push({
      x: Math.random() * w,
      y: h * 0.4 + Math.random() * h * 0.5,
      width: Math.random() * 80 + 40,
      height: Math.random() * 60 + 20,
      alpha: 0,
      maxAlpha: Math.random() * 0.04 + 0.01,
      life: 0,
      maxLife: Math.random() * 120 + 80,
      alive: true,
      update(dt) {
        this.life += dt;
        this.y -= 0.3 * dt;
        const p = this.life / this.maxLife;
        this.alpha = p < 0.3
          ? this.maxAlpha * (p / 0.3)
          : this.maxAlpha * (1 - (p - 0.3) / 0.7);
        if (this.life >= this.maxLife) this.alive = false;
      },
      draw(ctx) {
        ctx.save();
        ctx.filter = 'blur(8px)';
        ctx.fillStyle = `rgba(249, 115, 22, ${this.alpha})`;
        ctx.fillRect(this.x - this.width / 2, this.y - this.height / 2, this.width, this.height);
        ctx.restore();
      },
    });
  }

  // ── HEATWAVE ──────────────────────────────────────────────────────────────
  function buildHeatwave() {
    // Heatwave uses shimmer + additional distortion lines
    buildShimmer();
    spawnHeatLines();
  }

  function spawnHeatLines() {
    for (let i = 0; i < 8; i++) {
      const w = canvas.width, h = canvas.height;
      particles.push({
        x: 0,
        y: h * 0.6 + Math.random() * h * 0.3,
        width: w,
        alpha: 0,
        maxAlpha: 0.06,
        life: 0,
        maxLife: Math.random() * 80 + 40,
        alive: true,
        update(dt) {
          this.life += dt;
          const p = this.life / this.maxLife;
          this.alpha = Math.sin(p * Math.PI) * this.maxAlpha;
          if (this.life >= this.maxLife) this.alive = false;
        },
        draw(ctx) {
          const grad = ctx.createLinearGradient(0, this.y, 0, this.y + 4);
          grad.addColorStop(0, `rgba(239, 68, 68, 0)`);
          grad.addColorStop(0.5, `rgba(239, 68, 68, ${this.alpha})`);
          grad.addColorStop(1, `rgba(239, 68, 68, 0)`);
          ctx.fillStyle = grad;
          ctx.fillRect(0, this.y, this.width, 4);
        },
      });
    }
  }

  // ── LIGHTNING ─────────────────────────────────────────────────────────────
  function buildLightning() {
    // Lightning flashes are triggered probabilistically
  }

  let lastLightning = 0;
  function maybeLightning() {
    const now = Date.now();
    if (now - lastLightning > Math.random() * 5000 + 3000) {
      lastLightning = now;
      spawnLightningFlash();
    }
  }

  function spawnLightningFlash() {
    const w = canvas.width;
    const x = Math.random() * w;
    particles.push({
      x,
      life: 0,
      maxLife: 8,
      alive: true,
      update(dt) {
        this.life += dt;
        if (this.life >= this.maxLife) this.alive = false;
      },
      draw(ctx) {
        const p = this.life / this.maxLife;
        const alpha = p < 0.3 ? p / 0.3 : p < 0.6 ? 1 : 1 - (p - 0.6) / 0.4;
        ctx.fillStyle = `rgba(167, 139, 250, ${alpha * 0.15})`;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      },
    });
  }

  // ── Public API ────────────────────────────────────────────────────────────
  const PARTICLE_MAP = {
    'snow': 'snow',
    'rain': 'rain',
    'wind': 'wind',
    'float': 'float',
    'glow': 'glow',
    'shimmer': 'shimmer',
    'heatwave': 'heatwave',
    'lightning': 'lightning',
    'none': null,
  };

  function applyFromTheme(themeKey) {
    const modes = {
      'extreme-cold': 'snow',
      'cold': 'wind',
      'normal': 'float',
      'warm': 'glow',
      'hot': 'shimmer',
      'extreme-hot': 'heatwave',
      'rain': 'rain',
      'snow': 'snow',
      'storm': 'lightning',
      'fog': 'float',
      'default': 'float',
    };
    setMode(modes[themeKey] || 'float');
  }

  return { init, setMode, applyFromTheme };
})();

// Init on DOM ready
document.addEventListener('DOMContentLoaded', () => ParticleEngine.init());
window.ParticleEngine = ParticleEngine;
