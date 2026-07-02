const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');

let state = null;
let gameId = null;
let keys = {};
let mouseX = 400;
let mouseY = 300;
let spellActive = false;
let commandActive = false;
let pollInterval = null;

function drawSquare(x, y, size, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x - size / 2, y - size / 2, size, size);
    ctx.strokeStyle = 'rgba(255,255,255,0.3)';
    ctx.lineWidth = 2;
    ctx.strokeRect(x - size / 2, y - size / 2, size, size);
}

function drawTriangle(x, y, size, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(x, y - size);
    ctx.lineTo(x - size, y + size);
    ctx.lineTo(x + size, y + size);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.3)';
    ctx.lineWidth = 2;
    ctx.stroke();
}

function drawCircle(x, y, size, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, size, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.3)';
    ctx.lineWidth = 2;
    ctx.stroke();
}

function drawRectangle(x, y, size, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x - size.w / 2, y - size.h / 2, size.w, size.h);
    ctx.strokeStyle = 'rgba(255,255,255,0.3)';
    ctx.lineWidth = 2;
    ctx.strokeRect(x - size.w / 2, y - size.h / 2, size.w, size.h);
}

function getDrawFn(role) {
    if (role === 'square') return drawSquare;
    if (role === 'triangle') return drawTriangle;
    if (role === 'circle') return drawCircle;
    if (role === 'rectangle') return drawRectangle;
    return drawSquare;
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#0d0d1a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = '#1a1a2e';
    ctx.lineWidth = 1;
    for (let i = 0; i < canvas.width; i += 40) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, canvas.height);
        ctx.stroke();
    }
    for (let i = 0; i < canvas.height; i += 40) {
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(canvas.width, i);
        ctx.stroke();
    }

    if (!state) return;

    (state.monsters || []).forEach(m => {
        ctx.fillStyle = m.color;
        ctx.beginPath();
        if (m.type === 'circle') {
            ctx.arc(m.x, m.y, 15, 0, Math.PI * 2);
        } else if (m.type === 'triangle') {
            ctx.moveTo(m.x, m.y - 15);
            ctx.lineTo(m.x - 15, m.y + 15);
            ctx.lineTo(m.x + 15, m.y + 15);
            ctx.closePath();
        } else {
            ctx.fillRect(m.x - 12, m.y - 12, 24, 24);
        }
        ctx.fill();

        const barW = 30, barH = 4;
        const barX = m.x - barW / 2, barY = m.y - 25;
        ctx.fillStyle = '#333';
        ctx.fillRect(barX, barY, barW, barH);
        ctx.fillStyle = m.hp > 1 ? '#2ecc71' : '#e74c3c';
        ctx.fillRect(barX, barY, barW * (m.hp / m.maxHp), barH);
    });

    (state.energies || []).forEach(e => {
        const pulse = Math.sin(Date.now() / 200 + e.x) * 0.3 + 0.7;
        ctx.save();
        ctx.globalAlpha = pulse;
        ctx.shadowColor = '#f1c40f';
        ctx.shadowBlur = 20;
        ctx.fillStyle = '#f1c40f';
        ctx.beginPath();
        ctx.arc(e.x, e.y, 10, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
        ctx.fillStyle = '#fff';
        ctx.font = '8px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('ENERGY', e.x, e.y + 20);
    });

    const p = state.player;
    if (p) {
        if (p.invincible && Math.floor(Date.now() / 100) % 2 === 0) {
            ctx.globalAlpha = 0.3;
        }
        const draw = getDrawFn(p.role);
        draw(p.x, p.y, p.size, p.color);
        ctx.globalAlpha = 1;

        if (state.player.slashTimer > 0) {
            const alpha = state.player.slashTimer / 10;
            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.strokeStyle = '#f1c40f';
            ctx.lineWidth = 4;
            ctx.shadowColor = '#f1c40f';
            ctx.shadowBlur = 12;
            ctx.beginPath();
            const endX = p.x + p.lastDx * 100;
            const endY = p.y + p.lastDy * 100;
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(endX, endY);
            ctx.stroke();
            ctx.restore();
        }

        ctx.fillStyle = '#fff';
        ctx.font = '12px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('YOU', p.x, p.y + (p.size.w || p.size) + 18);
    }
}

function updateHUD() {
    if (!state || !state.player) return;
    const pct = Math.max(0, (state.player.hp / state.player.maxHp) * 100);
    document.getElementById('health-fill').style.width = pct + '%';
    document.getElementById('health-text').textContent = Math.ceil(state.player.hp);
    document.getElementById('score').textContent = state.score;
}

