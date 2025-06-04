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

// 품질 슬라이더 이벤트
qualitySlider.addEventListener('input', (e) => {
    qualityValue.textContent = e.target.value;
});

// 업로드 영역 클릭 이벤트 - 더 단순하게
uploadArea.addEventListener('click', (e) => {
    console.log('업로드 영역 클릭');
    if (!isConverting) {
        fileInput.click();
    }
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    if (!isConverting) {
        uploadArea.classList.add('dragover');
    }
});

uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    if (!isConverting) {
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    }
});

// 파일 선택 이벤트 - 첫 버전 방식
fileInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
    // 파일 처리 후 input 초기화
    e.target.value = '';
});

// 파일 처리 함수 - 첫 버전 방식 + 개선
function handleFiles(files) {
    console.log('파일 처리 시작:', files.length);
    
    // 이미지 파일만 필터링
    const imageFiles = files.filter(file => {
        return file.type.startsWith('image/');
    });
    
    if (imageFiles.length === 0) {
        alert('❌ 이미지 파일만 선택해주세요!');
        return;
    }
    
    console.log('이미지 파일 필터링:', imageFiles.length);
    
    // 기존 파일에 추가
    selectedFiles = [...selectedFiles, ...imageFiles];
    
    // 중복 제거 (파일명 + 크기 기준)
    const uniqueFiles = [];
    const fileSignatures = new Set();
    
    selectedFiles.forEach(file => {
        const signature = `${file.name}_${file.size}_${file.lastModified}`;
        if (!fileSignatures.has(signature)) {
            fileSignatures.add(signature);
            uniqueFiles.push(file);
        }
    });
    
    selectedFiles = uniqueFiles;
    console.log('최종 파일 수:', selectedFiles.length);
    
    updateFileList();
    updateButtons();
    updateConvertOptions();
}

// 파일 리스트 업데이트 - 새 버전 스타일
function updateFileList() {
    if (selectedFiles.length === 0) {
        fileList.style.display = 'none';
        convertOptions.style.display = 'none';
        actions.style.display = 'none';
        return;
    }
    
    fileList.style.display = 'block';
    convertOptions.style.display = 'block';
    actions.style.display = 'block';
    
    filesContainer.innerHTML = selectedFiles.map((file, index) => {
        const fileSize = formatFileSize(file.size);
        
        return `
            <div class="file-item">
                <div class="file-info">
                    <div class="file-name">📄 ${file.name}</div>
                    <div class="file-size">${fileSize}</div>
                </div>
                <button class="file-remove" onclick="removeFile(${index})" title="파일 제거">
                    ×
                </button>
            </div>
        `;
    }).join('');
    
    hideResult();

    // 기본 파일명 설정
    updateDefaultFilename();
}

// 변환 옵션 업데이트
function updateConvertOptions() {
    // 여러 파일일 때만 변환 타입 선택 표시
    if (convertTypeSection) {
        convertTypeSection.style.display = selectedFiles.length > 1 ? 'block' : 'none';
    }
    
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

// 변환 타입 변경 이벤트
document.querySelectorAll('input[name="convertType"]').forEach(radio => {
    radio.addEventListener('change', updateFilenameExtension);
});

// 파일명 유효성 검사
if (outputFilename) {
    outputFilename.addEventListener('input', function() {
        const filename = this.value.trim();
        const invalidChars = /[<>:"/\\|?*]/g;
        
        if (invalidChars.test(filename)) {
            this.value = filename.replace(invalidChars, '');
        }
    });
}

// 파일 제거
function removeFile(index) {
    console.log('파일 제거:', index, selectedFiles[index]?.name);
    selectedFiles.splice(index, 1);
    updateFileList();
    updateButtons();
    updateConvertOptions();
    hideResult();
}

// 모든 파일 제거 - 첫 버전 방식
clearBtn.addEventListener('click', () => {
    console.log('파일 전체 제거');
    selectedFiles = [];
    fileInput.value = '';
    updateFileList();
    updateButtons();
    hideResult();
});

// 버튼 상태 업데이트 - 첫 버전 방식
function updateButtons() {
    if (convertBtn) {
        convertBtn.disabled = selectedFiles.length === 0 || isConverting;
    }
}

// 파일 크기 포맷 - 첫 버전 방식
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// PDF 변환 - 첫 버전 방식 + 새 기능들
convertBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0 || isConverting) {
        alert('❌ 변환할 이미지를 선택해주세요!');
        return;
    }
    
    isConverting = true;
    
    // UI 상태 변경
    showProgress();
    convertBtn.disabled = true;
    
    try {
        // FormData 생성
        const formData = new FormData();
        
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
        
        // 변환 요청
        updateProgress(30, '서버로 업로드 중...');
        
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
        alert('❌ 변환 중 오류가 발생했습니다: ' + error.message);
        hideProgress();
    } finally {
        isConverting = false;
        convertBtn.disabled = false;
    }
});

// 진행 상황 표시 - 첫 버전 방식
function showProgress() {
    if (progress) progress.style.display = 'block';
    if (result) result.style.display = 'none';
}

function updateProgress(percent, text) {
    if (progressFill) progressFill.style.width = percent + '%';
    if (progressText) progressText.textContent = text;
}

function hideProgress() {
    if (progress) progress.style.display = 'none';
}

// 결과 표시
function showResult(message) {
    setTimeout(() => {
        hideProgress();
        if (result) {
            result.style.display = 'block';
            const resultTextElement = result.querySelector('.result-text');
            if (resultTextElement) {
                resultTextElement.textContent = message;
            }
        }
    }, 500);
}

function hideResult() {
    if (result) result.style.display = 'none';
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

// 페이지 로드 시 초기화 - 첫 버전 방식
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