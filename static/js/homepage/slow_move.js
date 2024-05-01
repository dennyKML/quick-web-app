document.addEventListener('DOMContentLoaded', function () {
    const menuLinks = document.querySelectorAll('.menu__item a');

    menuLinks.forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault(); // Забороняємо браузеру перехід за замовчуванням

            const targetId = this.getAttribute('href'); // Отримуємо ідентифікатор цільового елемента
            const targetElement = document.querySelector(targetId); // Знаходимо цільовий елемент за ідентифікатором

            if (targetElement) {
                // Отримуємо вертикальне положення цільового елемента відносно верхнього краю документа
                const targetOffset = targetElement.offsetTop;

                // Плавно прокручуємо сторінку до цільового елемента
                window.scrollTo({
                    top: targetOffset,
                    behavior: 'smooth' // Плавна анімація прокрутки
                });
            }
        });
    });
});