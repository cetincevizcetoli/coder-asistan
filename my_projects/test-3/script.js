fetch('belge/isimler.txt')
    .then(response => response.text())
    .then(data => {
        const isimler = data.split('\n').filter(isim => isim.trim() !== '');
        const ul = document.getElementById('isimListesi');
        isimler.forEach(isim => {
            const li = document.createElement('li');
            li.textContent = isim;
            ul.appendChild(li);
        });
    })
    .catch(error => {
        console.error('Dosya okunurken bir hata oluştu:', error);
        const ul = document.getElementById('isimListesi');
        const li = document.createElement('li');
        li.textContent = 'İsimler yüklenemedi.';
        ul.appendChild(li);
    });
