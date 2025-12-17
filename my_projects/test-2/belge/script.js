fetch('belge/isimler.txt')
    .then(response => response.text())
    .then(data => {
        const isimler = data.split('\n').filter(isim => isim.trim() !== '');
        const isimListesiElement = document.getElementById('isimListesi');
        isimler.forEach(isim => {
            const listItem = document.createElement('li');
            listItem.textContent = isim;
            isimListesiElement.appendChild(listItem);
        });
    })
    .catch(error => console.error('Hata oluştu:', error));
