// 전역 변수
let selectedFiles = [];
let isConverting = false;

// DOM 요소들
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const filesContainer = document.getElementById('files');
const convertOptions = document.getElementById('convertOptions');
const convertTypeSection = document.getElementById('convertTypeSection');
const outputFilename = document.getElementById('outputFilename');
const filenameExtension = document.getElementById('filenameExtension');
const actions = document.getElementById('actions');
const convertBtn = document.getElementById('convertBtn');
const clearBtn = document.getElementById('clearBtn');
const progress = document.getElementById('progress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const result = document.getElementById('result');
const downloadLink = document.getElementById('downloadLink');
const qualitySlider = document.getElementById('quality');
const qualityValue = document.getElementById('qualityValue');

// 이벤트 리스너 등록
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    updateQualityDisplay();
});

function initializeEventListeners() {
    // 파일 입력 이벤트 - 수정됨
    fileInput.addEventListener('change', handleFileSelect);
    
    // 드래그 앤 드롭 이벤트
    uploadArea.addEventListener('click', () => {
        // 변환 중이 아닐 때만 파일 선택 가능
        if (!isConverting) {
            fileInput.click();
        }
    });
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleFileDrop);
    
    // 버튼 이벤트
    convertBtn.addEventListener('click', convertToPDF);
    clearBtn.addEventListener('click', clearFiles);
    
    // 변환 타입 변경 이벤트
    document.querySelectorAll('input[name="convertType"]').forEach(radio => {
        radio.addEventListener('change', updateFilenameExtension);
    });
    
    // 품질 슬라이더 이벤트
    qualitySlider.addEventListener('input', updateQualityDisplay);
    
    // 파일명 입력 이벤트
    outputFilename.addEventListener('input', validateFilename);
}

// 드래그 오버 처리
function handleDragOver(e) {
    e.preventDefault();
    if (!isConverting) {
        uploadArea.classList.add('dragover');
    }
}

// 드래그 리브 처리
function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

// 파일 드롭 처리
function handleFileDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    if (isConverting) return;
    
    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
}

// 파일 선택 처리 - 완전히 수정됨
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    console.log('파일 선택 이벤트:', files.length, files.map(f => f.name));
    
    if (files.length > 0) {
        addFiles(files);
    }
    
    // 파일 처리가 완료된 후 input을 리셋하지 않음
    // 대신 다음 선택을 위해 준비만 함
}

// 파일 추가 - 수정됨
function addFiles(files) {
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length === 0) {
        alert('이미지 파일만 업로드할 수 있습니다.');
        return;
    }
    
    console.log('이미지 파일 필터링:', imageFiles.length, '개');
    
    // 중복 파일 제거
    let addedCount = 0;
    imageFiles.forEach(file => {
        const isDuplicate = selectedFiles.some(existing => 
            existing.name === file.name && 
            existing.size === file.size && 
            existing.lastModified === file.lastModified
        );
        
        if (!isDuplicate) {
            selectedFiles.push(file);
            addedCount++;
            console.log('파일 추가:', file.name);
        } else {
            console.log('중복 파일 건너뜀:', file.name);
        }
    });
    
    console.log('총 파일 수:', selectedFiles.length, '(새로 추가:', addedCount + ')');
    
    // UI 업데이트
    updateUI();
    
    // 파일 선택 후 input을 다음 선택을 위해 준비
    // 약간의 지연 후 초기화 (브라우저 이벤트 처리 완료 대기)
    setTimeout(() => {
        if (fileInput && !isConverting) {
            fileInput.value = '';
            console.log('파일 input 초기화 완료');
        }
    }, 200);
}