async function sendUpdate() {
    if (!gameId) return;
    try {
        const res = await fetch('/api/game/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ keys })
        });
        state = await res.json();
        updateHUD();

        if (state.spellActive && !spellActive) {
            spellActive = true;
            showSpellModal(state.currentWord);
        }
        if (!state.running && !document.getElementById('game-over-modal').style.display) {
            showGameOver();
        }
        draw();
    } catch (e) {
        console.error('Update error', e);
    }
}

async function sendAction(action, extra = {}) {
    if (!gameId) return;
    try {
        const res = await fetch('/api/game/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, ...extra })
        });
        state = await res.json();
        updateHUD();
        draw();
    } catch (e) {
        console.error('Action error', e);
    }
}

function showSpellModal(word) {
    document.getElementById('spell-word').textContent = word;
    document.getElementById('spell-result').textContent = '';
    document.getElementById('spell-input').value = '';
    document.getElementById('spell-modal').style.display = 'flex';
    document.getElementById('spell-input').focus();
}

async function submitSpell() {
    const input = document.getElementById('spell-input');
    const given = input.value.trim().toLowerCase();
    try {
        const res = await fetch('/api/game/spell', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ word: given })
        });
        const data = await res.json();
        if (data.correct) {
            document.getElementById('spell-result').textContent = 'Correct! +50 HP';
            document.getElementById('spell-result').style.color = '#2ecc71';
        } else {
            document.getElementById('spell-result').textContent = 'Wrong! No energy recovered.';
            document.getElementById('spell-result').style.color = '#e74c3c';
        }
        setTimeout(() => {
            document.getElementById('spell-modal').style.display = 'none';
            spellActive = false;
            state = data.state;
            updateHUD();
        }, 800);
    } catch (e) {
        console.error('Spell error', e);
    }
}

function showGameOver() {
    document.getElementById('game-over-modal').style.display = 'flex';
    document.getElementById('final-score').textContent = state ? state.score : 0;
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

function initRoleSelection() {
    fetch('/api/roles').then(r => r.json()).then(roles => {
        const container = document.getElementById('role-options');
        roles.forEach(role => {
            const card = document.createElement('div');
            card.className = 'role-card';
            const shapeDiv = document.createElement('div');
            shapeDiv.className = `shape ${role.id}`;
            const name = document.createElement('h3');
            name.textContent = role.name;
            const desc = document.createElement('p');
            desc.textContent = role.desc;
            card.appendChild(shapeDiv);
            card.appendChild(name);
            card.appendChild(desc);
            card.addEventListener('click', () => startGame(role.id));
            container.appendChild(card);
        });
    });
}

async function startGame(roleId) {
    document.getElementById('role-selection').style.display = 'none';
    document.getElementById('game-container').style.display = 'block';

    const res = await fetch('/api/game/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: roleId })
    });
    const data = await res.json();
    gameId = data.gameId;
    state = data.state;
    updateHUD();
    draw();

    pollInterval = setInterval(sendUpdate, 1000 / 30);
}

function restartGame() {
    document.getElementById('game-over-modal').style.display = 'none';
    document.getElementById('game-container').style.display = 'none';
    document.getElementById('role-selection').style.display = 'block';
    state = null;
    gameId = null;
    spellActive = false;
    commandActive = false;
}

document.addEventListener('keydown', (e) => {
    if (spellActive) return;
    keys[e.key.toLowerCase()] = true;

    if (e.key === 'Enter' && !commandActive) {
        commandActive = true;
        document.getElementById('command-input-area').style.display = 'block';
        document.getElementById('command-input').focus();
    }
    if (e.key === 'Escape' && commandActive) {
        commandActive = false;
        document.getElementById('command-input-area').style.display = 'none';
        document.getElementById('command-input').value = '';
    }
});

document.addEventListener('keyup', (e) => {
    keys[e.key.toLowerCase()] = false;
});

canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
    mouseY = e.clientY - rect.top;
});

canvas.addEventListener('click', () => {
    if (state && state.running && !commandActive && !spellActive) {
        sendAction('attack', { mouseX, mouseY });
    }
});

document.getElementById('command-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        const cmd = document.getElementById('command-input').value.trim().toLowerCase();
        if (cmd === '/super') {
            sendAction('super');
        }
        commandActive = false;
        document.getElementById('command-input-area').style.display = 'none';
        document.getElementById('command-input').value = '';
    }
});

document.getElementById('spell-submit').addEventListener('click', submitSpell);
document.getElementById('spell-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') submitSpell();
});
document.getElementById('restart-btn').addEventListener('click', restartGame);

initRoleSelection();
