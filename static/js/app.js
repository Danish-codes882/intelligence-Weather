/**
 * app.js — Weather Intelligence Platform
 * Main frontend application: search, data rendering, charts, UI state.
 */

'use strict';

// ── SVG Icon System ──────────────────────────────────────────────────────────
const WEATHER_ICONS = {
  sunny: `<svg class="weather-icon-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="32" cy="32" r="12" fill="#FCD34D"/>
    <g stroke="#FCD34D" stroke-width="2.5" stroke-linecap="round">
      <line x1="32" y1="4" x2="32" y2="12"/>
      <line x1="32" y1="52" x2="32" y2="60"/>
      <line x1="4" y1="32" x2="12" y2="32"/>
      <line x1="52" y1="32" x2="60" y2="32"/>
      <line x1="11.5" y1="11.5" x2="17.2" y2="17.2"/>
      <line x1="46.8" y1="46.8" x2="52.5" y2="52.5"/>
      <line x1="52.5" y1="11.5" x2="46.8" y2="17.2"/>
      <line x1="17.2" y1="46.8" x2="11.5" y2="52.5"/>
    </g>
  </svg>`,
  'clear-night': `<svg class="weather-icon-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M36 10C28 14 22 22 22 32C22 44 32 54 44 54C47 54 50 53 52 52C44 58 32 58 22 52C12 46 8 34 14 22C18 14 26 8 36 10Z" fill="#C7D2FE"/>
    <circle cx="50" cy="14" r="2" fill="#C7D2FE" opacity="0.6"/>
    <circle cx="44" cy="6" r="1.5" fill="#C7D2FE" opacity="0.4"/>
    <circle cx="58" cy="20" r="1.5" fill="#C7D2FE" opacity="0.4"/>
  </svg>`,
  'partly-cloudy': `<svg class="weather-icon-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="24" cy="26" r="9" fill="#FCD34D" opacity="0.9"/>
    <ellipse cx="36" cy="38" rx="14" ry="10" fill="#94A3B8"/>
    <ellipse cx="26" cy="40" rx="10" ry="8" fill="#CBD5E1"/>
    <ellipse cx="44" cy="40" rx="8" ry="7" fill="#CBD5E1"/>
  </svg>`,
  cloudy: `<svg class="weather-icon-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="32" cy="34" rx="18" ry="12" fill="#64748B"/>
    <ellipse cx="22" cy="36" rx="12" ry="10" fill="#94A3B8"/>
    <ellipse cx="42" cy="36" rx="10" ry="9" fill="#94A3B8"/>
    <ellipse cx="32" cy="28" rx="10" ry="9" fill="#94A3B8"/>
  </svg>`,
  rain: `<svg class="weather-icon-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="32" cy="26" rx="16" ry="10" fill="#64748B"/>
    <ellipse cx="22" cy="28" rx="10" ry="8" fill="#94A3B8"/>
    <ellipse cx="42" cy="28" rx="8" ry="7" fill="#94A3B8"/>
    <g stroke="#7DD3FC" stroke-width="2" stroke-linecap="round">
      <line x1="22" y1="40" x2="20" y2="50"/>
      <line x1="32" y1="42" x2="30" y2="54"/>
      <line x1="42" y1="40" x2="40" y2="50"/>
    </g>
  </svg>`,
  snow: `<svg class="weather-icon-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="32" cy="24" rx="16" ry="10" fill="#64748B"/>
    <ellipse cx="22" cy="26" rx="10" ry="8" fill="#CBD5E1"/>
    <g stroke="#E0F2FE" stroke-width="1.5" stroke-linecap="round">
      <line x1="22" y1="40" x2="22" y2="50"/>
      <line x1="17" y1="45" x2="27" y2="45"/>
      <line x1="18" y1="41" x2="26" y2="49"/>
      <line x1="26" y1="41" x2="18" y2="49"/>
      <line x1="42" y1="40" x2="42" y2="50"/>
      <line x1="37" y1="45" x2="47" y2="45"/>
      <line x1="38" y1="41" x2="46" y2="49"/>
      <line x1="46" y1="41" x2="38" y2="49"/>
    </g>
  </svg>`,
  thunderstorm: `<svg class="weather-icon-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="32" cy="22" rx="16" ry="10" fill="#374151"/>
    <ellipse cx="22" cy="24" rx="10" ry="8" fill="#4B5563"/>
    <ellipse cx="42" cy="24" rx="8" ry="7" fill="#4B5563"/>
    <path d="M36 36L28 48H34L30 58L46 42H38L42 32L36 36Z" fill="#FDE047"/>
  </svg>`,
  fog: `<svg class="weather-icon-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <g stroke="#9CA3AF" stroke-width="2.5" stroke-linecap="round">
      <line x1="12" y1="24" x2="52" y2="24"/>
      <line x1="16" y1="32" x2="48" y2="32"/>
      <line x1="12" y1="40" x2="52" y2="40"/>
      <line x1="20" y1="48" x2="44" y2="48"/>
    </g>
  </svg>`,
};

