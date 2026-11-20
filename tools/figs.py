"""Generate lesson figures (SVG -> PNG). Run: python3 tools/figs.py"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = "font-family='Noto Sans CJK JP, Noto Sans CJK SC, sans-serif'"
INK, SUB = "#2b2b2b", "#666666"
BLUE, RED, GREEN, ORANGE, GRAY = "#eef3fa", "#fbeaea", "#eef7f1", "#fff4e5", "#f6f6f6"
ACC = "#c0392b"
BRAIN, BRAINS, HEMA, DURA, SKULL, SCALP = "#f2d7dc", "#c99aa5", "#7d5a44", "#4a6fa5", "#f1ede2", "#e9c9ae"
CSF, TUBE, VESSEL = "#bfe0f5", "#3d8b6e", "#c0392b"


def save(sub, name, w, h, body, title):
    d = os.path.join(ROOT, "figures", sub)
    os.makedirs(d, exist_ok=True)
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}'>"
           f"<rect width='{w}' height='{h}' fill='white'/>"
           f"<text x='30' y='44' font-size='30' font-weight='bold' fill='{INK}' {F}>{title}</text>{body}</svg>")
    p = os.path.join(d, name)
    open(p + ".svg", "w").write(svg)
    subprocess.run(["rsvg-convert", "-w", "1400", "-b", "white", p + ".svg", "-o", p + ".png"], check=True)


def t(x, y, s, size=22, color=INK, anchor="start", bold=False):
    b = " font-weight='bold'" if bold else ""
    return f"<text x='{x}' y='{y}' font-size='{size}' fill='{color}' text-anchor='{anchor}'{b} {F}>{s}</text>"


def box(x, y, w, h, lines, fill=GRAY, size=21, color=INK, bold_first=False):
    s = f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='12' fill='{fill}' stroke='#cfcfcf'/>"
    n = len(lines)
    for i, ln in enumerate(lines):
        yy = y + h / 2 + (i - (n - 1) / 2) * (size + 9) + size * 0.35
        s += t(x + w / 2, f"{yy:.0f}", ln, size, color, "middle", bold_first and i == 0)
    return s


def arrow(x1, y1, x2, y2, color="#888"):
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    ex, ey = x2 - 12 * math.cos(ang), y2 - 12 * math.sin(ang)
    a1 = (x2 - 16 * math.cos(ang - 0.45), y2 - 16 * math.sin(ang - 0.45))
    a2 = (x2 - 16 * math.cos(ang + 0.45), y2 - 16 * math.sin(ang + 0.45))
    return (f"<line x1='{x1}' y1='{y1}' x2='{ex:.1f}' y2='{ey:.1f}' stroke='{color}' stroke-width='3'/>"
            f"<polygon points='{x2},{y2} {a1[0]:.1f},{a1[1]:.1f} {a2[0]:.1f},{a2[1]:.1f}' fill='{color}'/>")


def note(y, s, w=1000):
    return f"<rect x='30' y='{y}' width='{w-60}' height='40' rx='8' fill='#f5f5f5'/>" + t(46, y + 27, s, 19, SUB)


# ---------------- Lesson 2: ICH ----------------
def l2():
    b = ""
    # brain coronal-ish ellipse with sites
    b += f"<ellipse cx='300' cy='330' rx='240' ry='220' fill='{BRAIN}' stroke='{BRAINS}' stroke-width='3'/>"
    b += f"<line x1='300' y1='115' x2='300' y2='470' stroke='{BRAINS}' stroke-width='2' stroke-dasharray='6 6'/>"
    b += f"<ellipse cx='300' cy='560' rx='110' ry='45' fill='{BRAIN}' stroke='{BRAINS}' stroke-width='3'/>"  # cerebellum
    b += f"<rect x='280' y='470' width='40' height='70' fill='{BRAIN}' stroke='{BRAINS}' stroke-width='3'/>"  # brainstem
    sites = [(215, 320, 34, "被殻"), (330, 340, 26, "視床"), (420, 200, 28, "皮質下"), (300, 505, 14, "橋"), (360, 560, 24, "小脳")]
    for x, y, r, _ in sites:
        b += f"<circle cx='{x}' cy='{y}' r='{r}' fill='{HEMA}' opacity='0.9'/>"
    labels = [("皮質下出血（約2割）", 420, 200, 140), ("被殻出血（約3割・最多）", 215, 320, 210),
              ("視床出血（約3割）", 330, 340, 280), ("橋（脳幹）出血", 300, 505, 350), ("小脳出血（約1割弱）", 360, 560, 420)]
    for s, px, py, ty in labels:
        b += f"<line x1='{px}' y1='{py}' x2='600' y2='{ty-7}' stroke='{INK}' stroke-width='1.5'/><circle cx='{px}' cy='{py}' r='4' fill='{INK}'/>"
        b += t(610, ty, s, 22)
    b += t(610, 490, "手術を考えやすい：被殻・皮質下・小脳", 20, ACC, bold=True)
    b += t(610, 520, "手術が勧められにくい：視床・橋", 20, SUB)
    b += note(620, "部位の割合は報告により幅がある（被殻約3割、視床約3割、皮質下約2割、小脳・脳幹各約1割）。模式図")
    save("02", "fig1_sites", 1000, 680, b, "図1　脳出血の起こる場所と手術の考えやすさ")

    b = ""
    cols = [("開頭血腫除去術", "K164「3」", ["頭蓋骨を数cm〜十数cm外す", "顕微鏡で血腫を吸引", "止血を直接確認できる", "全身麻酔・時間は長め"], RED),
            ("内視鏡下血腫除去術", "K164-5", ["1〜2cmの穴（穿頭）", "透明な筒を血腫まで入れ", "内視鏡で見ながら吸引", "体への負担が少ない"], BLUE),
            ("定位的血腫除去術", "K164-4", ["CTの座標で針を誘導", "血腫を吸引・ドレーン", "止血の確認はできない", "局所麻酔で行うことも"], GREEN)]
    for i, (name, code, pts, fill) in enumerate(cols):
        x = 30 + i * 320
        b += f"<rect x='{x}' y='80' width='300' height='420' rx='14' fill='{fill}' stroke='#cfcfcf'/>"
        b += t(x + 150, 125, name, 24, INK, "middle", True)
        b += t(x + 150, 158, code, 20, SUB, "middle")
        for j, p in enumerate(pts):
            b += t(x + 20, 215 + j * 60, "・" + p, 20)
    b += note(530, "点数（令和8年）：開頭・内視鏡はともに47,020点、定位的は18,220点。方法は施設と血腫の状態で選ぶ")
    save("02", "fig2_methods", 1000, 590, b, "図2　脳内血腫を取り除く3つの方法")


# ---------------- Lesson 3: EVD ----------------
def l3():
    b = ""
    # head side view
    b += f"<ellipse cx='260' cy='330' rx='190' ry='210' fill='{SCALP}'/>"
    b += f"<ellipse cx='260' cy='330' rx='170' ry='190' fill='{BRAIN}' stroke='{BRAINS}' stroke-width='3'/>"
    b += f"<path d='M180,300 q40,-60 120,-20 q30,20 10,60 q-60,10 -130,-40 z' fill='{CSF}' stroke='#7fb6d8' stroke-width='2'/>"
    b += t(215, 312, "側脳室", 18, INK)
    # catheter from top-front (Kocher point)
    b += f"<path d='M220,150 L245,285' stroke='{TUBE}' stroke-width='7' fill='none' stroke-linecap='round'/>"
    b += f"<path d='M220,150 Q260,110 420,110 L560,110 L560,200' stroke='{TUBE}' stroke-width='7' fill='none'/>"
    # ear canal reference
    b += f"<circle cx='395' cy='360' r='9' fill='{INK}'/>" + t(330, 405, "外耳孔＝0点の目安", 18, INK)
    b += f"<line x1='395' y1='360' x2='900' y2='360' stroke='{ACC}' stroke-width='2' stroke-dasharray='8 6'/>"
    # drainage device
    b += f"<rect x='540' y='200' width='40' height='60' rx='6' fill='#ddd' stroke='#888'/>"
    b += t(600, 230, "三方活栓・クランプ", 18, SUB)
    b += f"<line x1='560' y1='260' x2='560' y2='300' stroke='{TUBE}' stroke-width='6'/>"
    b += f"<rect x='520' y='300' width='80' height='26' rx='4' fill='#fff' stroke='#888'/>"
    b += t(615, 300, "チャンバー（滴下点）", 18, SUB)
    b += f"<line x1='560' y1='326' x2='560' y2='450' stroke='{TUBE}' stroke-width='5'/>"
    b += f"<rect x='525' y='450' width='70' height='90' rx='8' fill='#eef7f1' stroke='{TUBE}' stroke-width='2'/>"
    b += t(615, 500, "排液バッグ", 18, SUB)
    # height arrow
    b += f"<line x1='780' y1='313' x2='780' y2='360' stroke='{INK}' stroke-width='2'/>"
    b += arrow(780, 340, 780, 312, INK) + arrow(780, 335, 780, 360, INK)
    b += f"<line x1='600' y1='313' x2='800' y2='313' stroke='{INK}' stroke-width='1.5' stroke-dasharray='4 4'/>"
    b += t(800, 330, "設定圧", 20, ACC, bold=True)
    b += t(800, 356, "（例：10〜15cmH₂O）", 18, SUB)
    b += note(570, "滴下点の高さ＝設定圧。上げるほど出にくく、下げるほど出やすい。体位を変える時は必ずクランプ。模式図")
    save("03", "fig1_system", 1000, 630, b, "図1　脳室ドレナージの仕組み")

    b = ""
    b += box(250, 70, 500, 70, ["髄液の通り道がふさがる・出血で頭の中の圧が上がる"], BLUE)
    b += arrow(500, 140, 500, 180)
    items = [("くも膜下出血", "急性水頭症"), ("脳室内に広がる脳出血", "（視床出血など）"), ("小脳出血・腫瘍", "第4脳室の圧迫"), ("重症頭部外傷", "頭蓋内圧の測定")]
    for i, (a, c) in enumerate(items):
        b += box(30 + i * 240, 180, 220, 90, [a, c], ORANGE, 19)
    b += arrow(500, 270, 500, 310)
    b += box(250, 310, 500, 70, ["意識が悪くなる・CTで脳室が大きい"], GRAY)
    b += arrow(500, 380, 500, 420)
    b += box(200, 420, 600, 80, ["緊急で脳室ドレナージ（K145 穿頭脳室ドレナージ術）", "多くは当日。ベッドサイドや手術室で30分前後"], RED, 20)
    b += arrow(500, 500, 500, 540)
    b += box(150, 540, 700, 70, ["髄液がきれいになり、クランプしても悪化しなければ抜去（多くは1〜2週間以内）"], GREEN, 19)
    b += t(500, 650, "抜けない（水頭症が続く）場合 → VPシャント術などへ（第21回）", 20, SUB, "middle")
    save("03", "fig2_indication", 1000, 680, b, "図2　脳室ドレナージが必要になる流れ")


# ---------------- Lesson 4: clipping ----------------
def l4():
    b = ""
    # parent artery
    b += f"<path d='M60,420 C250,420 350,400 500,330 C650,260 760,260 940,260' stroke='{VESSEL}' stroke-width='46' fill='none' stroke-linecap='round' opacity='0.85'/>"
    # aneurysm
    b += f"<path d='M455,345 C420,250 430,150 520,130 C610,115 640,210 600,290 C580,320 560,320 545,315' fill='{VESSEL}' opacity='0.85'/>"
    b += f"<circle cx='545' cy='150' r='14' fill='#e57b6e'/>"
    # clip
    b += f"<rect x='420' y='255' width='190' height='26' rx='10' fill='#9aa5b1' stroke='#5f6b77' stroke-width='2' transform='rotate(-18 515 268)'/>"
    b += f"<rect x='600' y='180' width='120' height='40' rx='10' fill='#c7ced6' stroke='#5f6b77' stroke-width='2' transform='rotate(-18 660 200)'/>"
    labels = [("ブレブ（小さな出っ張り）", 545, 150, 640, 110), ("動脈瘤（こぶ）", 470, 210, 60, 160),
              ("クリップで「首（ネック）」を挟む", 470, 285, 60, 520), ("親血管（血流は保つ）", 820, 262, 720, 400)]
    for s, px, py, tx, ty in labels:
        ex = tx - 6 if tx > px else tx + len(s) * 21 + 6
        b += f"<line x1='{px}' y1='{py}' x2='{ex}' y2='{ty-7}' stroke='{INK}' stroke-width='1.5'/><circle cx='{px}' cy='{py}' r='4' fill='{INK}'/>"
        b += t(tx, ty, s, 21, INK, "start" if tx>px else "start")
    b += note(580, "チタン合金製のクリップ（長さ数mm〜1cm程度）。こぶに血液が入らなくなれば破裂しない。模式図")
    save("04", "fig1_clip", 1000, 640, b, "図1　クリッピングのしくみ")

    b = ""
    b += box(30, 80, 440, 110, ["破裂（くも膜下出血）", "突然の激しい頭痛 → 救急搬送"], RED, 22, bold_first=True)
    b += box(530, 80, 440, 110, ["未破裂", "脳ドック・別の検査で偶然見つかる"], BLUE, 22, bold_first=True)
    b += arrow(250, 190, 250, 230) + arrow(750, 190, 750, 230)
    b += box(30, 230, 440, 130, ["再破裂は発症早期に多い", "できるだけ早く（目安72時間以内）", "クリップかコイルで処置"], ORANGE, 20)
    b += box(530, 230, 440, 130, ["5〜7mm以上、または", "症状・形（ブレブ）・場所で検討", "年齢・持病・希望と合わせて"], GRAY, 20)
    b += arrow(250, 360, 250, 400) + arrow(750, 360, 750, 400)
    b += box(30, 400, 440, 100, ["入院は数週間〜1か月以上", "スパズム（発症4〜14日）に注意"], ORANGE, 20)
    b += box(530, 400, 440, 100, ["外来で説明・相談 → 予定入院", "入院は約1〜2週間"], GRAY, 20)
    b += note(530, "クリップ（開頭）かコイル（カテーテル）かは、場所・形・全身状態・施設の体制で決まる")
    save("04", "fig2_flow", 1000, 590, b, "図2　破裂と未破裂の2つの入口")


# ---------------- Lesson 5: coiling ----------------
def l5():
    b = ""
    # simple body outline
    b += f"<ellipse cx='250' cy='130' rx='60' ry='70' fill='{SCALP}'/>"
    b += f"<rect x='170' y='200' width='160' height='260' rx='50' fill='{SCALP}'/>"
    b += f"<rect x='185' y='450' width='55' height='200' rx='25' fill='{SCALP}'/><rect x='260' y='450' width='55' height='200' rx='25' fill='{SCALP}'/>"
    # route femoral -> aorta -> carotid -> head
    b += f"<path d='M215,560 L235,470 L250,330 L250,240 L265,200 L270,160 L258,120' stroke='{TUBE}' stroke-width='6' fill='none' stroke-linecap='round'/>"
    b += f"<circle cx='258' cy='115' r='10' fill='{VESSEL}'/>"
    b += f"<circle cx='215' cy='560' r='8' fill='{ACC}'/>"
    pts = [("足の付け根（大腿動脈）から刺す", 215, 560, 560), ("大動脈を上る", 250, 330, 380), ("首の動脈（内頸・椎骨）", 268, 180, 230), ("脳の動脈瘤まで", 258, 115, 110)]
    for s, px, py, ty in pts:
        b += f"<line x1='{px}' y1='{py}' x2='440' y2='{ty-7}' stroke='{INK}' stroke-width='1.5'/>"
        b += t(450, ty, s, 22)
    b += t(450, 470, "管は3重：シース → ガイディングカテーテル", 20, SUB)
    b += t(450, 498, "→ マイクロカテーテル（直径1mm弱）", 20, SUB)
    b += t(450, 526, "手首（橈骨動脈）から入る施設もある", 20, SUB)
    b += note(630, "術者が見ているのはX線の白黒の透視画像。造影剤を流したときだけ血管が見える。模式図")
    save("05", "fig1_route", 1000, 690, b, "図1　カテーテルの通り道")

    b = ""
    def an(cx, fill_level, label, step):
        s = f"<path d='M{cx-90},360 C{cx-40},360 {cx-40},360 {cx},330 C{cx+40},360 {cx+40},360 {cx+90},360' stroke='{VESSEL}' stroke-width='34' fill='none' opacity='0.85'/>"
        s += f"<circle cx='{cx}' cy='250' r='70' fill='{VESSEL}' opacity='0.85'/>"
        if fill_level >= 1:
            s += f"<circle cx='{cx}' cy='250' r='62' fill='none' stroke='#d9d9d9' stroke-width='5'/>"
        if fill_level >= 2:
            for r in (46, 32, 18):
                s += f"<circle cx='{cx}' cy='250' r='{r}' fill='none' stroke='#d9d9d9' stroke-width='5'/>"
        if fill_level >= 3:
            s += f"<circle cx='{cx}' cy='250' r='66' fill='#bfbfbf' opacity='0.8'/>"
        if fill_level < 3:
            s += f"<path d='M{cx-130},400 Q{cx-30},400 {cx},300' stroke='{TUBE}' stroke-width='5' fill='none'/>"
        s += f"<circle cx='{cx}' cy='120' r='20' fill='{DURA}'/>" + t(cx, 128, str(step), 22, "white", "middle", True)
        s += t(cx, 450, label[0], 21, INK, "middle", True) + t(cx, 480, label[1], 18, SUB, "middle")
        return s
    b += an(150, 0, ("マイクロカテを入れる", "先端を蒸気で曲げて形づけ"), 1)
    b += an(390, 1, ("最初のコイルで枠", "フレーミング"), 2)
    b += an(630, 2, ("細いコイルで詰める", "フィリング→仕上げ"), 3)
    b += an(870, 3, ("造影で確認・終了", "こぶに血液が入らない"), 4)
    b += box(30, 520, 940, 90, ["ネック（入口）が広い場合：バルーンで一時的に入口をふさぐ（BAT）", "または網状のステントを置いてコイルのはみ出しを防ぐ（SAC＝K178「3」）"], BLUE, 19)
    save("05", "fig2_steps", 1000, 640, b, "図2　コイル塞栓術のステップ")


# ---------------- Special: sedation ----------------
def sp():
    b = ""
    levels = [("軽い鎮静（抗不安）", "普通に会話できる", "#eef7f1"),
              ("中等度鎮静（意識下鎮静）", "呼びかけ・軽い刺激で目を開け、応答する", "#e3f1e8"),
              ("深鎮静", "強い刺激や痛みでやっと反応。呼吸が弱まりやすい", "#fff4e5"),
              ("全身麻酔", "痛みにも反応しない。気道確保が必要", "#fbeaea")]
    for i, (n, d, f) in enumerate(levels):
        y = 90 + i * 115
        x = 30 + i * 40
        b += f"<rect x='{x}' y='{y}' width='{560-i*40}' height='100' rx='12' fill='{f}' stroke='#cfcfcf'/>"
        b += t(x + 20, y + 42, n, 23, INK, bold=True) + t(x + 20, y + 76, d, 18, SUB)
    b += arrow(15, 90, 15, 545, "#999")
    b += t(640, 100, "医科（令和8年）", 22, INK, bold=True)
    b += t(640, 140, "・中等度まで：麻酔料の区分なし", 19)
    b += t(640, 175, "・意識消失・20分未満：L001", 19)
    b += t(660, 202, "（10分未満120点／20分未満310点）", 17, SUB)
    b += t(640, 240, "・深鎮静・20分以上：L007", 19)
    b += t(660, 267, "（2,600／1,700／900／600点）", 17, SUB)
    b += t(640, 305, "・気道確保あり：L008 全身麻酔", 19)
    b += t(640, 360, "歯科（令和8年）", 22, INK, bold=True)
    b += t(640, 400, "・吸入鎮静法 K002（70点）", 19)
    b += t(640, 435, "・静脈内鎮静法 K003（600点）", 19)
    b += t(640, 470, "・歯科吸入/静脈麻酔（Ⅰ）K005", 19)
    b += t(640, 505, "・同（Ⅱ）深鎮静 K006", 19)
    b += note(570, "深さの段階は米国麻酔科学会（ASA）の分類。1つ深い段階に対応できる準備が必要")
    save("sp1", "fig1_levels", 1000, 630, b, "図1　鎮静の深さと令和8年度の区分")

    b = ""
    b += box(300, 70, 400, 60, ["意識消失を伴う吸入・静脈麻酔か？"], BLUE)
    b += arrow(500, 130, 500, 170)
    b += box(300, 170, 400, 60, ["声門上器具・気管挿管で気道確保？"], BLUE)
    b += arrow(700, 200, 790, 200) + box(790, 170, 180, 60, ["L008 全身麻酔"], RED)
    b += t(735, 190, "はい", 18, SUB, "middle")
    b += arrow(500, 230, 500, 270) + t(520, 258, "いいえ", 18, SUB)
    b += box(300, 270, 400, 60, ["実施時間は20分以上？"], BLUE)
    b += arrow(300, 300, 210, 300) + box(30, 270, 180, 60, ["L001 鎮静"], GREEN)
    b += t(255, 290, "未満", 18, SUB, "middle")
    b += t(110, 360, "10分未満 120点", 18, SUB, "middle") + t(110, 386, "10〜20分 310点", 18, SUB, "middle")
    b += arrow(500, 330, 500, 370) + t(520, 358, "以上", 18, SUB)
    b += box(250, 370, 500, 60, ["L007 深鎮静：誰が・どの体制で行ったか？"], ORANGE)
    rows = [("麻酔科標榜医が専従（届出）", "2,600点"), ("標榜医の指導下で専従（届出）", "1,700点"), ("麻酔を専従で実施", "900点"), ("それ以外", "600点")]
    for i, (a, p) in enumerate(rows):
        y = 450 + i * 52
        b += f"<rect x='250' y='{y}' width='500' height='44' rx='8' fill='#fafafa' stroke='#e2e2e2'/>"
        b += t(270, y + 29, a, 19) + t(730, y + 29, p, 19, ACC, "end", True)
    b += note(670, "記録で確認するもの：開始・終了時刻（静脈麻酔は初回投与〜処置終了）、深さの評価、担当者、届出の有無")
    save("sp1", "fig2_flow", 1000, 730, b, "図2　医事課の区分選択フロー（医科）")


if __name__ == "__main__":
    l2(); l3(); l4(); l5(); sp()
    print("ok")
