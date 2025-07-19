document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const fileInput = document.getElementById('file-input');
    const startBtn = document.getElementById('start-btn');
    const addRowBtn = document.getElementById('add-row-btn');
    const tableBody = document.getElementById('table-body');
    const footer = document.querySelector('footer');
    
    const uploadSection = document.getElementById('upload-section');
    const flashcardSection = document.getElementById('flashcard-section');
    const spellingSection = document.getElementById('spelling-section');
    const summarySection = document.getElementById('summary-section');

    const navFlashcard = document.getElementById('nav-flashcard');
    const navSpelling = document.getElementById('nav-spelling');

    // Flashcard Elements
    const flashcardWord = document.getElementById('flashcard-word');
    const option1 = document.getElementById('option1');
    const option2 = document.getElementById('option2');
    const flashcardResult = document.getElementById('flashcard-result');

    // Spelling Elements
    const spellingTranslation = document.getElementById('spelling-translation');
    const spellingInput = document.getElementById('spelling-input');
    const checkSpellingBtn = document.getElementById('check-spelling-btn');
    const spellingResult = document.getElementById('spelling-result');

    // Summary Elements
    const accuracyText = document.getElementById('accuracy-text');
    const restartBtn = document.getElementById('restart-btn');

    // App State
    let words = [];
    let currentWordIndex = 0;
    let correctAnswers = 0;
    let currentMode = 'flashcard'; // 'flashcard' or 'spelling'
    let shuffledWords = [];

    // --- Event Listeners ---
    startBtn.addEventListener('click', startGame);
    addRowBtn.addEventListener('click', addTableRow);
    navFlashcard.addEventListener('click', () => switchMode('flashcard'));
    navSpelling.addEventListener('click', () => switchMode('spelling'));
    restartBtn.addEventListener('click', restartGame);

    // --- Core Functions ---

    function parseWordsFromFile(text) {
        const lines = text.trim().split('\n');
        const regex = /<([^>]+)>\s*<([^>]+)>\s*<([^>]+)>/;
        return lines.map(line => {
            const match = line.match(regex);
            if (match) {
                return {
                    english: match[1].trim(),
                    correct: match[2].trim(),
                    incorrect: match[3].trim()
                };
            }
            return null;
        }).filter(word => word !== null);
    }

    function parseWordsFromTable() {
        const rows = tableBody.querySelectorAll('.table-row');
        const wordsFromTable = [];
        rows.forEach(row => {
            const english = row.querySelector('.english-input').value.trim();
            const correct = row.querySelector('.correct-input').value.trim();
            const incorrect = row.querySelector('.incorrect-input').value.trim();
            if (english && correct && incorrect) {
                wordsFromTable.push({ english, correct, incorrect });
            }
        });
        return wordsFromTable;
    }

    function addTableRow() {
        const newRow = document.createElement('div');
        newRow.className = 'table-row';
        newRow.innerHTML = `
            <input type="text" class="english-input" placeholder="e.g., apple">
            <input type="text" class="correct-input" placeholder="e.g., n.苹果">
            <input type="text" class="incorrect-input" placeholder="e.g., n.香蕉">
        `;
        tableBody.appendChild(newRow);
    }

    function startGame() {
        const file = fileInput.files[0];
        
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                words = parseWordsFromFile(e.target.result);
                if (words.length > 0) {
                    initializeGame();
                } else {
                    alert('文件格式不正确或内容为空！');
                }
            };
            reader.readAsText(file);
        } else {
            words = parseWordsFromTable();
            if (words.length > 0) {
                initializeGame();
            } else {
                alert('请至少输入一个完整的单词行或上传文件！');
            }
        }
    }

    function initializeGame() {
        shuffledWords = [...words].sort(() => Math.random() - 0.5);
        currentWordIndex = 0;
        correctAnswers = 0;
        uploadSection.classList.add('hidden');
        summarySection.classList.add('hidden');
        footer.classList.remove('hidden'); // Show footer navigation
        switchMode(currentMode);
    }

    function switchMode(mode) {
        currentMode = mode;
        flashcardSection.classList.add('hidden');
        spellingSection.classList.add('hidden');
        navFlashcard.classList.remove('active');
        navSpelling.classList.remove('active');

        if (mode === 'flashcard') {
            flashcardSection.classList.remove('hidden');
            navFlashcard.classList.add('active');
            setupFlashcards();
        } else {
            spellingSection.classList.remove('hidden');
            navSpelling.classList.add('active');
            setupSpelling();
        }
    }

    function setupFlashcards() {
        currentWordIndex = 0;
        correctAnswers = 0;
        shuffledWords = [...words].sort(() => Math.random() - 0.5);
        showNextWord();
    }

    function setupSpelling() {
        currentWordIndex = 0;
        correctAnswers = 0;
        // For spelling, we might want a different shuffle logic, but for now, it's the same.
        shuffledWords = [...words].sort(() => Math.random() - 0.5);
        showNextWord();
    }

    function showNextWord() {
        if (currentWordIndex >= shuffledWords.length) {
            showSummary();
            return;
        }

        const word = shuffledWords[currentWordIndex];
        
        if (currentMode === 'flashcard') {
            flashcardResult.classList.add('hidden');
            flashcardWord.textContent = word.english;
            const options = [word.correct, word.incorrect].sort(() => Math.random() - 0.5);
            option1.textContent = options[0];
            option2.textContent = options[1];
            
            option1.onclick = () => checkFlashcardAnswer(options[0]);
            option2.onclick = () => checkFlashcardAnswer(options[1]);

        } else if (currentMode === 'spelling') {
            spellingResult.textContent = '';
            spellingResult.className = '';
            spellingTranslation.textContent = word.correct;
            spellingInput.value = '';
            spellingInput.focus();
            
            checkSpellingBtn.onclick = checkSpellingAnswer;
            spellingInput.onkeyup = (e) => {
                if (e.key === 'Enter') {
                    checkSpellingAnswer();
                }
            };
        }
    }

    function checkFlashcardAnswer(selectedOption) {
        const correct = selectedOption === shuffledWords[currentWordIndex].correct;
        flashcardResult.classList.remove('hidden');

        if (correct) {
            correctAnswers++;
            flashcardResult.textContent = '正确! ✅';
            flashcardResult.className = 'correct';
            setTimeout(() => {
                currentWordIndex++;
                showNextWord();
            }, 1000);
        } else {
            flashcardResult.textContent = `错误! ❌ 正确答案: ${shuffledWords[currentWordIndex].correct}`;
            flashcardResult.className = 'incorrect';
            // Play pronunciation (not implemented, placeholder)
            // const utterance = new SpeechSynthesisUtterance(shuffledWords[currentWordIndex].english);
            // speechSynthesis.speak(utterance);
            setTimeout(() => {
                currentWordIndex++;
                showNextWord();
            }, 2000);
        }
    }

    function checkSpellingAnswer() {
        const userAnswer = spellingInput.value.trim();
        const correctAnswer = shuffledWords[currentWordIndex].english;

        if (userAnswer.toLowerCase() === correctAnswer.toLowerCase()) {
            correctAnswers++;
            spellingResult.textContent = '正确! ✅';
            spellingResult.className = 'correct';
            setTimeout(() => {
                currentWordIndex++;
                showNextWord();
            }, 1000);
        } else {
            spellingResult.textContent = `错误! ❌ 正确拼写: ${correctAnswer}`;
            spellingResult.className = 'incorrect';
            spellingInput.value = ''; // Clear input for re-try
            spellingInput.focus();
        }
    }

    function showSummary() {
        flashcardSection.classList.add('hidden');
        spellingSection.classList.add('hidden');
        summarySection.classList.remove('hidden');
        const accuracy = words.length > 0 ? (correctAnswers / words.length * 100).toFixed(1) : 0;
        accuracyText.textContent = `本次练习共 ${words.length} 个单词，答对 ${correctAnswers} 个，正确率: ${accuracy}%`;
    }

    function restartGame() {
        uploadSection.classList.remove('hidden');
        summarySection.classList.add('hidden');
        footer.classList.add('hidden');
        words = [];
        fileInput.value = '';
        // Clear and reset table
        tableBody.innerHTML = `
            <div class="table-row">
                <input type="text" class="english-input" placeholder="e.g., apple">
                <input type="text" class="correct-input" placeholder="e.g., n.苹果">
                <input type="text" class="incorrect-input" placeholder="e.g., n.香蕉">
            </div>
        `;
    }
});
