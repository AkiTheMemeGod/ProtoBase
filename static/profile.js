document.addEventListener('DOMContentLoaded', function () {
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadPopup = document.getElementById('uploadPopup');
    const closeBtn = document.querySelector('.close');
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('pfp');
    const preview = document.getElementById('preview');

    uploadBtn.addEventListener('click', function () {
        uploadPopup.style.display = 'block';
    });

    closeBtn.addEventListener('click', function () {
        uploadPopup.style.display = 'none';
    });

    window.addEventListener('click', function (event) {
        if (event.target == uploadPopup) {
            uploadPopup.style.display = 'none';
        }
    });

    dropArea.addEventListener('click', function () {
        fileInput.click();
    });

    dropArea.addEventListener('dragover', function (event) {
        event.preventDefault();
        dropArea.style.backgroundColor = '#f1f1f1';
    });

    dropArea.addEventListener('dragleave', function () {
        dropArea.style.backgroundColor = '';
    });

    dropArea.addEventListener('drop', function (event) {
        event.preventDefault();
        dropArea.style.backgroundColor = '';
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            previewFile(files[0]);
        }
    });

    fileInput.addEventListener('change', function () {
        if (fileInput.files.length > 0) {
            previewFile(fileInput.files[0]);
        }
    });

    function previewFile(file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
    document.addEventListener('DOMContentLoaded', function() {
        const uploadBtn = document.getElementById('uploadBtn');
        const uploadPopup = document.getElementById('uploadPopup');
        const closeBtn = document.querySelector('.close');

        uploadBtn.addEventListener('click', function() {
            uploadPopup.style.display = 'flex'; // Use flex instead of block
        });

        closeBtn.addEventListener('click', function() {
            uploadPopup.style.display = 'none';
        });

        // Close popup when clicking outside content
        uploadPopup.addEventListener('click', function(e) {
            if (e.target === uploadPopup) {
                uploadPopup.style.display = 'none';
            }
        });
    });
});
