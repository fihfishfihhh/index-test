body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f3f5f9;
    color: #1d2433;
}

* { box-sizing: border-box; }

button, input {
    font: inherit;
}

main.app-shell {
    max-width: 1100px;
    margin: 0 auto;
    padding: 20px 12px 40px;
}

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 18px;
}

.topbar h1 {
    margin: 4px 0 0;
    font-size: clamp(1.8rem, 3vw, 2.3rem);
}

.eyebrow {
    color: #5e6c82;
    text-transform: uppercase;
    font-size: 0.76rem;
    letter-spacing: 0.08em;
}

.card {
    background: #ffffff;
    border: 1px solid #dfe5ee;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(20, 33, 61, 0.04);
    padding: 16px;
    margin-bottom: 16px;
}

.stage {
    position: relative;
    width: 100%;
    height: 420px;
    background: #0a0d13;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #1d2637;
}

#video, #overlay {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
}

#overlay {
    pointer-events: none;
}

.status-bar {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    background: rgba(0, 0, 0, 0.6);
    color: white;
    min-height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    letter-spacing: 0.02em;
    opacity: 0;
    transition: opacity 0.2s ease;
}

.status-bar.show {
    opacity: 1;
}

.status-bar.valid { background: rgba(24, 159, 95, 0.82); }
.status-bar.invalid { background: rgba(189, 46, 46, 0.84); }

.identity-label {
    position: absolute;
    left: 12px;
    bottom: 12px;
    background: rgba(0,0,0,0.6);
    color: white;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 0.9rem;
    display: none;
}

.challenge-box {
    position: absolute;
    left: 50%;
    bottom: 18px;
    transform: translateX(-50%);
    background: rgba(14, 18, 26, 0.7);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 10px;
    color: #fff;
    padding: 10px 16px;
    text-align: center;
    font-weight: 700;
}

.hidden { display: none !important; }

.camera-toolbar,
.inline-actions,
.dev-tabs {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 12px;
}

.button {
    border: 1px solid #d5dbe6;
    background: #ffffff;
    color: #1d2433;
    border-radius: 10px;
    padding: 10px 14px;
    cursor: pointer;
    font-weight: 700;
}

.button.primary {
    background: #2d5ee3;
    color: white;
    border-color: #2d5ee3;
}

.button.accent {
    background: #0e9f6e;
    color: white;
    border-color: #0e9f6e;
}

.button.secondary {
    background: #edf2ff;
    color: #1d2433;
}

.button.mode.active,
.button.tab.active {
    background: #152c52;
    color: white;
    border-color: #152c52;
}

.full {
    width: 100%;
}

.grid-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

label {
    display: block;
    margin: 12px 0 6px;
    font-weight: 700;
}

input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #d3ddea;
    border-radius: 10px;
    background: #fbfcff;
}

.summary-box {
    margin-top: 14px;
    background: #f5f8ff;
    border: 1px solid #dfe7fb;
    border-radius: 10px;
    padding: 12px;
    min-height: 100px;
    font-size: 0.96rem;
}

.panel-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
}

.panel-header h2 {
    margin: 0 10px 0 0;
}

.dev-panel input {
    flex: 1;
}

.tab-panel {
    display: none;
    margin-top: 14px;
}

.tab-panel.active {
    display: block;
}

.log-list {
    margin-top: 16px;
    max-height: 260px;
    overflow: auto;
    display: grid;
    gap: 8px;
}

.log-item {
    border: 1px solid #dde5ee;
    border-radius: 10px;
    padding: 10px 12px;
    background: #fafcff;
}

.status-text {
    margin-top: 14px;
    color: #485769;
    font-weight: 600;
}

@media (max-width: 760px) {
    .grid-layout {
        grid-template-columns: 1fr;
    }

    .stage {
        height: 320px;
    }
}
