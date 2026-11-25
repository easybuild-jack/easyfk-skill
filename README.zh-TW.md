<h1 align="center">easyfk-skill</h1>

<p align="center">
  <b>EasyFK 的 AI Skill 套件：建專案、查框架、寫程式碼、反推系統</b>
</p>

<p align="center">
  <a href="README.zh-CN.md">简体中文</a> · <a href="README.md">English</a> · <b>繁體中文</b> · <a href="README.ja.md">日本語</a>
</p>

<p align="center">
  <a href="#3-四個-skill-的分工"><img alt="skills" src="https://img.shields.io/badge/skills-4-2ea44f?style=flat-square"></a>
  <a href="#4-安裝"><img alt="agents" src="https://img.shields.io/badge/agents-Cursor%20%7C%20Claude%20Code-blue?style=flat-square"></a>
  <a href="https://www.easybuild.pro/easyfk"><img alt="easyfk" src="https://img.shields.io/badge/easyfk-3.2.12%20%7C%203.5.16-orange?style=flat-square"></a>
  <a href="https://github.com/easybuild-jack/easyfk-skill"><img alt="GitHub stars" src="https://img.shields.io/github/stars/easybuild-jack/easyfk-skill?style=flat-square&logo=github"></a>
</p>

<p align="center">
  <a href="https://www.easybuild.pro/easyfk">官網</a> ·
  <a href="https://www.easybuild.pro/docs/reader/dev-env">框架文件</a> ·
  <a href="#4-安裝">安裝</a> ·
  <a href="#5-怎麼用">用法</a>
</p>

---

讓 AI 在 EasyFK 專案裡知道專案怎麼建、框架有什麼、程式碼該怎麼寫、既有系統是怎麼運轉的。沒有 EasyFK 的專案也能用其中與框架無關的通用規範，但能力會明顯打折。

