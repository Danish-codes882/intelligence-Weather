/**
 * theme.js — Weather Intelligence Platform
 * GPU-optimized dynamic theme engine.
 * Applies weather-reactive CSS variables without page reload.
 */

const ThemeEngine = (() => {
  // ── Theme Definitions ────────────────────────────────────────────────────
  const THEMES = {
    'extreme-cold': {
      bgStart: '#060d20',
      bgEnd: '#0e1f4a',
      accent: '#60a5fa',
      accentDim: 'rgba(96, 165, 250, 0.15)',
      accentGlow: '0 0 30px rgba(96, 165, 250, 0.25)',
      glassBg: 'rgba(96, 165, 250, 0.05)',
      glassBorder: 'rgba(96, 165, 250, 0.1)',
    },
    'cold': {
      bgStart: '#0a1628',
      bgEnd: '#162944',
      accent: '#93c5fd',
      accentDim: 'rgba(147, 197, 253, 0.12)',
      accentGlow: '0 0 30px rgba(147, 197, 253, 0.2)',
      glassBg: 'rgba(147, 197, 253, 0.04)',
      glassBorder: 'rgba(147, 197, 253, 0.09)',
    },
    'normal': {
      bgStart: '#0a1610',
      bgEnd: '#122416',
      accent: '#4ade80',
      accentDim: 'rgba(74, 222, 128, 0.12)',
      accentGlow: '0 0 30px rgba(74, 222, 128, 0.2)',
      glassBg: 'rgba(74, 222, 128, 0.04)',
      glassBorder: 'rgba(74, 222, 128, 0.09)',
    },
    'warm': {
      bgStart: '#18100a',
      bgEnd: '#2e1a0a',
      accent: '#fb923c',
      accentDim: 'rgba(251, 146, 60, 0.15)',
      accentGlow: '0 0 30px rgba(251, 146, 60, 0.25)',
      glassBg: 'rgba(251, 146, 60, 0.05)',
      glassBorder: 'rgba(251, 146, 60, 0.1)',
    },
    'hot': {
      bgStart: '#200a00',
      bgEnd: '#401500',
      accent: '#f97316',
      accentDim: 'rgba(249, 115, 22, 0.15)',
      accentGlow: '0 0 30px rgba(249, 115, 22, 0.3)',
      glassBg: 'rgba(249, 115, 22, 0.05)',
      glassBorder: 'rgba(249, 115, 22, 0.12)',
    },
    'extreme-hot': {
      bgStart: '#160000',
      bgEnd: '#350000',
      accent: '#ef4444',
      accentDim: 'rgba(239, 68, 68, 0.15)',
      accentGlow: '0 0 40px rgba(239, 68, 68, 0.35)',
      glassBg: 'rgba(239, 68, 68, 0.06)',
      glassBorder: 'rgba(239, 68, 68, 0.12)',
    },
    'rain': {
      bgStart: '#080f1a',
      bgEnd: '#102030',
      accent: '#7dd3fc',
      accentDim: 'rgba(125, 211, 252, 0.12)',
      accentGlow: '0 0 30px rgba(125, 211, 252, 0.2)',
      glassBg: 'rgba(125, 211, 252, 0.04)',
      glassBorder: 'rgba(125, 211, 252, 0.09)',
    },
    'snow': {
      bgStart: '#070d1e',
      bgEnd: '#12203a',
      accent: '#e0f2fe',
      accentDim: 'rgba(224, 242, 254, 0.1)',
      accentGlow: '0 0 30px rgba(224, 242, 254, 0.15)',
      glassBg: 'rgba(224, 242, 254, 0.04)',
      glassBorder: 'rgba(224, 242, 254, 0.09)',
    },
    'storm': {
      bgStart: '#06060f',
      bgEnd: '#10102a',
      accent: '#a78bfa',
      accentDim: 'rgba(167, 139, 250, 0.12)',
      accentGlow: '0 0 30px rgba(167, 139, 250, 0.25)',
      glassBg: 'rgba(167, 139, 250, 0.04)',
      glassBorder: 'rgba(167, 139, 250, 0.09)',
    },
    'fog': {
      bgStart: '#0e0e14',
      bgEnd: '#1a1a24',
      accent: '#9ca3af',
      accentDim: 'rgba(156, 163, 175, 0.1)',
      accentGlow: '0 0 20px rgba(156, 163, 175, 0.15)',
      glassBg: 'rgba(156, 163, 175, 0.04)',
      glassBorder: 'rgba(156, 163, 175, 0.08)',
    },
    'default': {
      bgStart: '#0d0d12',
      bgEnd: '#1a1a2e',
      accent: '#818cf8',
      accentDim: 'rgba(129, 140, 248, 0.15)',
      accentGlow: '0 0 30px rgba(129, 140, 248, 0.25)',
      glassBg: 'rgba(255, 255, 255, 0.04)',
      glassBorder: 'rgba(255, 255, 255, 0.08)',
    },
  };

  let currentThemeKey = 'default';

  // ── Apply Theme ──────────────────────────────────────────────────────────
  function apply(themeKey) {
    if (themeKey === currentThemeKey) return;

    const theme = THEMES[themeKey] || THEMES['default'];
    currentThemeKey = themeKey;

    const root = document.documentElement;

    // Use requestAnimationFrame for GPU optimization
    requestAnimationFrame(() => {
      root.style.setProperty('--theme-bg-start', theme.bgStart);
      root.style.setProperty('--theme-bg-end', theme.bgEnd);
      root.style.setProperty('--accent', theme.accent);
      root.style.setProperty('--accent-dim', theme.accentDim);
      root.style.setProperty('--accent-glow', theme.accentGlow);
      root.style.setProperty('--glass-bg', theme.glassBg);
      root.style.setProperty('--glass-border', theme.glassBorder);

      document.body.setAttribute('data-theme', themeKey);

      // Update body gradient
      document.body.style.backgroundImage =
        `linear-gradient(160deg, ${theme.bgStart} 0%, ${theme.bgEnd} 100%)`;
    });
  }

  function getCurrentKey() { return currentThemeKey; }

  function getThemeFromAPI(themeObj) {
    if (!themeObj || !themeObj.key) return;
    apply(themeObj.key);
  }

  return { apply, getCurrentKey, getThemeFromAPI };
})();

window.ThemeEngine = ThemeEngine;
