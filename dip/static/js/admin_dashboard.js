const current_url = window.location.pathname;

const menu_items = document.querySelectorAll('.sidebar__item');

for (const item of menu_items) {
  const menu_item_url = item.children[0].getAttribute('href');

  if (current_url === menu_item_url) {
    item.classList.add('sidebar__item-active');
  }
}