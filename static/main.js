// DOM 요소들
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const filesContainer = document.getElementById('files');
const convertBtn = document.getElementById('convertBtn');
const clearBtn = document.getElementById('clearBtn');
const progress = document.getElementById('progress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const result = document.getElementById('result');
const downloadLink = document.getElementById('downloadLink');
const qualitySlider = document.getElementById('quality');
const qualityValue = document.getElementById('qualityValue');

// 전역 변수
let selectedFiles = [];

// 품질 슬라이더 이벤트
qualitySlider.addEventListener('input', (e) => {
    qualityValue.textContent = e.target.value;
});

// 드래그 앤 드롭 이벤트
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
});

// 파일 선택 이벤트
fileInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
});

// 파일 처리 함수
function handleFiles(files) {
    // 이미지 파일만 필터링
    const imageFiles = files.filter(file => {
        return file.type.startsWith('image/');
    });
    
    if (imageFiles.length === 0) {
        alert('❌ 이미지 파일만 선택해주세요!');
        return;
    }
    
    // 기존 파일에 추가
    selectedFiles = [...selectedFiles, ...imageFiles];
    
    // 중복 제거 (파일명 기준)
    const uniqueFiles = [];
    const fileNames = new Set();
    
    selectedFiles.forEach(file => {
        if (!fileNames.has(file.name)) {
            fileNames.add(file.name);
            uniqueFiles.push(file);
        }
    });
    
    selectedFiles = uniqueFiles;
    updateFileList();
    updateButtons();
}

// 파일 리스트 업데이트
function updateFileList() {
    if (selectedFiles.length === 0) {
        fileList.style.display = 'none';
        return;
    }
    
    fileList.style.display = 'block';
    
    filesContainer.innerHTML = selectedFiles.map((file, index) => {
        const fileSize = formatFileSize(file.size);
        const fileIcon = getFileIcon(file.type);
        
        return `
            <div class="file-item">
                <div class="file-info">
                    <div class="file-icon">${fileIcon}</div>
                    <div class="file-details">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${fileSize}</div>
                    </div>
                </div>
                <button class="file-remove" onclick="removeFile(${index})">
                    🗑️ 제거
                </button>
            </div>
        `;
    }).join('');
}

// 파일 제거
function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
    updateButtons();
}

// 모든 파일 제거
clearBtn.addEventListener('click', () => {
    selectedFiles = [];
    fileInput.value = '';
    updateFileList();
    updateButtons();
    hideResult();
});

// 버튼 상태 업데이트
function updateButtons() {
    convertBtn.disabled = selectedFiles.length === 0;
}

// 파일 크기 포맷
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 파일 아이콘
function getFileIcon(fileType) {
    if (fileType.includes('jpeg') || fileType.includes('jpg')) return '🖼️';
    if (fileType.includes('png')) return '🎨';
    if (fileType.includes('gif')) return '🎭';
    if (fileType.includes('bmp')) return '🖌️';
    if (fileType.includes('tiff')) return '📸';
    if (fileType.includes('webp')) return '🌐';
    return '🖼️';
}

// PDF 변환
convertBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) {
        alert('❌ 변환할 이미지를 선택해주세요!');
        return;
    }
    
    // UI 상태 변경
    showProgress();
    convertBtn.disabled = true;
    
    try {
        // FormData 생성
        const formData = new FormData();
        
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        formData.append('quality', qualitySlider.value);
        
        // 변환 요청
        updateProgress(0, '변환 준비 중...');
        
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        updateProgress(100, '변환 완료!');
        
        // PDF 다운로드
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        showResult(url);
        
    } catch (error) {
        console.error('변환 오류:', error);
        alert('❌ 변환 중 오류가 발생했습니다: ' + error.message);
        hideProgress();
    } finally {
        convertBtn.disabled = false;
    }
});

// 진행 상황 표시
function showProgress() {
    progress.style.display = 'block';
    result.style.display = 'none';
}

function updateProgress(percent, text) {
    progressFill.style.width = percent + '%';
    progressText.textContent = text;
}

function hideProgress() {
    progress.style.display = 'none';
}

// 결과 표시
function showResult(downloadUrl) {
    hideProgress();
    result.style.display = 'block';
    
    // 다운로드 링크 설정
    downloadLink.href = downloadUrl;
    
    // 파일명 생성 (현재 시간 기반)
    const now = new Date();
    const timestamp = now.toISOString().slice(0, 19).replace(/[:-]/g, '');
    downloadLink.download = `converted_images_${timestamp}.pdf`;
    
    // 자동 다운로드
    downloadLink.click();
}

function hideResult() {
    result.style.display = 'none';
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    updateButtons();
    
    // 드래그 앤 드롭 전역 방지 (페이지 전체에서)
    document.addEventListener('dragover', (e) => {
        e.preventDefault();
    });
    
    document.addEventListener('drop', (e) => {
        e.preventDefault();
    });
});