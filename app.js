const templates = [
  {
    id: 'dynamic-story',
    name: 'استوری پویای شبکه اجتماعی',
    description: 'حرکت سریع متن و گرادیان زنده',
    color: '#ff4d79',
    rotate: 12,
    pathText: 'حرکت موزون متن روی مسیر',
  },
  {
    id: 'corporate-intro',
    name: 'معرفی رسمی برند',
    description: 'ورود آرام لوگو و تایم‌لاین لایه‌ای',
    color: '#22c55e',
    rotate: 6,
    pathText: 'حرکت نرم برای برند رسمی',
  },
  {
    id: 'festival-opener',
    name: 'شروع رویداد و جشنواره',
    description: 'انفجار رنگ و پرسپکتیو سه‌بعدی',
    color: '#6366f1',
    rotate: 16,
    pathText: 'شروع باشکوه برای جشنواره',
  },
];

const messages = document.getElementById('messages');
const templateSelect = document.getElementById('templateSelect');
const textSample = document.getElementById('textSample');
const gradientInput = document.getElementById('gradientInput');
const rotateRange = document.getElementById('rotateRange');
const pathText = document.getElementById('pathText');
const calligraphyFont = document.getElementById('calligraphyFont');
const preview = document.getElementById('preview');
const previewLabel = document.getElementById('previewLabel');
const timelineTracks = document.getElementById('timelineTracks');
const waveform = document.getElementById('waveform');
const batchStatus = document.getElementById('batchStatus');

let userTemplates = JSON.parse(localStorage.getItem('userTemplates') || '[]');
let scenes = [
  { id: 1, name: 'صحنه ۱', duration: 4 },
  { id: 2, name: 'صحنه ۲', duration: 6 },
];

function showMessage(text, type = 'info') {
  const div = document.createElement('div');
  div.className = `message ${type === 'error' ? 'error' : ''}`;
  div.textContent = text;
  messages.prepend(div);
}

function populateTemplates() {
  const combined = [...templates, ...userTemplates];
  templateSelect.innerHTML = '';
  combined.forEach((template) => {
    const option = document.createElement('option');
    option.value = template.id;
    option.textContent = template.name;
    templateSelect.appendChild(option);
  });
}

function applyTemplate() {
  const selected = [...templates, ...userTemplates].find(
    (t) => t.id === templateSelect.value
  );
  if (!selected) return;

  textSample.style.backgroundImage = `linear-gradient(90deg, ${selected.color}, #111827)`;
  rotateRange.value = selected.rotate;
  pathText.textContent = selected.pathText;
  textSample.style.transform = `rotateY(${selected.rotate}deg) rotateX(5deg)`;
  showMessage(`الگو «${selected.name}» با موفقیت اعمال شد.`, 'info');
}

function saveTemplate() {
  const name = document.getElementById('customTemplateName').value.trim();
  if (!name) {
    return showMessage('لطفاً برای الگوی شخصی یک نام انتخاب کنید.', 'error');
  }
  const id = `user-${Date.now()}`;
  const newTemplate = {
    id,
    name,
    description: 'الگوی ذخیره‌شده توسط کاربر',
    color: gradientInput.value,
    rotate: Number(rotateRange.value),
    pathText: pathText.textContent,
  };
  userTemplates.push(newTemplate);
  localStorage.setItem('userTemplates', JSON.stringify(userTemplates));
  populateTemplates();
  templateSelect.value = id;
  showMessage('الگوی شما ذخیره شد و آمادهٔ استفاده است.', 'info');
}

function toggleQuality() {
  preview.classList.toggle('low-quality');
  preview.classList.toggle('high-quality');
  const isHigh = preview.classList.contains('high-quality');
  previewLabel.textContent = isHigh
    ? 'پیش‌نمایش دقیق و باکیفیت'
    : 'پیش‌نمایش کم‌کیفیت برای سرعت بالاتر';
}

function playAnimation() {
  textSample.style.transform = `rotateY(${rotateRange.value}deg) rotateX(5deg) translateY(-6px)`;
  preview.classList.add('pulse');
  setTimeout(() => {
    textSample.style.transform = `rotateY(${rotateRange.value}deg) rotateX(5deg)`;
    preview.classList.remove('pulse');
  }, 650);
  showMessage('انیمیشن بلافاصله برای بررسی اجرا شد.', 'info');
}

function renderTimeline() {
  timelineTracks.innerHTML = '';
  scenes.forEach((scene) => {
    const row = document.createElement('div');
    row.className = 'track';
    row.innerHTML = `
      <span>${scene.name}</span>
      <input type="range" min="2" max="15" value="${scene.duration}" aria-label="مدت صحنه" />
      <span>${scene.duration} ثانیه</span>
    `;
    const range = row.querySelector('input');
    range.addEventListener('input', (e) => {
      scene.duration = Number(e.target.value);
      row.lastElementChild.textContent = `${scene.duration} ثانیه`;
    });
    timelineTracks.appendChild(row);
  });
}

