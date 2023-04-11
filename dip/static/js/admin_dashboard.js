const sidebar_menu = document.querySelectorAll('.sidebar__item');

for (const item of sidebar_menu) {
  const menu_item_url = item.children[0].getAttribute('href');

  if (current_url === menu_item_url) {
    item.classList.add('sidebar__item-active');
  }
}
