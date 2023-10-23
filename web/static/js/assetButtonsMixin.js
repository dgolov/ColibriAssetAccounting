const showButtons = document.querySelectorAll('.show-btn');

showButtons.forEach(showButton => {
    showButton.addEventListener('click', () => {
        const parentRow = showButton.parentNode.parentNode;
        const childRow = parentRow.nextElementSibling;

        if (childRow && childRow.classList.contains('child-row')) {
            childRow.style.display = 'table-row';

            showButton.style.display = 'none';

            const hideButton = document.createElement('button');
            hideButton.classList.add('hide-btn');
            hideButton.textContent = 'Скрыть';

            hideButton.addEventListener('click', () => {
                childRow.style.display = 'none';
                hideButton.style.display = 'none';
                showButton.style.display = 'inline-block';
            });

            parentRow.querySelector('td').appendChild(hideButton);
        }
    });
});