const current_url = window.location.pathname;

const navbar_menu = document.querySelectorAll('.navbar__menu-item');

for (const item of navbar_menu) {
  const menu_item_url = item.children[0].getAttribute('href');

  if (current_url === menu_item_url) {
    item.classList.add('navbar__menu-item-active');
  }
}
