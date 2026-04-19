// Состояние сессии
const state = {
    sessionId: null,
    vehicle: null,
    step: 1,
    videoUploaded: false,
    audioUploaded: false,
    obdSubmitted: false,
};

const API_BASE = '/api';

const contentEl = document.getElementById('app-content');
const notificationEl = document.getElementById('notification');
const stepIndicators = {
    1: document.getElementById('step1-indicator'),
    2: document.getElementById('step2-indicator'),
    3: document.getElementById('step3-indicator'),
    4: document.getElementById('step4-indicator'),
};

// Утилита уведомлений
function showNotification(message, isError = false) {
    notificationEl.textContent = message;
    notificationEl.style.background = isError ? '#dc2626' : '#1e293b';
    notificationEl.classList.remove('hidden');
    setTimeout(() => notificationEl.classList.add('hidden'), 4000);
}

function updateStepIndicators() {
    for (let i = 1; i <= 4; i++) {
        const el = stepIndicators[i];
        el.classList.remove('active', 'completed');
        if (i === state.step) el.classList.add('active');
        else if (i < state.step) el.classList.add('completed');
    }
}

// ========== ШАГ 1: Ручной ввод (без фото) ==========
function renderStep1() {
    let html = `
        <div class="card">
            <h2>Шаг 1: Данные автомобиля и описание неисправности</h2>
            <form id="manual-form">
                <div class="form-group">
                    <label>Марка *</label>
                    <input type="text" id="make" required placeholder="Toyota" autocomplete="off">
                </div>
                <div class="form-group">
                    <label>Модель *</label>
                    <input type="text" id="model" required placeholder="Camry" autocomplete="off">
                </div>
                <div class="form-group">
                    <label>Год выпуска *</label>
                    <input type="number" id="year" required min="1950" max="2026" placeholder="2020">
                </div>
                <div class="form-group">
                    <label>Госномер (опционально)</label>
                    <input type="text" id="plate-number" placeholder="А123ВС177" autocomplete="off">
                </div>
                <div class="form-group">
                    <label>Опишите неисправность (что беспокоит, когда проявляется) *</label>
                    <textarea id="description" rows="4" required placeholder="Например: двигатель троит на холостых, слышен свист при разгоне, загорелся Check Engine..."></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Продолжить</button>
            </form>
        </div>
    `;
    contentEl.innerHTML = html;

    document.getElementById('manual-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            make: document.getElementById('make').value.trim(),
            model: document.getElementById('model').value.trim(),
            year: parseInt(document.getElementById('year').value),
            plate_number: document.getElementById('plate-number').value.trim() || null,
            description: document.getElementById('description').value.trim(),
        };
        try {
            const response = await fetch(`${API_BASE}/vehicle/manual`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Ошибка сервера');
            const result = await response.json();
            state.sessionId = result.session_id;
            state.vehicle = data;
            state.step = 2;
            renderStep2();
            updateStepIndicators();
            showNotification('Данные сохранены');
        } catch (err) {
            showNotification('Ошибка сохранения', true);
        }
    });
}

// ========== ШАГ 2: Загрузка видео/аудио ==========
function renderStep2() {
    let html = `
        <div class="card">
            <h2>Шаг 2: Загрузите материалы</h2>
            <p>Можно загрузить видео внешнего вида и/или аудиозапись работы двигателя.</p>
            <div class="flex-row">
                <div class="flex-col">
                    <h3>🎥 Видео</h3>
                    <div class="dropzone" id="video-dropzone">
                        <p>Выберите или перетащите видеофайл</p>
                        <input type="file" id="video-input" accept="video/*" style="display: none;">
                    </div>
                    <div id="video-status" class="upload-status">${state.videoUploaded ? '✅ Загружено' : ''}</div>
                </div>
                <div class="flex-col">
                    <h3>🎵 Аудио</h3>
                    <div class="dropzone" id="audio-dropzone">
                        <p>Выберите или перетащите аудиофайл</p>
                        <input type="file" id="audio-input" accept="audio/*" style="display: none;">
                    </div>
                    <div id="audio-status" class="upload-status">${state.audioUploaded ? '✅ Загружено' : ''}</div>
                </div>
            </div>
            <button class="btn btn-primary" id="next-step-btn" ${!state.videoUploaded && !state.audioUploaded ? 'disabled' : ''}>Продолжить</button>
        </div>
    `;
    contentEl.innerHTML = html;

    function setupDropzone(dropzoneId, inputId, type) {
        const dropzone = document.getElementById(dropzoneId);
        const input = document.getElementById(inputId);
        dropzone.addEventListener('click', () => input.click());
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('active');
        });
        dropzone.addEventListener('dragleave', () => dropzone.classList.remove('active'));
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('active');
            const file = e.dataTransfer.files[0];
            if (file) handleFileUpload(file, type);
        });
        input.addEventListener('change', (e) => {
            if (e.target.files[0]) handleFileUpload(e.target.files[0], type);
        });
    }

    async function handleFileUpload(file, type) {
        const statusEl = document.getElementById(`${type}-status`);
        statusEl.innerHTML = '<span class="loader"></span> Загрузка...';
        const formData = new FormData();
        formData.append('file', file);
        try {
            const response = await fetch(`${API_BASE}/upload/${type}/${state.sessionId}`, {
                method: 'POST',
                body: formData
            });
            if (response.ok) {
                statusEl.innerHTML = '✅ Загружено (идёт обработка)';
                if (type === 'video') state.videoUploaded = true;
                else state.audioUploaded = true;
                document.getElementById('next-step-btn').disabled = false;
                showNotification(`${type === 'video' ? 'Видео' : 'Аудио'} загружено`);
            } else {
                throw new Error();
            }
        } catch (err) {
            statusEl.innerHTML = '❌ Ошибка загрузки';
            showNotification('Ошибка загрузки', true);
        }
    }

    setupDropzone('video-dropzone', 'video-input', 'video');
    setupDropzone('audio-dropzone', 'audio-input', 'audio');

    document.getElementById('next-step-btn').addEventListener('click', () => {
        state.step = 3;
        renderStep3();
        updateStepIndicators();
    });
}

