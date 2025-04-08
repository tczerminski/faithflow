(function() {
    const searchInput = document.querySelector('input[name="search"]');
    const songList = document.getElementById('song-list');
    const allItems = Array.from(songList.querySelectorAll('li')).map(li => ({
        element: li,
        title: li.getAttribute('data-title'),
        id: li.id,
    }));

    const fuse = new Fuse(allItems, {
        keys: ['title','id'],
        threshold: 0.2, // tweak this value for more or less fuzziness
    });

    function updateList(query) {
        if (!query) {
            // Show all items
            allItems.forEach(item => item.element.style.display = '');
            return;
        }

        const results = fuse.search(query);
        const resultSet = new Set(results.map(result => result.item.element));

        allItems.forEach(item => {
            item.element.style.display = resultSet.has(item.element) ? '' : 'none';
        });
    }

    searchInput.addEventListener('input', (e) => {
        updateList(e.target.value.trim());
    });
})()