function getWeatherIcon(iconKey) {
  return WEATHER_ICONS[iconKey] || WEATHER_ICONS['cloudy'];
}

// ── Forecast Icon Map (FontAwesome) ──────────────────────────────────────────
function getFAIconClass(iconKey) {
  const map = {
    'sunny': 'fa-sun',
    'clear-night': 'fa-moon',
    'partly-cloudy': 'fa-cloud-sun',
    'cloudy': 'fa-cloud',
    'rain': 'fa-cloud-rain',
    'snow': 'fa-snowflake',
    'thunderstorm': 'fa-cloud-bolt',
    'fog': 'fa-smog',
  };
  return 'fa-solid ' + (map[iconKey] || 'fa-cloud');
}

// ── State ────────────────────────────────────────────────────────────────────
let currentChart = null;
let lastCitySearched = '';
let updateTimerInterval = null;

// ── DOM References ───────────────────────────────────────────────────────────
const dom = {};

function initDom() {
  const ids = [
    'search-form', 'city-input', 'search-btn', 'search-error',
    'results-container', 'skeleton-loader', 'results-content', 'empty-state',
    'empty-state-title', 'empty-state-body',
    'city-display', 'country-display', 'weather-icon-wrap',
    'temp-display', 'weather-desc', 'feels-like', 'humidity', 'wind-speed',
    'visibility', 'pressure', 'uv-index', 'cloud-cover',
    'ai-confidence', 'category-pill', 'pred-temp', 'trend-dir',
    'cluster-type', 'conditions-summary', 'clothing-primary', 'clothing-items',
    'heat-meter-fill', 'heat-badge', 'heat-tip',
    'cold-meter-fill', 'cold-badge', 'cold-tip',
    'humidity-meter-fill', 'humidity-badge', 'humidity-tip',
    'trend-meta', 'temp-chart',
    'forecast-strip', 'products-grid',
    'city-description', 'tourist-spots', 'city-gallery',
    'update-badge', 'update-time',
    'outfit-meta',
  ];
  ids.forEach(id => {
    dom[id.replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = document.getElementById(id);
    dom[id] = document.getElementById(id);
  });
}

// ── Input Sanitization ───────────────────────────────────────────────────────
function sanitizeInput(val) {
  return val
    .trim()
    .replace(/<[^>]*>/g, '')           // strip HTML tags
    .replace(/[^\w\s\-',\.]/g, '')     // allow only safe chars
    .slice(0, 80);
}

// ── Search Handler ───────────────────────────────────────────────────────────
async function handleSearch(e) {
  if (e) e.preventDefault();
  const raw = dom['city-input'].value;
  const city = sanitizeInput(raw);

  // Clear error
  showSearchError('');

  if (!city || city.length < 2) {
    showSearchError('Please enter a valid city name.');
    return;
  }

  setSearchLoading(true);
  showSkeletonLoader();
  hideEmpty();

  try {
    const data = await fetchWeather(city);
    if (!data) {
      showEmpty('City Not Found', `We couldn't find weather data for "${city}". Check the spelling and try again.`);
      return;
    }
    lastCitySearched = city;
    renderAll(data);
    startUpdateTimer();
  } catch (err) {
    console.error('Weather fetch error:', err);
    showEmpty('Something Went Wrong', 'Unable to fetch weather data. Please check your connection and try again.');
  } finally {
    setSearchLoading(false);
  }
}

async function fetchWeather(city) {
  const resp = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);

  if (resp.status === 404) return null;
  if (resp.status === 429) {
    showSearchError('Rate limit reached. Please wait a moment before searching again.');
    return null;
  }
  if (!resp.ok) return null;

  const json = await resp.json();
  return json.status === 'success' ? json.data : null;
}

// ── Render All ───────────────────────────────────────────────────────────────
function renderAll(data) {
  const { weather, ml, risks, products, city_content, theme } = data;

  // Apply theme
  if (window.ThemeEngine) ThemeEngine.getThemeFromAPI(theme);
  if (window.ParticleEngine) ParticleEngine.applyFromTheme(theme.key);

  renderCurrentWeather(weather.current, weather.city);
  renderMLAnalysis(ml);
  renderRisks(risks);
  renderTrendChart(weather.hourly_24h, ml.trend);
  renderForecast(weather.daily_forecast);
  renderProducts(products, ml.clothing);
  renderCityContent(city_content);

  showResults();
}

// ── Current Weather ──────────────────────────────────────────────────────────
function renderCurrentWeather(current, city) {
  const cityName = city.name;
  const countryCode = city.country_code || city.country;

  setText('city-display', cityName);
  dom['country-display'].textContent = countryCode ? ` · ${countryCode}` : '';
  document.title = `${cityName} — Weather Intelligence`;

  // Weather icon
  dom['weather-icon-wrap'].innerHTML = getWeatherIcon(current.icon_key);

  // Temperature (animated counter)
  animateCounter(dom['temp-display'], 0, current.temperature, 800, val => `${val}`);

  setText('weather-desc', current.description);
  setText('feels-like', current.feels_like);
  setText('humidity', current.humidity);
  setText('wind-speed', current.wind_speed);
  setText('visibility', current.visibility);
  setText('pressure', current.pressure);
  setText('uv-index', current.uv_index ?? '—');
  setText('cloud-cover', current.cloud_cover ?? '—');
}

// ── ML Analysis ──────────────────────────────────────────────────────────────
function renderMLAnalysis(ml) {
  if (!ml || ml.error) return;

  const { category, cluster, trend, clothing, prediction_confidence, summary } = ml;

  // Confidence
  animateCounter(dom['ai-confidence'], 0, Math.round(prediction_confidence), 600, v => v);

  // Category pill
  if (category) {
    dom['category-pill'].textContent = category.label;
    dom['category-pill'].setAttribute('data-cat', category.key);
  }

  // AI stats
  setText('pred-temp', ml.predicted_temp ? `${ml.predicted_temp}°C` : '—');
  setText('trend-dir', capitalize(trend?.trend_direction || 'stable'));
  setText('cluster-type', cluster?.cluster_type || '—');
  setText('conditions-summary', category?.label || '—');

  // Clothing
  if (clothing) {
    setText('clothing-primary', clothing.primary);
    dom['clothing-items'].innerHTML = (clothing.items || [])
      .map(item => `<li>${escHtml(item)}</li>`)
      .join('');
    if (dom['outfit-meta']) {
      dom['outfit-meta'].textContent = `${clothing.ml_prediction || clothing.primary} · ${clothing.confidence || 85}% confidence`;
    }
  }
}

// ── Risk Index ───────────────────────────────────────────────────────────────
function renderRisks(risks) {
  if (!risks) return;

  const { heatstroke, cold_exposure, humidity_discomfort } = risks;

  if (heatstroke) {
    animateMeter('heat-meter-fill', heatstroke.score, heatstroke.color);
    setText('heat-badge', heatstroke.label);
    setText('heat-tip', heatstroke.tip);
    dom['heat-meter-fill'].style.color = heatstroke.color;
    document.documentElement.style.setProperty('--risk-heat-color', heatstroke.color);
  }

  if (cold_exposure) {
    animateMeter('cold-meter-fill', cold_exposure.score, cold_exposure.color);
    setText('cold-badge', cold_exposure.label);
    setText('cold-tip', cold_exposure.tip);
    dom['cold-meter-fill'].style.color = cold_exposure.color;
    document.documentElement.style.setProperty('--risk-cold-color', cold_exposure.color);
  }

  if (humidity_discomfort) {
    animateMeter('humidity-meter-fill', humidity_discomfort.score, humidity_discomfort.color);
    setText('humidity-badge', humidity_discomfort.label);
    setText('humidity-tip', humidity_discomfort.tip);
    dom['humidity-meter-fill'].style.color = humidity_discomfort.color;
    document.documentElement.style.setProperty('--risk-humidity-color', humidity_discomfort.color);
  }
}

// ── Temperature Trend Chart ───────────────────────────────────────────────────
function renderTrendChart(hourly, trend) {
  if (currentChart) {
    currentChart.destroy();
    currentChart = null;
  }

  const canvas = dom['temp-chart'];
  if (!canvas) return;

  const historicalTemps = hourly?.temperatures?.slice(0, 12) || [];
  const predictedTemps = trend?.predicted_temps || [];
  const historicalTimes = (hourly?.times || []).slice(0, 12).map(formatHour);

  const futureTimes = [];
  const lastHour = hourly?.times?.[11]
    ? new Date(hourly.times[11] + ':00')
    : new Date();
  for (let i = 1; i <= 12; i++) {
    const d = new Date(lastHour.getTime() + i * 3600000);
    futureTimes.push(d.getHours().toString().padStart(2, '0') + ':00');
  }

  const allLabels = [...historicalTimes, ...futureTimes];

  // Historical dataset (solid)
  const historicalData = [...historicalTemps, ...new Array(12).fill(null)];
  // Predicted dataset (dashed)
  const predictedData = [...new Array(historicalTemps.length - 1).fill(null),
    historicalTemps[historicalTemps.length - 1] || null,
    ...predictedTemps];

  const accent = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#818cf8';
  const accentRgb = hexToRgb(accent) || { r: 129, g: 140, b: 248 };

  const ctx = canvas.getContext('2d');

  // Gradient fill
  const gradient = ctx.createLinearGradient(0, 0, 0, canvas.clientHeight * 1.5);
  gradient.addColorStop(0, `rgba(${accentRgb.r}, ${accentRgb.g}, ${accentRgb.b}, 0.2)`);
  gradient.addColorStop(1, `rgba(${accentRgb.r}, ${accentRgb.g}, ${accentRgb.b}, 0)`);

  currentChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: allLabels,
      datasets: [
        {
          label: 'Recorded Temperature (°C)',
          data: historicalData,
          borderColor: accent,
          backgroundColor: gradient,
          borderWidth: 2,
          pointRadius: 3,
          pointBackgroundColor: accent,
          fill: true,
          tension: 0.4,
          spanGaps: false,
        },
        {
          label: 'AI Predicted Temperature (°C)',
          data: predictedData,
          borderColor: `rgba(${accentRgb.r}, ${accentRgb.g}, ${accentRgb.b}, 0.5)`,
          borderWidth: 2,
          borderDash: [6, 4],
          pointRadius: 2,
          pointBackgroundColor: `rgba(${accentRgb.r}, ${accentRgb.g}, ${accentRgb.b}, 0.5)`,
          fill: false,
          tension: 0.4,
          spanGaps: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          labels: {
            color: 'rgba(240,240,248,0.6)',
            font: { family: "'DM Sans', sans-serif", size: 12 },
            boxWidth: 16,
          },
        },
        tooltip: {
          backgroundColor: 'rgba(20, 20, 30, 0.9)',
          titleColor: '#f0f0f8',
          bodyColor: 'rgba(240,240,248,0.7)',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: ctx => ctx.parsed.y !== null
              ? `${ctx.dataset.label}: ${ctx.parsed.y}°C`
              : null,
          },
        },
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: {
            color: 'rgba(240,240,248,0.4)',
            font: { family: "'DM Sans', sans-serif", size: 11 },
            maxRotation: 0,
            maxTicksLimit: 8,
          },
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: {
            color: 'rgba(240,240,248,0.4)',
            font: { family: "'DM Sans', sans-serif", size: 11 },
            callback: v => `${v}°`,
          },
        },
      },
    },
  });

  // Update trend meta
  if (dom['trend-meta'] && trend) {
    const dir = trend.trend_direction || 'stable';
    const slope = trend.slope || 0;
    dom['trend-meta'].textContent = `Linear Regression · Trend: ${capitalize(dir)} (${slope > 0 ? '+' : ''}${slope}°C/h)`;
  }
}

