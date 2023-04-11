const deleteButtons = document.querySelectorAll('.job-titles-list__button--delete');

const jobTitleEditable = document.querySelectorAll('.job-titles-list__name');


deleteButtons.forEach(button => {
  button.addEventListener('click', (e) => {

    e.preventDefault()

    const jobTitleId = button.parentNode.id;
    //из девелопа:
    //deleteJobTitle(jobTitleId); //Чтобы вернуть всё, как было, нужно это раскомментить, а условие снизу + текст удалить

    // ! Кнопка помойки просто не работает, поэтому исправление не особо нужно
    // Проверка наличия элемента с jobTitleId на странице
    const jobTitleEl = document.getElementById(jobTitleId);
    if (!jobTitleEl) {
      console.error(`Элемент по номеру ID ${jobTitleId} на странице не найден`);
      return;
    }

    //Проверка на подлинность отправителя
    if (e.source == window.opener) {
      deleteJobTitle(jobTitleId);
    } else {
      console.error(`Неавторизованная попытка удалить ID ${jobTitleId}`);
    }
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
      } else {
        response.text().then((error) => {
          showError(error)
        })
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