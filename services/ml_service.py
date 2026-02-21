"""
ml_service.py — Weather Intelligence Platform
Pure NumPy implementation of all ML algorithms.
Zero dependency on scikit-learn or pandas — fully Python 3.14 compatible.

Implements from scratch:
  - Linear Regression  (Normal Equation + R²)
  - Logistic Regression (Softmax, gradient descent)
  - KMeans Clustering  (k-means++ initialisation)
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
#  STANDARD SCALER
# ════════════════════════════════════════════════════════════════════════════

class StandardScaler:
    def __init__(self):
        self.mean_ = None
        self.std_ = None

    def fit(self, X):
        self.mean_ = X.mean(axis=0)
        self.std_ = X.std(axis=0)
        self.std_[self.std_ == 0] = 1.0
        return self

    def transform(self, X):
        return (X - self.mean_) / self.std_

    def fit_transform(self, X):
        return self.fit(X).transform(X)


# ════════════════════════════════════════════════════════════════════════════
#  LINEAR REGRESSION  (Normal Equation)
# ════════════════════════════════════════════════════════════════════════════

class LinearRegression:
    def __init__(self):
        self.coef_ = None
        self.intercept_ = None
        self._w = None

    def fit(self, X, y):
        n = X.shape[0]
        Xb = np.hstack([np.ones((n, 1)), X])
        lam = 1e-8
        A = Xb.T @ Xb + lam * np.eye(Xb.shape[1])
        b = Xb.T @ y
        try:
            self._w = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            self._w = np.linalg.lstsq(Xb, y, rcond=None)[0]
        self.intercept_ = float(self._w[0])
        self.coef_ = self._w[1:]
        return self

    def predict(self, X):
        Xb = np.hstack([np.ones((X.shape[0], 1)), X])
        return Xb @ self._w

    def score(self, X, y):
        y_pred = self.predict(X)
        ss_res = float(np.sum((y - y_pred) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        return 1.0 - ss_res / (ss_tot + 1e-12)


# ════════════════════════════════════════════════════════════════════════════
#  LOGISTIC REGRESSION  (Softmax + gradient descent)
# ════════════════════════════════════════════════════════════════════════════

def _softmax(Z):
    Z = Z - Z.max(axis=1, keepdims=True)
    E = np.exp(Z)
    return E / E.sum(axis=1, keepdims=True)


class LogisticRegression:
    def __init__(self, max_iter=400, lr=0.5, lam=1e-4):
        self.max_iter = max_iter
        self.lr = lr
        self.lam = lam
        self.W = None
        self.classes_ = None

    def fit(self, X, y):
        n, d = X.shape
        self.classes_ = np.unique(y)
        K = len(self.classes_)
        label_to_idx = {c: i for i, c in enumerate(self.classes_)}
        y_idx = np.array([label_to_idx[c] for c in y])

        Y = np.zeros((n, K))
        Y[np.arange(n), y_idx] = 1.0

        Xb = np.hstack([np.ones((n, 1)), X])
        rng = np.random.default_rng(42)
        self.W = rng.normal(0, np.sqrt(2.0 / (d + K)), (d + 1, K))

        for _ in range(self.max_iter):
            P = _softmax(Xb @ self.W)
            grad = Xb.T @ (P - Y) / n
            grad[1:] += self.lam * self.W[1:]
            self.W -= self.lr * grad

        return self

    def predict_proba(self, X):
        Xb = np.hstack([np.ones((X.shape[0], 1)), X])
        return _softmax(Xb @ self.W)

    def predict(self, X):
        return self.classes_[np.argmax(self.predict_proba(X), axis=1)]


# ════════════════════════════════════════════════════════════════════════════
#  KMEANS  (k-means++ init + Lloyd's algorithm)
# ════════════════════════════════════════════════════════════════════════════

class KMeans:
    def __init__(self, n_clusters=4, max_iter=100, n_init=3, random_state=0):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.n_init = n_init
        self.random_state = random_state
        self.cluster_centers_ = None
        self.labels_ = None
        self.inertia_ = np.inf

    def _init_centers(self, X, rng):
        n = X.shape[0]
        idx = rng.integers(0, n)
        centers = [X[idx].copy()]
        for _ in range(1, self.n_clusters):
            dists = np.array([
                min(float(np.sum((x - c) ** 2)) for c in centers)
                for x in X
            ])
            probs = dists / (dists.sum() + 1e-12)
            idx = rng.choice(n, p=probs)
            centers.append(X[idx].copy())
        return np.array(centers)

    def _run_once(self, X, rng):
        centers = self._init_centers(X, rng)
        labels = np.zeros(X.shape[0], dtype=int)

        for _ in range(self.max_iter):
            diff = X[:, np.newaxis, :] - centers[np.newaxis, :, :]
            dists_sq = np.sum(diff ** 2, axis=2)
            new_labels = np.argmin(dists_sq, axis=1)
            if np.array_equal(new_labels, labels):
                break
            labels = new_labels
            for k in range(self.n_clusters):
                members = X[labels == k]
                if len(members):
                    centers[k] = members.mean(axis=0)

        inertia = float(np.sum(np.min(
            np.sum((X[:, np.newaxis, :] - centers[np.newaxis, :, :]) ** 2, axis=2),
            axis=1
        )))
        return centers, labels, inertia

    def fit(self, X):
        rng = np.random.default_rng(self.random_state)
        best_c, best_l, best_i = None, None, np.inf
        for _ in range(self.n_init):
            c, l, i = self._run_once(X, rng)
            if i < best_i:
                best_c, best_l, best_i = c, l, i
        self.cluster_centers_ = best_c
        self.labels_ = best_l
        self.inertia_ = best_i
        return self

    def predict(self, X):
        diff = X[:, np.newaxis, :] - self.cluster_centers_[np.newaxis, :, :]
        dists_sq = np.sum(diff ** 2, axis=2)
        return np.argmin(dists_sq, axis=1)


# ════════════════════════════════════════════════════════════════════════════
#  CATEGORY & CLOTHING LOGIC
# ════════════════════════════════════════════════════════════════════════════

CATEGORIES = [
    ('extreme_cold', 'Extreme Cold', lambda t: t < 5),
    ('cold',         'Cold',         lambda t: 5  <= t < 15),
    ('normal',       'Normal',       lambda t: 15 <= t < 25),
    ('warm',         'Warm',         lambda t: 25 <= t < 30),
    ('hot',          'Hot',          lambda t: 30 <= t < 35),
    ('extreme_hot',  'Extreme Hot',  lambda t: t >= 35),
]


def classify_temperature(temp):
    for key, label, fn in CATEGORIES:
        if fn(temp):
            return {'key': key, 'label': label}
    return {'key': 'normal', 'label': 'Normal'}


def clothing_from_temp(temp, wind=0, humidity=50):
    eff = temp - wind * 0.05
    if eff < 5:
        primary = 'Heavy Jacket + Thermal Sweater'
        items = ['Thermal base layer', 'Heavy insulated jacket', 'Wool sweater', 'Scarf & gloves', 'Warm boots']
    elif eff < 10:
        primary = 'Heavy Jacket'
        items = ['Fleece sweater', 'Heavy jacket', 'Jeans or warm pants', 'Warm socks']
    elif eff < 20:
        primary = 'Light Jacket'
        items = ['Light jacket or hoodie', 'Long-sleeve shirt', 'Comfortable trousers']
    elif eff < 25:
        primary = 'Full Sleeve Shirt'
        items = ['Long-sleeve shirt or light sweater', 'Jeans or chinos']
    elif eff < 30:
        primary = 'T-Shirt & Jeans'
        items = ['T-shirt', 'Light jeans or shorts', 'Sneakers']
    elif eff < 35:
        primary = 'Light Cotton Wear'
        items = ['Breathable cotton t-shirt', 'Shorts or light trousers', 'Sunglasses']
    else:
        primary = 'Summer Wear'
        items = ['Lightweight linen/cotton', 'Shorts', 'Sun hat', 'Sunglasses', 'Sunscreen']
    if humidity > 75 and temp > 20:
        items.append('Moisture-wicking fabric recommended')
    return {'primary': primary, 'items': items}


# ════════════════════════════════════════════════════════════════════════════
#  LINEAR REGRESSION: 24h temperature trend
# ════════════════════════════════════════════════════════════════════════════

def predict_temperature_trend(hourly_temps):
    if len(hourly_temps) < 4:
        fallback = float(hourly_temps[0]) if hourly_temps else 20.0
        return {
            'historical_temps': list(hourly_temps),
            'smoothed_temps': list(hourly_temps),
            'predicted_temps': [fallback] * 12,
            'slope': 0.0, 'trend_direction': 'stable',
            'confidence': 0.0, 'next_6h_avg': fallback, 'next_12h_avg': fallback,
        }

    temps = np.array(hourly_temps, dtype=float)
    X = np.arange(len(temps), dtype=float).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, temps)

    confidence = max(0.0, min(1.0, model.score(X, temps)))
    future_X = np.arange(len(temps), len(temps) + 12, dtype=float).reshape(-1, 1)
    future_preds = model.predict(future_X).tolist()

    window = min(6, len(temps))
    smoothed = np.convolve(temps, np.ones(window) / window, mode='valid').tolist()

    slope = float(model.coef_[0])
    trend_dir = 'rising' if slope > 0.15 else ('falling' if slope < -0.15 else 'stable')

    return {
        'historical_temps': temps.tolist(),
        'smoothed_temps': smoothed,
        'predicted_temps': [round(t, 1) for t in future_preds],
        'slope': round(slope, 3),
        'trend_direction': trend_dir,
        'confidence': round(confidence * 100, 1),
        'next_6h_avg': round(float(np.mean(future_preds[:6])), 1),
        'next_12h_avg': round(float(np.mean(future_preds)), 1),
    }


# ════════════════════════════════════════════════════════════════════════════
#  LOGISTIC REGRESSION: Clothing prediction — module-level cache
# ════════════════════════════════════════════════════════════════════════════

_CLOTHING_LABELS = [
    'Heavy Jacket + Thermal', 'Heavy Jacket', 'Light Jacket',
    'Full Sleeve Shirt', 'T-Shirt & Jeans', 'Light Cotton', 'Summer Wear',
]

_log_model = None
_log_scaler = None


def _build_clothing_data():
    rng = np.random.default_rng(42)
    n = 2000
    temps = rng.uniform(-10, 45, n)
    humidity = rng.uniform(10, 100, n)
    wind = rng.uniform(0, 80, n)
    labels = []
    for t, h, w in zip(temps, humidity, wind):
        eff = t - w * 0.05
        if   eff <  5:  labels.append(0)
        elif eff < 10:  labels.append(1)
        elif eff < 20:  labels.append(2)
        elif eff < 25:  labels.append(3)
        elif eff < 30:  labels.append(4)
        elif eff < 35:  labels.append(5)
        else:           labels.append(6)
    return np.column_stack([temps, humidity, wind]), np.array(labels)


def _get_logistic_model():
    global _log_model, _log_scaler
    if _log_model is None:
        logger.info("Training Logistic Regression...")
        X, y = _build_clothing_data()
        _log_scaler = StandardScaler()
        Xs = _log_scaler.fit_transform(X)
        _log_model = LogisticRegression(max_iter=400, lr=0.5, lam=1e-4)
        _log_model.fit(Xs, y)
        logger.info("Logistic Regression ready.")
    return _log_model, _log_scaler


def predict_clothing_logistic(temp, humidity, wind):
    model, scaler = _get_logistic_model()
    feat = scaler.transform(np.array([[temp, humidity, wind]]))
    proba = model.predict_proba(feat)[0]
    pred_class = int(np.argmax(proba))
    return {
        'clothing_category': _CLOTHING_LABELS[pred_class],
        'class_index': pred_class,
        'confidence': round(float(proba[pred_class]) * 100, 1),
    }


# ════════════════════════════════════════════════════════════════════════════
#  KMEANS: Weather pattern clustering — module-level cache
# ════════════════════════════════════════════════════════════════════════════

CLUSTER_LABELS = ['Dry Heat', 'Humid Heat', 'Windy Cold', 'Mild Pleasant']

_KMEANS_CENTERS_RAW = np.array([
    [37.0, 20.0, 15.0],
    [33.0, 85.0, 10.0],
    [ 5.0, 60.0, 45.0],
    [20.0, 55.0, 12.0],
])

_km_model = None
_km_scaler = None


def _get_kmeans_model():
    global _km_model, _km_scaler
    if _km_model is None:
        logger.info("Training KMeans...")
        rng = np.random.default_rng(0)
        samples = [rng.normal(loc=c, scale=[4, 12, 8], size=(400, 3))
                   for c in _KMEANS_CENTERS_RAW]
        X = np.clip(np.vstack(samples), [-20, 0, 0], [50, 100, 120])
        _km_scaler = StandardScaler()
        Xs = _km_scaler.fit_transform(X)
        _km_model = KMeans(n_clusters=4, n_init=5, random_state=0)
        _km_model.fit(Xs)
        logger.info("KMeans ready.")
    return _km_model, _km_scaler


def predict_cluster(temp, humidity, wind):
    model, scaler = _get_kmeans_model()
    feat = scaler.transform(np.array([[temp, humidity, wind]]))
    cluster_id = int(model.predict(feat)[0])
    center = model.cluster_centers_[cluster_id]
    dist = float(np.linalg.norm(feat[0] - center))
    confidence = round(max(0.0, min(100.0, 100.0 - dist * 20.0)), 1)
    return {
        'cluster_id': cluster_id,
        'cluster_type': CLUSTER_LABELS[cluster_id],
        'confidence': confidence,
    }


# ════════════════════════════════════════════════════════════════════════════
#  MASTER ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

def run_full_analysis(weather_payload):
    current = weather_payload.get('current', {})
    hourly  = weather_payload.get('hourly_24h', {})

    temp       = float(current.get('temperature',  20))
    feels_like = float(current.get('feels_like',   temp))
    humidity   = float(current.get('humidity',     50))
    wind       = float(current.get('wind_speed',   0))
    hourly_temps = hourly.get('temperatures', [])

    try:
        trend = predict_temperature_trend(hourly_temps) if hourly_temps else {}
    except Exception as e:
        logger.warning(f"Trend prediction failed: {e}")
        trend = {}

    try:
        clothing_ml = predict_clothing_logistic(temp, humidity, wind)
    except Exception as e:
        logger.warning(f"Logistic prediction failed: {e}")
        clothing_ml = {'clothing_category': 'T-Shirt & Jeans', 'class_index': 4, 'confidence': 75.0}

    clothing_rules = clothing_from_temp(temp, wind, humidity)
    category = classify_temperature(temp)

    try:
        cluster = predict_cluster(temp, humidity, wind)
    except Exception as e:
        logger.warning(f"Cluster prediction failed: {e}")
        cluster = {'cluster_id': 3, 'cluster_type': 'Mild Pleasant', 'confidence': 70.0}

    overall_conf = round(
        trend.get('confidence', 70.0)  * 0.40 +
        clothing_ml.get('confidence', 80.0) * 0.35 +
        cluster.get('confidence', 75.0)     * 0.25, 1
    )

    return {
        'predicted_temp': trend.get('next_6h_avg', round(temp, 1)),
        'trend': trend,
        'clothing': {
            'ml_prediction': clothing_ml['clothing_category'],
            'primary':       clothing_rules['primary'],
            'items':         clothing_rules['items'],
            'confidence':    clothing_ml['confidence'],
        },
        'category':              category,
        'cluster':               cluster,
        'prediction_confidence': overall_conf,
        'summary': {
            'current_temp':    temp,
            'feels_like':      feels_like,
            'humidity':        humidity,
            'wind_speed':      wind,
            'category':        category['label'],
            'cluster_type':    cluster['cluster_type'],
            'trend_direction': trend.get('trend_direction', 'stable'),
        },
    }
