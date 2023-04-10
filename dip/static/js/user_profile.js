const editButton = document.querySelector(".user-card__button");
//Оригинальная строчка:
//editButton.addEventListener('click', (e) => { e.preventDefault(); openEditModal() })

//!
//Текст уязвимости: When receiving message with message event, the sender's identity should 
//be verified using the origin and possibly source properties. For more information checkout the OWASP A2:2017 
//(https://owasp.org/www-project-top-ten/2017/A2_2017-Broken_Authentication) and 
//(https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage) advisory. Code: 
//editButton.addEventListener('click', (e) => { e.preventDefault(); openEditModal() })

// Исправление. Опять хуйня с адресом страницы
editButton.addEventListener('click', (e) => {
    e.preventDefault();
    //несколько адресов
    if (e.origin !== "http://127.0.0.1:5000" || e.origin !== "http://example.ru") {
        return;
    }
    openEditModal()

    //Previous shit:
    //if (window.parent === e.source && "https://127.0.0.1:5000" === e.origin) {openEditModal()}
})

//оригинал из девелопа: //Вернуть и удалить гойскую функцию
//editButton.addEventListener('click', (e) => { e.preventDefault(); openEditModal() })

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

const modal = document.querySelector('.modal');
const overlay = document.querySelector('.modal__overlay');
const editUserForm = document.querySelector('#edit-user-form');
const editUserButton = document.querySelector('.user-list__button--edit');
const cancelButton = document.querySelector('.modal__button--cancel');
const userList = document.querySelector('.user-list__table tbody');


async function openEditModal() {

    document.getElementById('photo_preview').src = document.querySelector('.user-card__img').src;

    modal.style.display = 'block';
}

function closeEditModal() {
    modal.style.display = 'none';
}


async function handleFormSubmit(event) {
    event.preventDefault();
    let formData = new FormData(event.target);

    let userUrl = `/profile`;

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