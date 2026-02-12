const commentForm = document.getElementById('commentForm');
const authorNameInput = document.getElementById('authorName');
const commentTextTextarea = document.getElementById('commentText');
const commentsList = document.getElementById('commentsList');

commentForm.addEventListener('submit', function(event) {
    event.preventDefault(); 
    
    const authorName = authorNameInput.value.trim();
    const commentText = commentTextTextarea.value.trim();
    
    if (!authorName || !commentText) {
        alert('Пожалуйста, заполните все поля');
        return;
    }
    
    const commentElement = createCommentElement(authorName, commentText);
    
    commentsList.prepend(commentElement);
    
    commentForm.reset();
});


function createCommentElement(author, text) {
    const article = document.createElement('article');
    article.className = 'comment';
    
    const authorElement = document.createElement('h3');
    authorElement.className = 'author-name';
    authorElement.textContent = author; 
    
    const timeElement = document.createElement('time');
    timeElement.className = 'comment-time';
    timeElement.textContent = getCurrentDateTime();
    timeElement.setAttribute('datetime', new Date().toISOString());
    
    const textElement = document.createElement('p');
    textElement.className = 'comment-text';
    textElement.textContent = text; 
    
    const deleteButton = document.createElement('button');
    deleteButton.className = 'delete-btn';
    deleteButton.textContent = 'Удалить';
    deleteButton.type = 'button';

    deleteButton.addEventListener('click', function(event) {
        const commentToRemove = event.target.closest('article');
        
        if (commentToRemove) {
            commentToRemove.remove();
        }
    });
    
    article.append(authorElement, timeElement, textElement, deleteButton);
    return article;
}

function getCurrentDateTime() {
    const now = new Date();
    return now.toLocaleString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

