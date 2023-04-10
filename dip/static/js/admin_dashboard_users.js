let currentUser = null;

const editButtons = document.querySelectorAll('.user-list__button--edit');
const deleteButtons = document.querySelectorAll('.user-list__button--delete');
const addButton = document.querySelector('.user-list__button--add');

editButtons.forEach((button) => {
    const userId = button.parentNode.parentNode.id
    //button.addEventListener('click', (e) => { e.preventDefault(); openEditModal(userId) })

    //!
    //Текст уязвимости: "When receiving message with message event, the sender's identity 
    //should be verified using the origin and possibly source properties. For more
    //information checkout the OWASP A2:2017 
    //(https://owasp.org/www-project-top-ten/2017/A2_2017-Broken_Authentication) and 
    //(https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage) advisory.
    //Code: button.addEventListener('click', (e) => { e.preventDefault(); openEditModal(userId) })"

    //предлжоение исправления №1:
    // Это позволит открыть модальное окно без вызова метода "preventDefault()", который вызывает ошибку.
    button.addEventListener('click', () => { openEditModal(userId) })

    // ! Это дерьмо убивает кнопку карандаша для редактирования юзера в дашборде
    //предложение исправления №2, опять ебаный домен:
    //Уязвимость связана с тем, что при клике на кнопку "редактировать" не проверяется и 
    //не подтверждается идентичность отправителя сообщения. Чтобы исправить эту 
    //уязвимость, следует добавить проверку идентичности отправителя сообщения, используя 
    //свойства origin и source.
    //button.addEventListener('click', (e) => {
    //    //Проверяем идентичность отправителя сообщения
    //    if (e.origin === 'https://127.0.0.1:5000' || e.origin === 'https://eshe-domen:228' && e.source === window.opener) {
    //        e.preventDefault();
    //        openEditModal(userId);
    //    } else {
    //        console.warn('Unauthorized message sender');
    //    }
    //});
});

deleteButtons.forEach(button => {
    button.addEventListener('click', () => {
        const name = button.parentNode.querySelector('.user-list__name').textContent;
        button.parentNode.remove();
    });
});

addButton.addEventListener('click', (e) => {
    e.preventDefault();
    const userId = null
    openEditModal(userId);
})


// Modal


const modal = document.querySelector('.modal');
const overlay = document.querySelector('.modal__overlay');
const editUserForm = document.querySelector('#edit-user-form');
const editUserButton = document.querySelector('.user-list__button--edit');
const cancelButton = document.querySelector('.modal__button--cancel');
const userList = document.querySelector('.user-list__table tbody');


async function getUserData(id) {

    const user = await fetch(`/admin/dashboard/user/${id}`)
        .then((response) => {
            if (response.ok) {
                return response.json();
            }
        })
        .then((data) => {
            return data
        })

    return user
}


async function updateUser(id, data) {
    const response = await fetch(`/users/${id}`, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    });
    const updatedUser = await response.json();
    return updatedUser;
}


async function openEditModal(userId) {

    if (userId) {

        currentUser = await getUserData(userId)

        editUserForm.elements.id.value = currentUser.id;
        editUserForm.elements.username.value = currentUser.username;
        editUserForm.elements.first_name.value = currentUser.first_name;
        editUserForm.elements.second_name.value = currentUser.second_name;
        editUserForm.elements.patronymic.value = currentUser.patronymic;
        editUserForm.elements.job_title.value = currentUser.job_title ? currentUser.job_title.id : '';
        editUserForm.elements.email.value = currentUser.email;
        editUserForm.elements.phone_number.value = currentUser.phone_number;
        editUserForm.elements.role.value = currentUser.role;

        if (currentUser.photo) {
            document.getElementById('photo_preview').src = `/user/${userId}/photo`;
        }


    }
    var errorElement = document.querySelector('.message-error');
    errorElement.style.display = 'none'
    modal.style.display = 'block';
}

const photoInput = document.getElementById("photo");
const photoPreview = document.getElementById("photo_preview");

photoInput.addEventListener("change", function () {
    const file = this.files[0]

    const reader = new FileReader();
    reader.addEventListener("load", function () {
        photoPreview.src = reader.result;
    });
    reader.readAsDataURL(file);
});

photoPreview.addEventListener("click", function () { photoInput.click() })


function closeEditModal() {
    modal.style.display = 'none';
}

async function handleFormSubmit(event) {
    event.preventDefault();
    let formData = new FormData(event.target);
    const id = formData.get('id');

    let userUrl = `/admin/dashboard/user/create`;

    if (id) {
        userUrl = `/admin/dashboard/user/${id}/update`;
    }


    // Чтобы сервер мог отследить, что аватар не менялся
    if (formData.get('photo').name !== '') {
        // Чтобы пользователь не загрузил RCE

        const array = new Uint32Array(1);
        crypto.getRandomValues(array);

        const newFilename = array[0].toString(16).slice(2) + '.' + formData.get('photo').name.split('.').pop()
        formData.set('photo', formData.get('photo'), newFilename);
    }

    fetch(userUrl, {
        method: 'POST',
        body: formData,
        redirect: 'follow'
    })
        .then((response) => {
            if (response.ok) {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            } else {
                response.text().then(error => {
                    var errorElement = document.querySelector('.message-error');
                    errorElement.textContent = error;
                    errorElement.style.display = 'block'
                })
            }
        })

}

cancelButton.addEventListener('click', closeEditModal);
editUserForm.addEventListener('submit', handleFormSubmit);
overlay.addEventListener('click', closeEditModal);