> ## 先了解 EasyFK，再決定怎麼用
>
> 這套 skill 是 [EasyFK 架構](https://www.easybuild.pro/easyfk) 的配套說明書。它講的模組座標、分層寫法、設定前綴、類名註解，全部來自 easyfk 框架本身，不是通用的 Spring 經驗。
>
> - **專案用了 EasyFK**：全部能力可用。上手前請先讀官網，了解這套架構是什麼、有哪些模組：**<https://www.easybuild.pro/easyfk>**
> - **專案沒用 EasyFK**：也能用，但只用與框架無關的那部分——寫能運作的最少實作、阿里開發規範、文件與計畫、自檢與複核。所有 easyfk 相關的內容（模組選型、`easyfk-` 座標與私有儲存庫、框架類名註解和設定前綴、按 BOM 版本路由、反推裡對框架的解讀）一律不參考、不套用。
>
> **先說清楚**：不用 EasyFK 時能力會大打折扣。這套 skill 最值錢的是框架能力地圖和按版本給的確切類名與設定，去掉這塊，剩下的是一套通用開發規範——有用，但換個通用 coding skill 也能給到。

---

## 1. 它和 EasyFK 是什麼關係

[EasyFK（易架構）](https://www.easybuild.pro/easyfk) 是企業級的 Java 技術底座，定位是「一次建設，全域複用」：12 個核心模組、40+ 可插拔元件、統一依賴治理，把所有專案都要重複搭的基礎設施（統一回傳體、例外、日誌、驗證、ORM、快取、MQ、執行緒集區……）做成標準化元件，業務專案按需引入即可開工。

配套的 AI skill 與這套架構綁得很緊，有三個原因：

| 原因 | 說明 |
|---|---|
| **框架閉源，能力只存在於框架裡** | `com.mcst:*` 的 jar 只發佈在私有 Maven 儲存庫。模組有哪些、類叫什麼、註解怎麼寫、設定前綴是什麼，AI 靠通用知識猜不出來，猜錯就是編譯不過 |
| **編碼規範由框架的分層決定** | `Controller → IXxxApi → Service → Repository → Mapper` 這一套（以及 `ApiServerImpl / ApiScImpl / ApiDubboImpl` 的多棧實作）是 EasyFK 的約定，不是普通 Spring 專案的寫法 |
| **框架在演進** | 不同 easyfk 版本的類名、設定項、模組增減都不一樣。skill 按專案實際依賴的 BOM 版本載入對應快照，寫出來的才是這個版本真正能跑的程式碼 |

所以判斷分兩層：

- **有 `easyfk-` 座標或 `com.mcst` 包名** → 按本套件全部規則走。
- **沒有** → 只保留與框架無關的通用規範：最少實作、阿里規範、日誌註解、文件與計畫、自檢與複核、專案說明裡的定位與業務資料依賴。涉及 easyfk 的模組選型、座標與私有儲存庫、類名註解、設定前綴、版本路由一律跳過，也不拿框架寫法往普通 Spring 專案上套。這時它能幫的有限，能力明顯打折——本來就不打算用 EasyFK 的話，通用 coding skill 是更合適的選擇。

## 2. 它解決什麼問題

| 沒有 skill 時 | 有 skill 時 |
|---|---|
| AI 不知道框架已經提供了 `Result`、執行緒集區、快取、鎖、業務編號，於是自己寫一份，或者隨手引入 Guava、commons-lang3 等重複能力 | 先查框架能力地圖，有現成模組就按模組文件的類名和設定寫，缺什麼才補什麼 |
| 分層靠猜：Controller 直接注入 Service、跨服務呼叫不走契約、交易與唯一性校驗漏掉 | 按規範逐層寫：主鍵 `String` + UUID、`@Transactional`、`@SingleUniqueField`、契約四件套一次補齊，寫完自檢 |
| 框架升級後 AI 還在用舊版本的類名和設定前綴 | 從 BOM 讀出專案版本，路由到該版本的文件快照，寫的就是這個版本的 API |
| 接手一個沒人維護的老專案，讀程式碼如讀天書 | 從入口反推出兩份報告：業務分析報告 + 架構分析報告，含流程圖、時序圖、高可用方案 |
| 專案說不清自己是什麼、碰了哪些資料，變更來了只能靠人回憶影響範圍 | 專案說明開頭標明定位（業務專案 / 元件專案，元件專案寫清服務於誰），第 5 節給出業務資料依賴清單：依賴哪些外部資料（如行情、倉位）、自管理哪些、對外提供哪些，各自從哪來、誰在用、變了會波及哪裡 |
| 寫完自己查自己，複雜改動漏了分支、少了契約同步，上線才暴露 | 複雜改動和新需求完成後，另起一個沒參與開發的子 agent，只拿需求和設計逐條審程式碼；阻斷問題改完才收，任務狀態同步落到計畫文件，供上層總管看進展 |

## 3. 四個 skill 的分工

四個 skill 平級安裝、互相按名稱引用，一個需求通常由其中一個主導：

| skill | 回答的問題 | 典型觸發 |
|---|---|---|
| [easyfk-framework-skill](easyfk-framework-skill/SKILL.md) | 框架**有什麼**：工程與模組、每個模組解決什麼問題、這個需求該選哪個模組、有哪些現成工具類、設定前綴是什麼；某個類的**精確簽名**（方法多載、常數值、設定項預設值） | 「要發 MQ 用哪個模組」「有沒有現成的物件轉換工具」「easyfk 支援分庫分表嗎」「`RRBuilder` 有哪些方法」 |
| [easyfk-dev-skill](easyfk-dev-skill/SKILL.md) | 程式碼**怎麼寫**：分層、命名、各層寫法、交易與例外、架構類專案的模組拆分與執行緒模型、文件、自檢 | 「訂單模組加一個取消介面」「按 easyfk 建一個新專案」「寫個 starter」 |
| [easyfk-reverse-skill](easyfk-reverse-skill/SKILL.md) | 系統**是什麼樣**：從現有程式碼還原業務分析報告、架構分析報告，以及業務資料依賴（依賴、自管理、對外提供了哪些業務資料） | 「梳理一下這個老專案的業務流程」「補一張整體架構圖」「這個專案到底依賴了哪些業務資料」 |
| [easyfk-generator-skill](easyfk-generator-skill/SKILL.md) | 專案**怎麼建出來**：檢查 JDK 與 `efg` 安裝狀態、沒裝就下載安裝並驗證、問清要生成的專案類型和參數、寫 `generator.yml`、呼叫 CLI 生成、核對產物 | 「用 easyfk 新建一個訂單微服務」「生成專案骨架」「給既有專案加一張表的 Entity 和業務程式碼」「表改了欄位，刷新一下 DTO」「efg 裝不上 / 報錯」 |

其中 easyfk-dev-skill 有一塊與框架無關（最少實作、阿里規範、文件與計畫、自檢與複核）。專案不用 EasyFK 時只有這部分可用，框架相關的規則全部跳過，能力會明顯打折，判斷方法見 §1。

依賴關係是單向的：建專案先走 generator（生成器 → 框架版本），寫程式碼前先查框架能力（dev → framework），反推框架呼叫時也要查框架（reverse → framework）。生成器只負責把工程和分層程式碼產出來，產出的程式碼怎麼寫、怎麼改，仍然是 dev 說了算。

## 4. 安裝

支援 Cursor、Claude Code 等讀取 `SKILL.md` 的 AI 編碼工具。四個 skill 必須是 skills 目錄**第一層**的平級目錄，嵌套在 `easyfk-skill/` 子目錄下通常不會被識別。

```bash
git clone --depth 1 https://github.com/easybuild-jack/easyfk-skill.git
```

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File easyfk-skill/install.ps1 [-Target <skills 目錄>]
```

```bash
# macOS / Linux
sh easyfk-skill/install.sh [<skills 目錄>]
```

- 目標目錄預設 `~/.cursor/skills`（個人全域）；只給某個專案裝用 `<專案>/.cursor/skills`；Claude Code 用 `~/.claude/skills`。
- 已有的同名目錄會先刪再裝；發現改名前的舊版 `easyfk-skill`（`name: easyfk-skill`）會一併移除。
- 裝完重啟 IDE 或新開工作階段生效。**更新**：重新 clone 再跑一次安裝腳本即可。

## 5. 怎麼用

**不需要手動指定 skill。** 在 EasyFK 專案裡正常提需求，AI 會先從建置檔（`easyfk-` 座標）或原始碼包名（`com.mcst`）認出這是 EasyFK 專案，再按 BOM 版本載入對應文件。

不是 EasyFK 專案時，它不會套用框架那套寫法，只用通用規範（最少實作、文件與計畫、自檢與複核），並主動告訴你能力打了折。普通 Java 專案不會被塞進 `IXxxApi`、`easyfk-` 座標這些框架約定。

幾個實際的說法：

| 你的需求 | 會發生什麼 |
|---|---|
| 「用 easyfk 新建一個訂單微服務，連本機 MySQL 的 order 資料庫」 | 查 JDK 和 `efg`，沒裝就下載安裝並驗證 → 問清專案類型和參數 → 寫 `generator.yml` → 呼叫 `efg` 生成 → 核對模組和分層程式碼是否齊全 |
| 「給既有專案加一張表的 Entity 和業務程式碼」 | 讀現有設定確認座標和包名 → 補 `db-tables` → `efg -m` 再 `efg -s`，不覆蓋已手寫的檔案 |
| 「表改了欄位，幫忙刷新一下 DTO」 | 確認表結構 → `efg -d`，只動 DTO 和 Param |
| 「訂單模組加一個取消介面，要校驗狀態、記日誌」 | 查框架有沒有現成能力 → 按分層生成 Controller / Api / Service / Repository 全套 → 自檢並說明改了什麼 |
| 「這個需求改完了，幫我複核一下」 | 另起一個沒參與開發的子 agent，只拿需求、設計和改動清單逐條審程式碼，輸出阻斷 / 建議清單；阻斷改完複審，結果和任務狀態寫進計畫文件 |
| 「這裡要削峰，用 MQ 還是 Disruptor？」 | 對比 `mq-*` 與 `queue-disruptor` 的持久化、可靠性差異，給出選型和設定前綴，不自己造佇列 |
| 「`RRBuilder` 有哪些方法？」「這個設定項預設值是多少？」 | 查該 easyfk 版本的 API 簽名速查（按模組一份，含方法多載、常數取值、設定項預設值），不憑記憶編 API |
| 「這個專案要同時支援 Dubbo 和 Feign 兩種呼叫」 | 按多棧微服務形態給出契約與實作拆分方案 |
| 「這個老專案沒人維護了，幫我理清業務」 | 找出所有入口（Controller、MQ 消費、XXL-JOB、Aeron、etcd 選主……）→ 輸出業務分析報告 + 架構分析報告 + 業務資料依賴清單 |
| 「上游行情改了合約乘數，我們這邊要動哪些地方？」 | 查業務資料依賴清單裡行情資料的「使用方」和「變更影響」，指出要改的模組、介面和類別#方法，而不是全儲存庫搜一遍 |
| 「升級到新版 easyfk，哪些寫法要改」 | 對比兩版快照，列出改名的設定項、變化的類名，保留舊寫法並註明「從哪個版本起改為」 |

## 6. 框架依賴

easyfk **不開源**，但可免費用。框架的 jar 不發佈在 Maven Central 等公共儲存庫，需要透過官方私有的 Maven 儲存庫取得。

儲存庫位址、存取權杖，以及 Maven / Gradle 的具體設定方法，見官網：<https://www.easybuild.pro/easyfk>

這一步是前提：沒有設好儲存庫，`com.mcst:*` 的依賴會一律解析失敗（找不到構件或 401）。

## 7. 目錄結構

```
easyfk-skill/
├── README.md                 英文（預設，GitHub 顯示這一份）
├── README.zh-CN.md           簡體中文
├── README.zh-TW.md           本檔案（繁體中文）
├── README.ja.md              日文
├── install.ps1 / install.sh  安裝腳本
├── easyfk-framework-skill/   框架能力地圖 + 版本快照
│   ├── SKILL.md              模組全景、需求選型、工具清單、能力邊界、依賴接入
│   ├── maintenance.md        套件自身的維護流程
│   ├── versions/             按 easyfk 版本存放的文件快照
│   │   └── <版本>/           VERSION.md、manuals.txt、modules/、api/、manuals/
│   └── scripts/              快照同步腳本、API 文件生成腳本
├── easyfk-dev-skill/         開發規範
│   ├── SKILL.md              總則、分層、命名、自檢
│   └── rules/                按層與情境拆分的 12 份規則
├── easyfk-reverse-skill/     從程式碼反推業務與架構
│   └── SKILL.md
└── easyfk-generator-skill/   用 efg CLI 建立專案
    ├── SKILL.md              環境與安裝檢查、參數詢問、generator.yml、生成與產物核對
    └── reference/
        └── cli使用手册.md     隨套件發佈的 CLI 原版手冊（完整參數、設定範例、資料庫類型）
```

## 8. 相關連結

- EasyFK 架構介紹：<https://www.easybuild.pro/easyfk>
- EasyFK 文件（開發環境、快速開始）：<https://www.easybuild.pro/docs/reader/dev-env>
- 本儲存庫：<https://github.com/easybuild-jack/easyfk-skill.git>

## 9. 貢獻

Issue 和 PR 都歡迎：回報文件錯漏、補框架新版本的快照、改進規則寫法都可以。

- 動 skill 內容前先讀套件的維護流程 [easyfk-framework-skill/maintenance.md](easyfk-framework-skill/maintenance.md)。新增或更新某個 easyfk 版本的文件快照需要該版本框架原始碼，這部分只有維護者能做。
- 改這份 README 時，四份語言版本（`README.md`、`README.zh-CN.md`、`README.zh-TW.md`、`README.ja.md`）一起改，章節結構和表格行列保持一致。
- 提交前在本機跑一次 `install.sh` / `install.ps1`，確認四個 skill 能正常安裝到 skills 目錄第一層。
- 內容用哪種語言提交都行，中文、英文均可。
