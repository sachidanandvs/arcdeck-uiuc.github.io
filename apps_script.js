// =====================================================
// Google Apps Script - Google Sheets에 붙여넣기
// =====================================================
//
// 셋업 방법:
// 1. Google Sheets 새로 만들기
// 2. 첫 번째 행(헤더)에 다음 입력:
//    A1: timestamp | B1: evaluator | C1: academic_status | D1: topic | E1: paper | F1: rank_A | G1: rank_B | H1: rank_C
// 3. Extensions > Apps Script 클릭
// 4. 기본 코드 지우고 아래 전체 복사 붙여넣기
// 5. Deploy > New deployment
//    - Type: Web app
//    - Execute as: Me
//    - Who has access: Anyone
// 6. Deploy 누르고 URL 복사
// 7. eval.html의 APPS_SCRIPT_URL에 그 URL 붙여넣기
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
      row.rank_A,
      row.rank_B,
      row.rank_C
    ]);
  });

  return ContentService
    .createTextOutput(JSON.stringify({ status: 'ok' }))
    .setMimeType(ContentService.MimeType.JSON);
}
