const subjectInput = document.getElementById('subject');
const gradeInput = document.getElementById('grade');
const errorMessage = document.getElementById('errorMessage');
const gradesList = document.getElementById('grades');
const averageGradeElement = document.getElementById('average-grade');
const gradeForm = document.getElementById('gradeForm');

gradeForm.addEventListener('submit', function(event) {
    event.preventDefault();

    errorMessage.textContent = '';

    const subject = subjectInput.value.trim();
    const grade = Number(gradeInput.value);

    let isValid = true;

    if (isNaN(grade) || grade < 1 || grade > 5) {
        errorMessage.textContent = 'Оценка должна быть числом от 1 до 5';
        isValid = false;
    }
    
    if (!isValid) {
        return; 
    }

    addGradeToList(subject, grade);

    updateAverageGrade();
    
    gradeForm.reset();
});

function addGradeToList(subject, grade) {
    const emptyMessage = gradesList.querySelector('.empty-list');
    if (emptyMessage) {
        emptyMessage.remove();
    }

    const listItem = document.createElement('li');
    listItem.innerHTML = `
        <span>${subject}</span>
        <span class="grade-value">${grade}</span>
    `;

    if (grade >= 4) {
        listItem.classList.add('good');
    } else {
        listItem.classList.add('bad');
    }

    gradesList.appendChild(listItem);
}

function updateAverageGrade() {
    const gradeItems = gradesList.querySelectorAll('li:not(.empty-list)');
    
    if (gradeItems.length === 0) {
        averageGradeElement.textContent = '0.00';
        return; 
    }
    
    let total = 0;
    gradeItems.forEach(item => {
        const gradeValue = parseInt(item.querySelector('.grade-value').textContent);
        total += gradeValue;
    });
    
    const average = total / gradeItems.length;
    averageGradeElement.textContent = average.toFixed(2);
}