// ========== ШАГ 3: OBD-код (опционально) ==========
function renderStep3() {
    let html = `
        <div class="card">
            <h2>Шаг 3: Код ошибки OBD-II (если есть)</h2>
            <p>Если у вас есть код ошибки (например, P0171), введите его.</p>
            <form id="obd-form">
                <div class="form-group">
                    <input type="text" id="obd-code" placeholder="P0171" pattern="[Pp][0-9]{4}" title="Формат: PXXXX">
                </div>
                <div class="btn-group">
                    <button type="submit" class="btn btn-primary">Расшифровать</button>
                    <button type="button" class="btn btn-secondary" id="skip-obd">Пропустить</button>
                </div>
            </form>
            <div id="obd-result"></div>
        </div>
    `;
    contentEl.innerHTML = html;

    document.getElementById('obd-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const code = document.getElementById('obd-code').value.trim().toUpperCase();
        if (!code) return;
        try {
            const response = await fetch(`${API_BASE}/obd/${state.sessionId}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code})
            });
            const result = await response.json();
            document.getElementById('obd-result').innerHTML = `
                <div class="result-box">
                    <strong>${code}:</strong> ${result.description}
                </div>
                <button class="btn btn-success" id="to-step4">Продолжить к диагностике</button>
            `;
            state.obdSubmitted = true;
            document.getElementById('to-step4').addEventListener('click', () => {
                state.step = 4;
                renderStep4();
                updateStepIndicators();
            });
            showNotification('Код расшифрован');
        } catch (err) {
            showNotification('Ошибка расшифровки', true);
        }
    });

    document.getElementById('skip-obd').addEventListener('click', () => {
        state.step = 4;
        renderStep4();
        updateStepIndicators();
    });
}

// ========== ШАГ 4: Генерация отчёта ==========
function renderStep4() {
    let html = `
        <div class="card">
            <h2>Шаг 4: Диагностический отчёт</h2>
            <p>Нажмите кнопку, чтобы ИИ проанализировал все данные и выдал заключение.</p>
            <button class="btn btn-success" id="generate-report-btn">🔍 Сгенерировать отчёт</button>
            <div id="report-container"></div>
        </div>
    `;
    contentEl.innerHTML = html;

    document.getElementById('generate-report-btn').addEventListener('click', async () => {
        const btn = document.getElementById('generate-report-btn');
        btn.disabled = true;
        btn.innerHTML = '<span class="loader"></span> Анализируем... (может занять до 30 секунд)';
        try {
            const response = await fetch(`${API_BASE}/diagnostic/generate/${state.sessionId}`, {
                method: 'POST'
            });
            const result = await response.json();
            document.getElementById('report-container').innerHTML = `
                <div class="result-box">
                    <h3>Результат диагностики</h3>
                    <div style="white-space: pre-wrap;">${result.report}</div>
                </div>
            `;
            btn.style.display = 'none';
            showNotification('Отчёт готов!');
        } catch (err) {
            showNotification('Ошибка генерации отчёта', true);
            btn.disabled = false;
            btn.textContent = '🔍 Сгенерировать отчёт';
        }
    });
}

// ========== Инициализация ==========
function init() {
    renderStep1();
    updateStepIndicators();
}

init();