const express = require("express");
const multer = require("multer");
const axios = require("axios");
const path = require("path");

const upload = multer();
const app = express();
const API_URL = process.env.API_URL || "http://unstructured:8000";

app.use(express.urlencoded({ extended: true }));

app.get("/", (req, res) => {
  res.send(`<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Document Upload</title>
</head>
<body>
  <h1>Upload Document</h1>
  <form action="/upload" method="post" enctype="multipart/form-data">
    <input type="file" name="file" />
    <button type="submit">Upload</button>
  </form>
</body>
</html>`);
});

app.post("/upload", upload.single("file"), async (req, res) => {
  if (!req.file) {
    return res.status(400).send("No file uploaded");
  }

  try {
    const response = await axios.post(`${API_URL}/upload`, req.file.buffer, {
      headers: {
        "Content-Type": req.file.mimetype,
        "X-Filename": req.file.originalname
      }
    });

    res.send(`<p>Uploaded and processed.</p>
<p>Base key: ${response.data.key}</p>
<p><a href="/">Upload another</a></p>`);
  } catch (err) {
    console.error("Upload error:", err.message);
    res.status(500).send("Error uploading file");
  }
});

const port = 3000;
app.listen(port, () => {
  console.log("Web app listening on port", port);
});