// UI 업데이트
function updateUI() {
    const hasFiles = selectedFiles.length > 0;
    
    console.log('UI 업데이트 시작:', hasFiles, selectedFiles.length);
    
    // 요소들 확인 및 표시/숨김
    const elements = {
        fileList: document.getElementById('fileList'),
        convertOptions: document.getElementById('convertOptions'),
        actions: document.getElementById('actions'),
        result: document.getElementById('result'),
        progress: document.getElementById('progress')
    };
    
    // 파일 관련 UI 표시/숨김
    if (elements.fileList) {
        elements.fileList.style.display = hasFiles ? 'block' : 'none';
    }
    
    if (elements.convertOptions) {
        elements.convertOptions.style.display = hasFiles ? 'block' : 'none';
    }
    
    if (elements.actions) {
        elements.actions.style.display = hasFiles ? 'block' : 'none';
    }
    
    // 파일 목록 업데이트
    if (hasFiles) {
        displayFiles();
        updateConvertOptions();
        updateDefaultFilename();
    }
    
    // 결과 및 진행률 숨김
    if (elements.result) elements.result.style.display = 'none';
    if (elements.progress) elements.progress.style.display = 'none';
    
    console.log('UI 업데이트 완료');
}

// 파일 목록 표시
function displayFiles() {
    if (!filesContainer) return;
    
    filesContainer.innerHTML = selectedFiles.map((file, index) => `
        <div class="file-item">
            <div class="file-info">
                <div class="file-name">📄 ${file.name}</div>
                <div class="file-size">${formatFileSize(file.size)}</div>
            </div>
            <button class="file-remove" onclick="removeFile(${index})" title="파일 제거">
                ×
            </button>
        </div>
    `).join('');
}

// 변환 옵션 업데이트
function updateConvertOptions() {
    if (!convertTypeSection) return;
    
    // 여러 파일일 때만 변환 타입 선택 표시
    convertTypeSection.style.display = selectedFiles.length > 1 ? 'block' : 'none';
    
    // 단일 파일일 때는 자동으로 merged 선택
    if (selectedFiles.length === 1) {
        const mergedRadio = document.querySelector('input[name="convertType"][value="merged"]');
        if (mergedRadio) {
            mergedRadio.checked = true;
        }
    }
    
    updateFilenameExtension();
}

// 기본 파일명 설정
function updateDefaultFilename() {
    if (!outputFilename || selectedFiles.length === 0) {
        return;
    }
    
    if (selectedFiles.length === 1) {
        // 단일 파일: 원본 파일명 (확장자 제외)
        const baseName = selectedFiles[0].name.replace(/\.[^/.]+$/, '');
        outputFilename.value = baseName;
    } else {
        // 여러 파일: 첫 번째 파일명 기반
        const firstName = selectedFiles[0].name.replace(/\.[^/.]+$/, '');
        outputFilename.value = `${firstName}_and_${selectedFiles.length - 1}_more`;
    }
}

// 파일명 확장자 업데이트
function updateFilenameExtension() {
    if (!filenameExtension) return;
    
    const convertTypeRadio = document.querySelector('input[name="convertType"]:checked');
    const convertType = convertTypeRadio ? convertTypeRadio.value : 'merged';
    
    if (convertType === 'individual' && selectedFiles.length > 1) {
        filenameExtension.textContent = '.zip';
    } else {
        filenameExtension.textContent = '.pdf';
    }
}

