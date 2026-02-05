// require('./utils.js') Это просто пока что мечта


(async function () {
    //  Все, что понадобится из DOM
    const usersList = document.querySelector('#users-list')
    const formTitle = document.querySelector('#form-title')
    const formUserId = document.querySelector('#user-id')
    const formName = document.querySelector('#name')
    const formEmail = document.querySelector('#email')
    const formAge = document.querySelector('#age')
    const formSaveBtn = document.querySelector('#save-btn')
    const formCancelBtn = document.querySelector('#cancel-btn')


    let {users} = await fetchUsers()

    addUsersInList(users)

    usersList.addEventListener('click', handleCardClick)

    formSaveBtn.addEventListener('click', handleSubmitButtonListener)
    formCancelBtn.addEventListener('click', resetUserForm);

    /**
     * Методы слушатели
     */
    async function handleSubmitButtonListener(e) {
        e.preventDefault()
        const isEditMode = !!formUserId.value

        if (isEditMode) {
            const {status, user: updatedUser} = await fetchUserUpdate(formUserId.value, {
                name: formName.value,
                email: formEmail.value,
                age: formAge.value
            })

            if (status === 'success') {
                const userCard = document.querySelector(`[data-id="${formUserId.value}"]`);
                userCard.replaceWith(createCard(updatedUser));
            }

        } else {
            const {status, user} = await fetchUserCreate({
                name: formName.value,
                email: formEmail.value,
                age: formAge.value
            })
            if (status === 'success') {
                addUsersInList([user])
            }
        }
        if (status === 'success') {
            resetUserForm()

        }
    }
    async function handleCardClick(e) {
        const userCard = e.target.closest('.user-card');
        if (!userCard) return;

        const userId = Number(userCard.dataset.id);

        const user = users.filter(user => user.id === userId)[0]

        if (e.target.classList.contains('user-button-delete')) {

            if (confirm(`Вы уверены что хотите удалить пользователя ${user.name}?`)) {
                const {status, message} = await fetchDeleteUser(userId);
                if (status === 'success') {
                    userCard.remove();
                }
            }
        }


        if (e.target.classList.contains('user-button-edit')) {
            formTitle.textContent = "Редактирование пользователя"

            formUserId.value = userId
            formName.value = user.name
            formEmail.value = user.email
            formAge.value = user.age

            formCancelBtn.classList.remove('hidden')

        }
    }


    /**
     * Методы централизованного хранилищи
     *
     */
    function addUsersInList(localUsers) {
        localUsers.forEach(user => {
            const userCard = createCard(user);
            usersList.append(userCard);
        });

        if (users !== localUsers)
            users = users.concat(localUsers)
    }



    /**
     * CRUD методы
     *
     */
    async function fetchUsers() {
        const usersResponse = await fetch('http://localhost:5000/users')
        return await usersResponse.json()
    }

    async function fetchUserCreate(userData) {
        const res = await fetch('http://localhost:5000/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        return {status, user, message} = await res.json()

    }

    async function fetchDeleteUser(id) {
        const res = await fetch(`http://localhost:5000/users/${id}`, {
            method: 'DELETE'
        });

        const {status, message, user: deletedUser} = await res.json()

        return {status, message};
    }

    async function fetchUserUpdate(userId, params) {
        const res = await fetch(`http://localhost:5000/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });


        return {status, user, message} = await res.json()
    }


    /**
     * Util methods
     *
     */
    function createCard(user) {
        const userCard = document.createElement('div');
        const userName = document.createElement('h3');
        const userEmail = document.createElement('span');
        const userAge = document.createElement('span');

        const userButtons = document.createElement('div');
        const userButtonEdit = document.createElement('button');
        const userButtonDelete = document.createElement('button');

        // Выдаем атрибуты
        userCard.dataset.id = user.id;

        // Выдаем классы
        userCard.classList.add('user-card')
        userName.classList.add('user-name');
        userEmail.classList.add('user-email');
        userAge.classList.add('user-age');
        userButtons.classList.add('user-buttons');
        userButtonEdit.classList.add('user-button', 'user-button-edit');
        userButtonDelete.classList.add('user-button', 'user-button-delete');

        // Заполнение данными
        userName.textContent = user.name;
        userEmail.textContent = user.email;
        userAge.textContent = user.age;
        userButtonEdit.textContent = 'Редактировать';
        userButtonDelete.textContent = 'Удалить';

        // Вкладываем
        userButtons.append(userButtonEdit, userButtonDelete);
        userCard.append(userName, userEmail, userAge, userButtons);
        return userCard;
    }
    function resetUserForm() {
        formTitle.textContent = "Добавить нового пользователя"
        formUserId.value = ''
        formName.value = ''
        formEmail.value = ''
        formAge.value = ''
        formCancelBtn.classList.add('hidden')
    }





    /**
     * @Deprecated
     */
    async function fetchEditUser(userId, userCard) {
        const {status, user: updatedUser} = await fetchUserUpdate(userId, {
            name: formName.value,
            email: formEmail.value,
            age: formAge.value
        })

        if (status === 'success') {
            formCancelBtn.classList.add('hidden')
            userCard.replaceWith(createCard(updatedUser));

            /**
             * Этот вариант легко получить в React приложениях с QueryClient,
             * но это не удобно для пользователя и есть overhead
             */
            // const {users: newUsers, usersCount: newCount } =  await fetchUsers()
            // users = newUsers;
            //
            // usersList.innerHTML = '';
            // addUsersInList(users)
        }
        resetUserForm();
    }


    /**
     * @Deprecated
     */
    async function handleSubmitForm(e) {
        e.preventDefault()


        const {status, user: updatedUser} = await fetchUserUpdate(userId, {
            name: formName.value,
            email: formEmail.value,
            age: formAge.value
        })

        if (status === 'success') {
            formCancelBtn.classList.add('hidden')
            userCard.replaceWith(createCard(updatedUser));

            /**
             * Этот вариант легко получить в React приложениях с QueryClient,
             * но это не удобно для пользователя и есть overhead
             */
            // const {users: newUsers, usersCount: newCount } =  await fetchUsers()
            // users = newUsers;
            //
            // usersList.innerHTML = '';
            // addUsersInList(users)
        }
        resetUserForm();
    }


})()