// ── 7-Day Forecast ────────────────────────────────────────────────────────────
function renderForecast(days) {
  if (!dom['forecast-strip'] || !days?.length) return;

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const today = new Date();

  dom['forecast-strip'].innerHTML = days.map((day, i) => {
    const d = day.date ? new Date(day.date) : new Date(today.getTime() + i * 86400000);
    const name = i === 0 ? 'Today' : dayNames[d.getDay()];
    const iconClass = getFAIconClass(day.icon_key || 'cloudy');

    return `
      <div class="forecast-day" title="${escHtml(day.description)}">
        <span class="forecast-day__name">${name}</span>
        <i class="${iconClass} forecast-day__icon"></i>
        <span class="forecast-day__max">${day.temp_max}°</span>
        <span class="forecast-day__min">${day.temp_min}°</span>
        <span class="forecast-day__desc">${escHtml(day.description)}</span>
      </div>
    `;
  }).join('');
}

// ── Products ──────────────────────────────────────────────────────────────────
function renderProducts(products, clothing) {
  if (!dom['products-grid']) return;

  if (!products?.length) {
    dom['products-grid'].innerHTML = `<p style="color:var(--text-tertiary);grid-column:1/-1;padding:2rem 0;">Product suggestions are currently unavailable.</p>`;
    return;
  }

  dom['products-grid'].innerHTML = products.map(p => `
    <a class="product-card" href="${escAttr(p.link)}" target="_blank" rel="noopener noreferrer">
      <div class="product-card__img-wrap">
        <img
          class="product-card__img"
          src="${escAttr(p.image)}"
          alt="${escAttr(p.name)}"
          loading="lazy"
          onload="this.classList.add('loaded')"
          onerror="this.src='data:image/svg+xml,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'400\\' height=\\'300\\'/>';"
        />
        <span class="product-card__tag">${escHtml(p.tag || 'Featured')}</span>
      </div>
      <div class="product-card__body">
        <div class="product-card__brand">${escHtml(p.brand || '')}</div>
        <div class="product-card__name">${escHtml(p.name)}</div>
        <div class="product-card__footer">
          <span class="product-card__price">${escHtml(p.price)}</span>
          <span class="product-card__cta">
            View <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:0.7rem;"></i>
          </span>
        </div>
      </div>
    </a>
  `).join('');
}