function updateTextEffects() {
  const gradient = gradientInput.value;
  const rotate = rotateRange.value;
  textSample.style.backgroundImage = `linear-gradient(135deg, ${gradient}, #22d3ee, #a855f7)`;
  textSample.style.transform = `rotateY(${rotate}deg) rotateX(6deg)`;
  textSample.style.fontFamily = calligraphyFont.value;
}

function renderWaveform() {
  const ctx = waveform.getContext('2d');
  ctx.clearRect(0, 0, waveform.width, waveform.height);
  ctx.beginPath();
  ctx.moveTo(0, waveform.height / 2);
  for (let x = 0; x < waveform.width; x += 8) {
    const y = waveform.height / 2 + Math.sin(x / 20) * 20 + Math.random() * 6;
    ctx.lineTo(x, y);
  }
  ctx.strokeStyle = '#0ea5e9';
  ctx.lineWidth = 2;
  ctx.stroke();
}

function startBatchProcessing() {
  batchStatus.innerHTML = '';
  const count = Number(document.getElementById('batchCount').value);
  for (let i = 1; i <= count; i++) {
    const item = document.createElement('div');
    item.className = 'status-item';
    item.textContent = `ویدیو ${i}: در حال پردازش سریع...`;
    batchStatus.appendChild(item);
    setTimeout(() => {
      item.textContent = `ویدیو ${i}: آمادهٔ خروجی با بهترین کیفیت`;
    }, 800 * i);
  }
  showMessage('پردازش چندگانه شروع شد و وضعیت در حال نمایش است.', 'info');
}

function sendToCloud() {
  document.getElementById('cloudStatus').textContent = 'ارسال به صف رندر';
  showMessage('فایل‌ها برای رندر ابری در صف قرار گرفتند.', 'info');
  setTimeout(() => {
    document.getElementById('cloudStatus').textContent = 'آماده';
    showMessage('نتیجهٔ رندر ابری آماده شد و قابل دانلود است.', 'info');
  }, 1500);
}

function checkCompatibility() {
  const format = document.getElementById('formatSelect').value;
  if (['mp4', 'webm', 'mov'].includes(format)) {
    showMessage(`فرمت ${format.toUpperCase()} با سیستم شما سازگار است.`, 'info');
  } else {
    showMessage('فرمت انتخابی پشتیبانی نمی‌شود. لطفاً فرمت دیگری برگزینید.', 'error');
  }
}

function simulateError() {
  showMessage('مشکلی در بارگذاری فایل رخ داد. لطفاً مسیر را بررسی کنید.', 'error');
  showMessage('فونت موردنظر یافت نشد؛ در حال استفاده از جایگزین مناسب.', 'error');
}

function monitorMemory() {
  const usage = Math.round(10 + Math.random() * 20);
  document.getElementById('memoryUsage').textContent = `${usage}٪`;
}

function updateVoiceSync() {
  const offset = document.getElementById('voiceOffset').value;
  showMessage(`هماهنگی صدا با تایم‌لاین به ${offset} ثانیه تنظیم شد.`, 'info');
}

function setupEventListeners() {
  document.getElementById('applyTemplate').addEventListener('click', applyTemplate);
  document.getElementById('saveTemplate').addEventListener('click', saveTemplate);
  document.getElementById('toggleQuality').addEventListener('click', toggleQuality);
  document.getElementById('playAnimation').addEventListener('click', playAnimation);
  gradientInput.addEventListener('input', updateTextEffects);
  rotateRange.addEventListener('input', updateTextEffects);
  calligraphyFont.addEventListener('change', updateTextEffects);
  document.getElementById('startBatch').addEventListener('click', startBatchProcessing);
  document.getElementById('cloudRender').addEventListener('click', sendToCloud);
  document.getElementById('checkCompatibility').addEventListener('click', checkCompatibility);
  document.getElementById('simulateError').addEventListener('click', simulateError);
  document.getElementById('addScene').addEventListener('click', () => {
    scenes.push({ id: Date.now(), name: `صحنه ${scenes.length + 1}`, duration: 5 });
    renderTimeline();
  });
  document.getElementById('voiceOffset').addEventListener('change', updateVoiceSync);
}

function init() {
  populateTemplates();
  renderTimeline();
  renderWaveform();
  setupEventListeners();
  updateTextEffects();
  showMessage('به استودیو موشن گرافیک خوش آمدید. همه‌چیز برای شروع آماده است.');
  setInterval(monitorMemory, 2500);
}

document.addEventListener('DOMContentLoaded', init);
