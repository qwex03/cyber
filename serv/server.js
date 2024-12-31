const express = require('express');
const multer = require('multer');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;

app.use(cors());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

const upload = multer({ dest: 'uploads/' });

app.post('/upload', upload.single('file'), (req, res) => {
    const file = req.file;
    const tempPath = file.path;
    const targetPath = path.join(__dirname, './uploads/image.png');
    fs.rename(tempPath, targetPath, (err) => {
        if (err) {
            console.log(err);
            return res.status(500).json({ message: 'File upload failed' });
        }
        return res.status(200).json({ message: 'File uploaded successfully' });
    });
});

app.listen(PORT, () => {    
    console.log(`Server running on port ${PORT}`);
});