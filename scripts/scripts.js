const dropzone = document.getElementById('dropzone-file');
const image = document.getElementById('image-preview');
const input = document.getElementById('input-container');
const imageContainer = document.getElementById('image');
const closeBtn = document.getElementById('close');

dropzone.addEventListener('change', async (event) => {
    event.preventDefault();
    event.stopPropagation();
    
    const files = event.target.files;
    const file = files[0];
    if (file.type.match('image.*')) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch('http://localhost:5000/upload', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (result.message === 'File uploaded successfully') {
            const imageUrl = URL.createObjectURL(file);
            image.src = imageUrl;
            input.classList.add('hidden');
            imageContainer.classList.remove('hidden');
        } else {
            console.error('Erreur lors du téléchargement du fichier');
        }
    } else {
        alert('Le type de fichier n\'est pas pris en charge');
    }
});

closeBtn.addEventListener('click', () => {
    input.classList.remove('hidden');
    imageContainer.classList.add('hidden');
    image.src = '';
});