// ── City Content ──────────────────────────────────────────────────────────────
function renderCityContent(cityContent) {
  if (!cityContent) return;

  // Description
  setText('city-description', cityContent.description || '');

  // Tourist spots
  const spots = cityContent.tourist_spots || [];
  if (dom['tourist-spots']) {
    if (spots.length) {
      dom['tourist-spots'].innerHTML = `
        <div style="font-size:0.75rem;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;">
          Popular Attractions
        </div>
        ${spots.map(s => `
          <div class="tourist-spot-item">
            <i class="fa-solid fa-map-pin"></i>
            <span>${escHtml(s)}</span>
          </div>
        `).join('')}
      `;
    } else {
      dom['tourist-spots'].innerHTML = '';
    }
  }

  // Gallery
  const images = cityContent.images || [];
  if (dom['city-gallery']) {
    if (images.length) {
      dom['city-gallery'].innerHTML = images.slice(0, 4).map((img, i) => `
        <div class="city-gallery__img-wrap">
          <img
            class="city-gallery__img"
            src="${escAttr(img.url)}"
            alt="${escAttr(img.alt || cityContent.name)}"
            loading="lazy"
            onload="this.classList.add('loaded')"
            onerror="this.parentElement.style.display='none';"
          />
        </div>
      `).join('');
    } else {
      dom['city-gallery'].innerHTML = '';
    }
  }
}

