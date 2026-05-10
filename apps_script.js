// =====================================================
// Google Apps Script - paste into the linked Google Sheet
// =====================================================
//
// Setup:
// 1. Create a new Google Sheet
// 2. In row 1, add these headers (in order):
//    A1: timestamp | B1: evaluator | C1: academic_status | D1: topic |
//    E1: paper | F1: criterion | G1: rank_A | H1: rank_B | I1: rank_C | J1: rank_D
// 3. Extensions > Apps Script
// 4. Replace the default code with this file's contents
// 5. Deploy > New deployment
//    - Type: Web app
//    - Execute as: Me
//    - Who has access: Anyone
// 6. Copy the deployment URL into APPS_SCRIPT_URL in index.html
//
// criterion values: logical_progression | cross_slide_coherence |
//                   global_coherence | technical_depth | visuals
// =====================================================

function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = JSON.parse(e.postData.contents);
  var rows = data.rows;

  rows.forEach(function(row) {
    sheet.appendRow([
      row.timestamp,
      row.evaluator,
      row.academic_status,
      row.topic,
      row.paper,
      row.criterion,
      row.rank_A,
      row.rank_B,
      row.rank_C,
      row.rank_D
    ]);
  });

  return ContentService
    .createTextOutput(JSON.stringify({ status: 'ok' }))
    .setMimeType(ContentService.MimeType.JSON);
}
