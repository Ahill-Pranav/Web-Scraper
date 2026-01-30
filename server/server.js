const express = require("express");
const fs = require("fs");
const path = require("path");
const csv = require("csv-parser");

const app = express();
const PORT = 3000;

// folders to read CSV from
const OUTPUT_DIRS = [
  path.join(__dirname, "..", "outputs"),
  path.join(__dirname, "..", "outputs_selenium"),
];

app.use(express.static(path.join(__dirname, "public")));

// utility: read csv into array
function readCSV(filePath) {
  return new Promise((resolve, reject) => {
    const rows = [];
    fs.createReadStream(filePath)
      .pipe(csv())
      .on("data", (data) => rows.push(data))
      .on("end", () => resolve(rows))
      .on("error", reject);
  });
}

// homepage → list csv files
app.get("/", async (req, res) => {
  let files = [];

  OUTPUT_DIRS.forEach((dir) => {
    if (!fs.existsSync(dir)) return;

    fs.readdirSync(dir)
      .filter((f) => f.endsWith(".csv"))
      .forEach((f) => {
        files.push({
          name: f,
          path: path.join(dir, f),
          source: path.basename(dir),
        });
      });
  });

  let html = `
  <html>
  <head>
    <title>Myntra Scraper Dashboard</title>
    <link rel="stylesheet" href="/style.css">
  </head>
  <body>
    <h1>🛍️ Myntra Scraper Dashboard</h1>
    <p>Select a CSV file to preview scraped data.</p>

    <table>
      <tr>
        <th>File</th>
        <th>Folder</th>
      </tr>
  `;

  files.forEach((f) => {
    html += `
      <tr>
        <td>
          <a href="/view?file=${encodeURIComponent(f.path)}">
            ${f.name}
          </a>
        </td>
        <td>${f.source}</td>
      </tr>
    `;
  });

  html += `</table></body></html>`;
  res.send(html);
});

// preview one csv
app.get("/view", async (req, res) => {
  const filePath = req.query.file;

  if (!filePath || !fs.existsSync(filePath)) {
    return res.status(404).send("File not found");
  }

  const rows = await readCSV(filePath);

  let html = `
  <html>
  <head>
    <title>Preview ${path.basename(filePath)}</title>
    <link rel="stylesheet" href="/style.css">
  </head>
  <body>
    <h1>${path.basename(filePath)}</h1>
    <a href="/">⬅ Back</a>

    <p>Total rows: <b>${rows.length}</b></p>

    <table>
      <tr>
  `;

  Object.keys(rows[0] || {}).forEach((key) => {
    html += `<th>${key}</th>`;
  });

  html += "</tr>";

  rows.forEach((row) => {
    html += "<tr>";
    Object.values(row).forEach((val) => {
      html += `<td>${val || ""}</td>`;
    });
    html += "</tr>";
  });

  html += "</table></body></html>";

  res.send(html);
});

app.listen(PORT, () => {
  console.log(`🚀 Dashboard running at http://localhost:${PORT}`);
});