// ── Update Timer ──────────────────────────────────────────────────────────────
function startUpdateTimer() {
  if (updateTimerInterval) clearInterval(updateTimerInterval);
  const badge = dom['update-badge'];
  const timeEl = dom['update-time'];
  if (!badge || !timeEl) return;

  badge.style.display = 'flex';
  timeEl.textContent = 'Just updated';

  let secondsAgo = 0;
  updateTimerInterval = setInterval(() => {
    secondsAgo += 10;
    const mins = Math.floor(secondsAgo / 60);
    timeEl.textContent = mins < 1
      ? 'Just updated'
      : `Updated ${mins}m ago`;
  }, 10000);
}

// ── UI State Helpers ──────────────────────────────────────────────────────────
function showSkeletonLoader() {
  const rc = dom['results-container'];
  const sk = dom['skeleton-loader'];
  const rv = dom['results-content'];
  if (rc) rc.style.display = 'block';
  if (sk) sk.style.display = 'block';
  if (rv) rv.style.display = 'none';
}

function showResults() {
  const sk = dom['skeleton-loader'];
  const rv = dom['results-content'];
  if (sk) {
    sk.style.opacity = '0';
    sk.style.transition = 'opacity 0.3s';
    setTimeout(() => {
      sk.style.display = 'none';
      sk.style.opacity = '';
    }, 300);
  }
  if (rv) {
    rv.style.display = 'block';
    rv.style.animation = 'fadeInUp 0.4s ease forwards';
  }

  // Scroll to results
  setTimeout(() => {
    dom['results-container']?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);
}

function showEmpty(title, body) {
  const rc = dom['results-container'];
  const sk = dom['skeleton-loader'];
  const rv = dom['results-content'];
  const es = dom['empty-state'];

  if (rc) rc.style.display = 'none';
  if (sk) sk.style.display = 'none';
  if (rv) rv.style.display = 'none';
  if (es) {
    es.style.display = 'flex';
    setText('empty-state-title', title);
    setText('empty-state-body', body);
  }
}

function hideEmpty() {
  const es = dom['empty-state'];
  if (es) es.style.display = 'none';
}

function setSearchLoading(loading) {
  const btn = dom['search-btn'];
  if (!btn) return;
  if (loading) {
    btn.classList.add('loading');
    btn.innerHTML = `<span class="loading-spinner"></span>`;
  } else {
    btn.classList.remove('loading');
    btn.innerHTML = `<span class="btn-text">Analyse</span><i class="fa-solid fa-arrow-right btn-icon"></i>`;
  }
}

function showSearchError(msg) {
  const el = dom['search-error'];
  if (el) el.textContent = msg || '';
}

// ── Utility Functions ─────────────────────────────────────────────────────────
function setText(id, val) {
  const el = dom[id] || document.getElementById(id);
  if (el) el.textContent = val ?? '—';
}

function escHtml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function escAttr(str) {
  return String(str || '').replace(/['"<>&]/g, c => ({
    "'": '&#039;', '"': '&quot;', '<': '&lt;', '>': '&gt;', '&': '&amp;',
  }[c]));
}

