const deleteButtons = document.querySelectorAll('.job-titles-list__button--delete');

const jobTitleEditable = document.querySelectorAll('.job-titles-list__name');


deleteButtons.forEach(button => {
  button.addEventListener('click', (e) => {

    e.preventDefault()

    const jobTitleId = button.parentNode.id;

    //deleteJobTitle(jobTitleId); //Чтобы вернуть всё, как было, нужно это раскомментить, а условие снизу + текст удалить нахой

    // Проверка наличия элемента с jobTitleId на странице
    const jobTitleEl = document.getElementById(jobTitleId);
    if (!jobTitleEl) {
      console.error(`Элемент по номеру ID ${jobTitleId} на странице не найден`);
      return;
    }

    // Проверка на подлинность отправителя и наличие достаточных прав
    if (isAuthorizedToDelete(jobTitleId, e.origin, e.source)) {
      deleteJobTitle(jobTitleId);
    } else {
      console.error(`Неавторизованная поптыка удалить ID ${jobTitleId}`);
    }

    //Текст уязвимости, сслыку не нашёл: When receiving message with message event, the 
    //sender's identity should be verified using the origin and possibly source properties. 
    //For more information checkout the OWASP A2:2017 
    //(https://owasp.org/www-project-top-ten/2017/A2_2017-Broken_Authentication) and 
    //(https://developer. mozilla.org/en-US/docs/Web/API/Window/postMessage) advisory. 
    //Code: button.addEventListener('click', (e) => {

    // Опять хуйня с адресом страницы.
    // Нужно проверить идентификатор отправителя, который указывается в свойстве origin
    // и в свойстве source объекта event. В условии происходит проверка, что отправитель 
    // сообщения имеет идентификатор 
    //if (e.origin === 'http://127.0.0.1:5000' && e.source === parent) {
    //  deleteJobTitle(jobTitleId);
    //} else {
    //  console.warn('Неавторизованный отправитель');
    //}
  });
});

jobTitleEditable.forEach(field => {

  const oldJobTitle = field.textContent;

  field.addEventListener('keypress', (e) => {

    const jobTitleId = field.parentNode.id;

    if (e.key === 'Enter') {
      e.preventDefault();
      newJobTitle = field.textContent;
      updateJobTitle(jobTitleId, newJobTitle, oldJobTitle);
    }
  })
})


function deleteJobTitle(jobTitleId) {
  fetch(`/admin/dashboard/job-titles/${jobTitleId}/delete`)
    .then((response) => {
      if (response.ok) {
        const el = document.querySelector(`.job-titles-list__item[id="${jobTitleId}"]`);
        el.remove();
      }
    })
}

function updateJobTitle(jobTitleId, newJobTitle) {

  fetch(`/admin/dashboard/job-titles/${jobTitleId}/update`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      id: jobTitleId,
      title: newJobTitle
    })
  })
    .then((response) => {
      if (response.ok) {
        const el = document.querySelector(`.job-titles-list__item[id="${jobTitleId}"] > .job-titles-list__name`);
        el.blur()
      } else {
        response.text().then((error) => {
          showError(error)
        })
      }
    })
}


var timer = null;

function showError(message) {
  if (timer !== null) {
    clearTimeout(timer);
    timer = null;
  }
  var errorElement = document.querySelector(".job-titles-list__temp-message-error");
  errorElement.innerHTML = message;
  errorElement.style.display = 'block';
  timer = setTimeout(function () { errorElement.style.display = 'none'; }, 2000);
}