// 파일명 유효성 검사
function validateFilename() {
    if (!outputFilename) return;
    
    const filename = outputFilename.value.trim();
    const invalidChars = /[<>:"/\\|?*]/g;
    
    if (invalidChars.test(filename)) {
        outputFilename.value = filename.replace(invalidChars, '');
    }
}

// 파일 제거
function removeFile(index) {
    console.log('파일 제거:', index, selectedFiles[index]?.name);
    selectedFiles.splice(index, 1);
    updateUI();
}

// 모든 파일 제거
function clearFiles() {
    console.log('파일 전체 제거');
    selectedFiles = [];
    
    // input 초기화
    if (fileInput && !isConverting) {
        fileInput.value = '';
    }
    
    updateUI();
}

// 품질 표시 업데이트
function updateQualityDisplay() {
    if (qualityValue && qualitySlider) {
        qualityValue.textContent = qualitySlider.value;
    }
}

// PDF 변환
async function convertToPDF() {
    if (selectedFiles.length === 0 || isConverting) {
        return;
    }
    
    isConverting = true;
    
    try {
        // UI 상태 변경
        showProgress('변환 준비 중...');
        if (convertBtn) convertBtn.disabled = true;
        
        // FormData 생성
        const formData = new FormData();
        
        // 파일들 추가
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        // 옵션 추가
        const convertTypeElement = document.querySelector('input[name="convertType"]:checked');
        const convertType = convertTypeElement ? convertTypeElement.value : 'merged';
        const filename = outputFilename ? outputFilename.value.trim() || 'converted' : 'converted';
        const quality = qualitySlider ? qualitySlider.value : 95;
        
        formData.append('convert_type', convertType);
        formData.append('filename', filename);
        formData.append('quality', quality);
        
        console.log('전송 데이터:');
        console.log('- 파일 수:', selectedFiles.length);
        console.log('- 변환 타입:', convertType);
        console.log('- 파일명:', filename);
        console.log('- 품질:', quality);
        
        // FormData 내용 확인
        for (let [key, value] of formData.entries()) {
            if (key === 'files') {
                console.log(`- ${key}:`, value.name);
            } else {
                console.log(`- ${key}:`, value);
            }
        }
        
        // 진행률 업데이트
        updateProgress(30, '서버로 업로드 중...');
        
        // API 호출
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });
        
        updateProgress(60, 'PDF 변환 중...');
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `서버 오류: ${response.status}`);
        }
        
        updateProgress(90, '다운로드 준비 중...');
        
        // 응답 처리
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            // ZIP 파일 다운로드 URL 응답
            const result = await response.json();
            console.log('JSON 응답:', result);
            
            if (result.download_url) {
                updateProgress(95, 'ZIP 파일 다운로드 중...');
                const downloadResponse = await fetch(result.download_url);
                const blob = await downloadResponse.blob();
                const finalFilename = result.filename || `${filename}.zip`;
                downloadFile(blob, finalFilename);
            }
        } else {
            // 직접 PDF 파일 응답
            const blob = await response.blob();
            const finalFilename = `${filename}.pdf`;
            downloadFile(blob, finalFilename);
        }
        
        updateProgress(100, '변환 완료!');
        showResult('PDF 변환이 완료되었습니다!');
        
    } catch (error) {
        console.error('변환 오류:', error);
        hideProgress();
        alert(`변환 중 오류가 발생했습니다: ${error.message}`);
    } finally {
        isConverting = false;
        if (convertBtn) convertBtn.disabled = false;
    }
}

// 진행률 표시
function showProgress(message) {
    if (progress) progress.style.display = 'block';
    if (result) result.style.display = 'none';
    if (progressText) progressText.textContent = message;
    if (progressFill) progressFill.style.width = '0%';
}

// 진행률 업데이트
function updateProgress(percent, message) {
    if (progressFill) progressFill.style.width = `${percent}%`;
    if (progressText) progressText.textContent = message;
}

// 진행률 숨김
function hideProgress() {
    if (progress) progress.style.display = 'none';
}

// 결과 표시
function showResult(message) {
    setTimeout(() => {
        if (progress) progress.style.display = 'none';
        if (result) {
            result.style.display = 'block';
            const resultTextElement = result.querySelector('.result-text');
            if (resultTextElement) {
                resultTextElement.textContent = message;
            }
        }
    }, 500);
}

// 파일 다운로드
function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    console.log('파일 다운로드 완료:', filename);
}

// 파일 크기 포맷
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 드래그 방지 (전체 페이지)
document.addEventListener('dragover', function(e) {
    e.preventDefault();
});

document.addEventListener('drop', function(e) {
    e.preventDefault();
});