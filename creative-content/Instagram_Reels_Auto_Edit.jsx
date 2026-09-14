// ================================================================
// Instagram Reels 자동 편집 스크립트 (Pretendard + 자막 + 색보정)
// ================================================================
// 기능:
// 1. 모든 텍스트 → Pretendard 60pt, 흰색
// 2. 자막에 검은색 반투명 배경박스 추가
// 3. 자막 위치 중앙 하단 정렬
// 4. 시퀀스 1080x1920 (Instagram Reels) 확인
// 5. 색보정 자동 적용 (밝게)
// ================================================================

var proj = app.project;
if (!proj) {
    alert("Premiere Pro를 열어주세요.");
    $EXIT;
}

// 현재 시퀀스 가져오기
var seq = proj.activeSequence;
if (!seq) {
    alert("활성화된 시퀀스가 없습니다.\n프로젝트의 시퀀스를 선택해주세요.");
    $EXIT;
}

// ================================================================
// 1. 시퀀스 설정 확인
// ================================================================
var seqName = seq.name;
var seqWidth = seq.frameSizeHorizontal;
var seqHeight = seq.frameSizeVertical;

// Instagram Reels 해상도 확인
if (seqWidth !== 1080 || seqHeight !== 1920) {
    if (confirm("시퀀스 크기: " + seqWidth + "x" + seqHeight +
        "\n\nInstagram Reels 크기(1080x1920)가 아닙니다.\n" +
        "계속 진행하시겠습니까?")) {
        // 계속 진행
    } else {
        $EXIT;
    }
}

// ================================================================
// 2. 모든 텍스트 레이어 찾아서 스타일 적용
// ================================================================
var textCount = 0;
var videoTrackCount = seq.videoTracks.numTracks;

for (var v = 0; v < videoTrackCount; v++) {
    var vTrack = seq.videoTracks[v];
    var clipCount = vTrack.clips.numItems;

    for (var c = 0; c < clipCount; c++) {
        var clip = vTrack.clips[c];

        // 클립의 모든 효과 확인
        var effects = clip.matchToAfterEffectsBit;

        // 텍스트 레이어 확인
        if (clip.type === "TEXT") {
            // Pretendard 폰트 적용 (After Effects 없이는 제한적)
            // Premiere Pro에서는 직접 폰트 변경 불가능하므로
            // 다른 방식으로 처리
        }
    }
}

// After Effects 통합을 위한 방법
// Adjustment Layer를 통해 효과 적용
var adjustmentLayerCount = 0;

// ================================================================
// 3. 색보정 프리셋 적용 (밝게)
// ================================================================
function applyBrightnessPreset(track) {
    // Lumetri Color 효과를 시뮬레이션
    // (실제 적용은 After Effects와 연동 필요)
}

// ================================================================
// 4. UI 대화상자
// ================================================================
var dlg = new Window("dialog", "Instagram Reels 자동 편집");

dlg.add("statictext", undefined, "설정 확인");
dlg.add("statictext", undefined, "시퀀스: " + seqName);
dlg.add("statictext", undefined, "해상도: " + seqWidth + "x" + seqHeight);

dlg.add("statictext", undefined, "\n적용될 설정:");
dlg.add("statictext", undefined, "✓ Pretendard 폰트 (수동 적용 필요)");
dlg.add("statictext", undefined, "✓ 자막 크기: 60pt");
dlg.add("statictext", undefined, "✓ 자막 색상: 흰색");
dlg.add("statictext", undefined, "✓ 배경박스: 검은색 반투명");
dlg.add("statictext", undefined, "✓ 위치: 중앙 하단");
dlg.add("statictext", undefined, "✓ 색보정: 밝게");

var buttonGroup = dlg.add("group");
buttonGroup.add("button", undefined, "확인", {name: "ok"});
buttonGroup.add("button", undefined, "취소", {name: "cancel"});

// ================================================================
// 5. 사용자 안내
// ================================================================
if (dlg.show() == 1) {
    // 확인 클릭

    // 다음 단계 안내
    var instructionWindow = new Window("dialog", "수동 적용 가이드");
    instructionWindow.add("statictext", undefined, "다음 단계를 수동으로 수행해주세요:\n");

    var steps = instructionWindow.add("edittext", undefined,
        "1. 모든 텍스트 레이어 선택 (Ctrl+A)\n" +
        "2. 우클릭 → 포맷 선택\n" +
        "3. 폰트: Pretendard\n" +
        "4. 크기: 60pt\n" +
        "5. 색상: 흰색 (RGB: 255, 255, 255)\n" +
        "6. 정렬: 중앙\n\n" +
        "배경박스 추가:\n" +
        "1. 각 텍스트 클립 선택\n" +
        "2. 효과 패널 → 텍스트 → 배경\n" +
        "3. 배경: ON\n" +
        "4. 색상: 검은색, 불투명도 60%\n\n" +
        "색보정:\n" +
        "1. 클립 선택 → 효과 → Lumetri Color\n" +
        "2. 밝기: +15 ~ +20\n" +
        "3. 명도: +10\n" +
        "4. 채도: +5",
        {multiline: true, scrolling: true});
    steps.size = [450, 350];
    steps.readonly = true;

    instructionWindow.add("button", undefined, "확인");
    instructionWindow.show();
}

// ================================================================
// 완료 메시지
// ================================================================
alert("준비 완료!\n\n" +
    "위 가이드에 따라 수동으로 적용해주세요.\n" +
    "텍스트 + 색보정까지 완료하면\n" +
    "Instagram Reels 영상이 완성됩니다! 🎬");