function capitalize(str) {
  return String(str || '').charAt(0).toUpperCase() + String(str || '').slice(1);
}

function formatHour(isoStr) {
  if (!isoStr) return '';
  const parts = isoStr.split('T');
  return parts[1]?.slice(0, 5) || isoStr.slice(-5);
}

function hexToRgb(hex) {
  hex = hex.trim().replace('#', '');
  if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
  const n = parseInt(hex, 16);
  if (isNaN(n)) return null;
  return { r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255 };
}

function animateCounter(el, from, to, duration, format) {
  if (!el) return;
  const start = performance.now();
  const step = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const val = Math.round(from + (to - from) * eased);
    el.textContent = format(val);
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

function animateMeter(elId, score, color) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.style.background = color || 'var(--accent)';
  el.style.color = color || 'var(--accent)';
  // Slight delay for CSS transition
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      el.style.width = `${Math.min(100, Math.max(0, score))}%`;
    });
  });
}

// ── Scroll Reveal ─────────────────────────────────────────────────────────────
function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('revealed');
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('[data-reveal]').forEach(el => observer.observe(el));
}

// ── Keyboard Shortcut ─────────────────────────────────────────────────────────
function initKeyboardShortcut() {
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT') {
      e.preventDefault();
      dom['city-input']?.focus();
    }
    if (e.key === 'Enter' && document.activeElement === dom['city-input']) {
      handleSearch(e);
    }
  });
}

// ── Boot ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initDom();
  initScrollReveal();
  initKeyboardShortcut();

  // Search form
  const form = document.getElementById('search-form');
  if (form) {
    form.addEventListener('submit', handleSearch);
  }

  const btn = document.getElementById('search-btn');
  if (btn) {
    btn.addEventListener('click', handleSearch);
  }

  // Input: clear error on type
  const input = document.getElementById('city-input');
  if (input) {
    input.addEventListener('input', () => showSearchError(''));
    // Focus on load
    setTimeout(() => input.focus(), 500);
  }

  // Default city on load (optional UX)
  // Uncomment to auto-load a default city:
  // dom['city-input'].value = 'London'; handleSearch();
});
