# 浮生渡忧舫

> 一舟横渡烟波外，半卷诗书寄此生

一个**零构建、零依赖**的个人主页 —— 纯静态单文件实现，新中式仙侠风。开场有「御剑飞行」动画，作品区带可翻页的详情浮层。

浏览器直接打开 `index.html` 即可运行，不需要 npm、不需要打包、不需要任何后端。

---

## 目录

- [功能特性](#功能特性)
- [技术要点](#技术要点)
- [目录结构](#目录结构)
- [本地预览](#本地预览)
- [部署到 Vercel](#部署到-vercel)
- [自定义](#自定义)
- [素材说明](#素材说明)
- [浏览器兼容](#浏览器兼容)
- [许可](#许可)

---

## 功能特性

**首屏**

- 加载屏：先天八卦法阵（乾巽坎艮坤震離兌 + 圈层刻度）套太极图，下方进度条上游标是一柄长剑，读数写作「正在开卷」
- **御剑飞行开场**：真人素材（绿幕）在浏览器端实时抠像，沿一条曲线「天路」飞向画面右上角的天边云隙并淡出，身后带多重掠影
- 主标题毛笔字 + 打字机副标题 + 每次刷新随机取一句古诗
- 悬停长剑的法阵光效

**内容区**

- 「关于」：SVG 法阵圆环 + 滚动揭示动画
- 「作品」：三张 3D 翻转卡片，点开是详情浮层 —— 含作品简介、核心能力、参数表、外链按钮与可切换的页面截图画廊
- 「联系」：页脚聚合社交入口与随机金句

**通用**

- 完整响应式（手机 / 平板 / 桌面），移动端有独立导航抽屉
- 深浅内容都以深色底为主，配色为玄黑 + 青蓝 + 暗金

---

## 技术要点

整站是**一个 HTML 文件**，CSS 与 JS 全部内联，无框架、无构建步骤。

几处值得一提的实现：

**1. 浏览器端实时绿幕抠像（WebGL）**

开场飞行的人物素材是一段绿幕视频。GPU 着色器逐像素算「归一化绿度」`gn = (G − max(R,B)) / G` 后取 alpha：

```glsl
float mx = max(c.r, c.b);
float gn = (c.g - mx) / max(c.g, 0.004);
float a  = clamp((0.80 - gn) / 0.58, 0.0, 1.0);
```

选归一化绿度而不是绝对绿度 `G − max(R,B)`，是因为素材绿幕本身有明暗梯度 —— 用绝对绿度会让 57% 以上的画面糊进「半透明模糊带」，整屏泛绿雾。

**2. 素材离线预处理**

网页端只做一次阈值切分，脏活留在离线：探测黑边 → 裁边 → 连通域分离人体与背景雾 → 填洞（救回黑发镂空）→ 把背景**重建为纯绿** → 边缘羽化 → 去绿溢 → 编码。

**3. 飞行动画的朝向控制**

天路用 Catmull-Rom 插值并按弧长参数化。人物**不做任何跟随轨迹的旋转** —— 早期版本把人物朝向绑到轨迹切线上，结果旋转量沿路径从 +36.7° 摆到 −41.8°，看起来像在半空翻滚。

**4. 视频与动画严格同步**

`<video>` 会「提前起跑」：老写法挂 `src` 的同时就 `play()`，视频提前 2.3 秒开始，飞到一半就播完并 loop 回开头，人物姿态当场跳回。正解是两段式挂载（先只挂 `src` 缓冲，起飞前 60ms 才 `currentTime = 0; play()`），并去掉 `loop`。

**5. 入场时序锚在 `window.load`，但带一道 4 秒兜底闸门**

加载屏、御剑飞行、文字浮现共用同一个时间基准 `introT0`，而它的触发点是 `window.load`。问题在于 **`load` 会等页面上所有子资源**，包括一条远程字体表。

实测（用 `rel=preload` 与 `media="print"` 两种写法各跑一次，把字体地址换成一个「连接永远不返回」的地址）：

| 写法 | `window.load` 何时触发 |
|---|---|
| `<link rel="stylesheet" media="print" onload="this.media='all'">` | **21.3 秒后** ❌ |
| `<link rel="preload" as="style" onload="this.rel='stylesheet'">` | 49 毫秒 ✅ |

`media="print"` 那种写法确实不阻塞首帧渲染，但它**参与 `load` 事件的等待计数**。在国内，`fonts.googleapis.com` 经常不是被快速拒绝、而是一路静默丢包 —— 于是 `load` 被拖二十几秒，加载屏就一直停在那儿、御剑飞行永不开始，看起来就像「首屏动画坏了」。所以字体表改用 `preload`，不进入 `load` 关键路径。

同时留了一道 **4 秒硬上限**：任何子资源（首屏那几张大图）把 `load` 拖过 4 秒，就强制触发 `introT0`，动画照旧准点起飞，各元素之间的相对时序完全不变。

---

## 目录结构

```
personal-homepage/
├── index.html                    # 整站（HTML + CSS + JS 全内联，约 3800 行）
├── vercel.json                   # Vercel 部署配置（缓存策略 + 安全响应头）
├── favicon.ico                   # 站点图标（16/32/48/64 多尺寸）
├── LICENSE                       # MIT
├── README.md
├── generate_background.py        # ⚠ 早期背景图试验脚本，产物已不在站内，见下方说明
└── assets/
    ├── hero-bg-new.jpg           # 首屏背景（仙侠山峦）
    ├── about.jpg                 # 「关于」区配图
    ├── footer-bg.jpg             # 页脚背景
    ├── work-qinglian.jpg         # 作品卡片封面 ×3
    ├── work-zblg.jpg
    ├── work-xungu.jpg
    ├── flyer-src.mp4             # 御剑飞行的绿幕源素材
    ├── logo-boat.png             # 站点 logo（烟波画舫）
    ├── taiji.png                 # 太极装饰
    ├── sword-gold.png            # 加载屏长剑
    ├── sword-golden.png          # 首屏长剑
    ├── favicon-32.png
    ├── apple-touch-icon.png      # iOS 添加到主屏
    ├── og-cover.jpg              # 社交分享预览图 1200×630
    └── works/                    # 作品详情里的页面截图
        ├── xg-1.jpg
        ├── xg-2.jpg
        └── xg-code.jpg
```

---

## 本地预览

**方式一：直接打开**

双击 `index.html` 即可。**但开场飞行动画会失效** —— 浏览器把 `file://` 下的视频当跨源资源，无法送进 WebGL 纹理。此时页面会自动降级（跳过飞行直接展示首屏），控制台有一条 `warn`，不是错误。

**方式二：起一个本地服务（推荐）**

```bash
cd personal-homepage

# Python 3
python -m http.server 8000

# 或 Node.js
npx serve .
```

然后访问 <http://localhost:8000>。这样绿幕抠像与飞行动画都能正常跑。

---

## 部署到 Vercel

本仓库是纯静态站，Vercel 可**零配置**识别。推荐流程：

**1. 推到 GitHub**

```bash
git init
git add .
git commit -m "feat: 浮生渡忧舫 · 个人主页"
git branch -M main
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main
```

> ⚠️ 注意：**仓库根目录就应该是 `index.html` 所在层级**。如果你把 `personal-homepage/` 整个目录推进仓库，导入 Vercel 时需要把 Root Directory 设成 `personal-homepage`。

**2. 在 Vercel 导入**

1. 打开 <https://vercel.com>，用 GitHub 账号登录
2. **Add New… → Project**
3. 在列表里找到刚才的仓库，点 **Import**
4. Framework Preset 选 **Other**
5. **Build Command** 留空，**Output Directory** 留空
6. 点 **Deploy**

几十秒后就能拿到一个 `https://<项目名>.vercel.app` 地址。

**3. 关于 `vercel.json`**

已经配好了两件事，不用再手动调：

- **缓存**：`/assets/*` 走 `max-age=604800`（7 天）+ `stale-while-revalidate`（30 天）。回访直接从缓存出，同时留了后台刷新窗口 —— 换素材后最多 7 天自动生效，不必等一年。
- **安全响应头**：`X-Content-Type-Options: nosniff`、`X-Frame-Options: SAMEORIGIN`、`Referrer-Policy`、`Permissions-Policy`。

> 这里刻意**没有**加 `Content-Security-Policy`。站内有大量内联 `<style>` / `<script>` 与 WebGL，CSP 写错会直接白屏，收益不抵风险。

### ⚠️ 中国大陆访问提醒

**`*.vercel.app` 在中国大陆基本无法直接访问**（DNS 被污染）。如果你要给国内的人看，必须绑一个自己的域名：

1. 在 Vercel 项目里 **Settings → Domains** 添加你的域名
2. 到域名服务商处解析，**用 A 记录指向 `76.76.21.21`**

> **不要用 CNAME 指向 `cname.vercel-dns.com`。** Vercel 的托管 DNS 会解析出两条 A 记录，其中 `216.198.79.x` 那一条在国内 TLS 握手会被 RST。浏览器按 happy-eyeballs 有大约一半概率选中那条坏 IP，表现为页面随机打不开、接口偶尔 `Failed to fetch`，而 `curl` 一切正常 —— 极难排查。改用 A 记录指向 `76.76.21.21` 可以根治。

### 部署后自查（3 条，都在浏览器里做）

上线后**不要直接双击本地文件对比**（`file://` 下绿幕抠像本来就会被安全策略拒绝），请在线上页面按 F12：

1. **看视频那一枪**：Network 里过滤 `flyer-src.mp4`，状态应为 **206**、`Content-Type: video/mp4`。若是 404，就是路径大小写问题（见下方「改动后自查」第 1 条）。
2. **看控制台**：不应出现 `heroFlight: video texture blocked`。出现这一条说明纹理上传被安全策略拒了 —— 正式 https 部署不会发生，只会在 `file://` 下出现。
3. **看首屏**：加载屏应该在 2 秒左右淡出，紧接着人物从右下**滑向左上、在右上角天边化掉**。若加载屏一直停着不动，多半是 `load` 事件被某个子资源拖住了（见「技术要点」第 5 条那道兜底闸门）。

---

## 自定义

全站内容都在 `index.html` 里，按下面的锚点找即可。

| 想改什么 | 找什么 |
|---|---|
| 网页标题 / 描述 | `<title>` 与 `<meta name="description">` |
| 首屏主标题 | `class="hero-title"` |
| 打字机文案 | 搜 `typewriterText`（单个字符串常量） |
| 随机诗句池 | 搜 `const poems`（字符串数组） |
| 「关于」正文 | `<section class="section section-narrow" id="about">` |
| 页脚金句池 | 搜 `footer-poem-text` |
| 社交链接 | 页脚 `footer-social` 里的四个 `<a href>` |
| **作品数据** | 搜 `WORK_DETAILS` —— 卡片、详情浮层、截图画廊全部由这一个数组驱动 |
| 配色 | `:root` 里的 CSS 变量（`--bg-deep` `--gold` 等） |
| 主题字体 | `<head>` 里那条 Google Fonts 链接 |

**改作品最省事的做法**：只动 `WORK_DETAILS` 数组。每件作品形如：

```js
{
  tag: '题库 · 刷题',
  name: '轻练助手',
  tagline: '一句话概括',
  intro: ['第一段', '第二段'],
  feats: ['能力一', '能力二'],
  meta: [['形态', '响应式网页版'], ['数据', '云端题库']],
  links: [{ label: '打开网页版', href: 'https://example.com', primary: true }],
  shots: [
    { src: 'assets/works/xx-1.jpg', device: 'phone',   label: '移动端 · 列表' },
    { src: 'assets/works/xx-2.jpg', device: 'desktop', url: 'example.com', label: '桌面端 · 工作台' },
    { src: 'assets/works/xx-code.jpg', device: 'code',  label: '小程序码' }
  ]
}
```

- `device` 取 `phone` / `desktop` / `code`，决定套哪种外框（手机框 / 浏览器框 / 方框）
- `links` 里 `href` 留空字符串时，按钮照常渲染但不跳转 —— 适合还没上线的作品
- `shots` 传 `{ device: 'pending', shape: 'phone', label: '…' }` 会渲染成同比例的占位框，将来换成真图不会跳版

---

## 素材说明

### 图片格式

`assets/` 里的 `.jpg` **确实都是 JPEG**（魔数 `ff d8 ff`）。这批图早期由 Pillow 生成时按 `.jpg` 命名却用了 PNG 编码，导致两个问题：Vercel 按扩展名发 `Content-Type: image/jpeg` 与实际内容不符；1024×1024 的照片级图像用 PNG 存，体积虚高约 6 倍。

已统一转为 **JPEG quality 88 + 4:4:4 无色度抽样**，体积从 7.26MB 降到 1.08MB（省 85%），PSNR 39.5~45.6dB，差异图确认无结构化伪影与色带。

`logo-boat.png`、`sword-gold.png`、`sword-golden.png`、`taiji.png` 保持 PNG —— 它们有真实透明通道，转 JPEG 会丢透明。

### 换素材时的注意

`assets/` 走的是 **7 天浏览器缓存**。替换同名文件后，老访客最多 7 天才会看到新图。要立刻生效，改一下文件名并同步更新 `index.html` 里的引用（或加 `?v=20260927` 这类查询串）。

绿幕素材 `flyer-src.mp4` 有额外要求：必须是一段**背景为纯色绿幕**的视频，且人物在画面中的位置/朝向全程稳定。首帧的「人体质心」归一化坐标要同步写进 `index.html` 的 `ANCHOR_X` / `ANCHOR_Y`。

编码时还要记得 **faststart**（让 `moov` 原子排在 `mdat` 之前，ffmpeg 加 `-movflags +faststart`）。当前素材的 `moov` 在第 32 字节，浏览器拿到第一个分片就能解码，不必等下完整个 1 MB。忘了这一步不会报错，但 `<video>` 会退化成「先下完再播」，起飞那一刻可能还是空帧。

### 改动后自查

换素材或改路径之后，上线前过一遍这四条 —— 它们都属于「本机看着完全正常、一上线才炸」：

1. **路径大小写**：Vercel 跑在 Linux 上，文件系统区分大小写。`assets/Foo.jpg` 和 `assets/foo.jpg` 是两个不同的文件；Windows 开发时拼错大小写不报错，上线直接 404。请逐级精确比对，不要只看「文件存在」。
2. **后缀与真实编码是否一致**：用错编码存图后，本机浏览器能靠内容嗅探正常显示，CDN 却会按后缀发错误的 `Content-Type`。校验方法是看文件头魔数 —— `.jpg` 前三字节必须是 `ff d8 ff`，`.png` 必须是 `89 50 4e 47`。
3. **引用的文件是否都在**：特别注意「写在注释里的还原示例」—— 比如上面 `WORK_DETAILS` 里留的那几行被注释掉的截图路径，对应文件已按设计移到仓库之外，别把它当成真引用去修。
4. **是否还有孤儿文件**：`assets/` 里没被任何地方引用的图会白白进仓库、拖大体积。

### `generate_background.py`

按文件名容易误会 —— 它是**早期**用来试验背景图的脚本，产物是 `assets/hero-bg-v2.jpg`，**这个文件已不在站内**，当前所有背景图都不是它生成的。保留它只是因为它是这个站点的开发痕迹。你要删掉它不影响任何功能。

---

## 浏览器兼容

- Chrome / Edge / Safari / Firefox 现代版本
- 需要 **WebGL**（绿幕抠像）与 **ES6**。不满足时开场动画自动降级，其余内容不受影响
- 使用 `aspect-ratio`、`clamp()`、CSS 自定义属性等现代特性，不支持 IE
- 字体走 Google Fonts CDN，国内加载可能偏慢；如需完全离线，可改为自托管字体文件

---

## 许可

[MIT](LICENSE) © 2026 Billchou

页面内的图片、视频、文案为作者原创素材，采用同一许可。如需商用素材本身，请先联系作者。
