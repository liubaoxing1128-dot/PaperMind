# PaperMind Design System

PaperMind 是一款“AI 论文阅读工作台”。设计语言以专业、安静、现代、阅读优先和 AI 辅助为核心，不使用玻璃拟态、霓虹渐变或复杂动画。

## 1. Color System

| Token | 色值 | 用途 |
| --- | --- | --- |
| Primary | `#5657C8` | 主操作、选中状态、链接、重点信息 |
| Primary Hover | `#4546AA` | Primary 的 Hover / Pressed 状态 |
| Primary Soft | `#EEEEFF` | 选中背景、Focus Ring、轻量强调 |
| Secondary | `#667085` | 次级文字、图标、Secondary / Ghost 操作 |
| Background | `#F4F3F0` | 应用工作台背景 |
| Card | `#FFFFFF` | 面板、卡片、输入区背景 |
| Border | `#E2E1DC` | 卡片、输入框、分隔线 |
| Success | `#2F7D5A` | 成功反馈、在线状态 |
| Warning | `#A96C16` | 警告与需要注意的信息 |
| Danger | `#B54752` | 错误、危险操作、失败反馈 |

正文使用 `#202124`；次级信息使用 Secondary；弱提示使用 `#94969C`。页面只使用一个品牌强调色，避免视觉噪音。

## 2. Typography

字体栈：Geist、PingFang SC、Microsoft YaHei、sans-serif。

| Style | Size | Weight | Line Height | 用途 |
| --- | --- | --- | --- | --- |
| H1 | `20px` | `720` | `1.35` | 产品名、页面主标题 |
| H2 | `16px` | `680` | `1.35` | 面板标题、内容标题 |
| Body | `14px` | `400–650` | `1.65` | 正文、文件名、按钮、输入内容 |
| Caption | `12px` | `400–650` | `1.5` | 辅助说明、状态、元数据 |

## 3. Button

所有标准按钮：高度 `40px`、水平 Padding `16px`、圆角 `10px`、字号 `14px`、字重 `650`。

- Primary：Primary 背景、白色文字；用于上传、发送等主操作。
- Secondary：Card 背景、Border 边框、主文字；用于普通次级操作。
- Danger：Danger 背景、白色文字；仅用于不可逆操作。
- Ghost：透明背景、Secondary 文字；用于 Citation 展开等轻量操作。
- Hover：只改变背景或边框，不使用夸张位移。
- Focus：使用 `3px` Primary Soft Focus Ring。
- Disabled：`50%` 透明度并禁用指针交互。

全局可复用类：`.pm-button`、`.pm-button-primary`、`.pm-button-secondary`、`.pm-button-danger`、`.pm-button-ghost`。

## 4. Card

- 圆角：`16px`
- Padding：`16px`
- 边框：`1px solid #E2E1DC`
- 阴影：低对比双层阴影，仅用于区分工作区层级
- 背景：纯白，不使用透明玻璃或渐变

全局可复用类：`.pm-card`。

## 5. Spacing

| Token | Value | 常见用途 |
| --- | --- | --- |
| `--space-1` | `8px` | 图标间距、紧凑控件 |
| `--space-2` | `12px` | 列表间距、组件内部间距 |
| `--space-3` | `16px` | 卡片 Padding、标准区块间距 |
| `--space-4` | `24px` | 内容组之间的分隔 |
| `--space-5` | `32px` | 页面级区块间距 |

避免使用没有语义的随机间距值。

## 6. Icon

统一使用 `lucide-react`：

- 常规图标：`16–18px`
- 强调图标：`20px`
- Stroke Width：`1.75` 左右
- 图标继承文字颜色，不单独增加装饰色
- 不使用 Emoji 作为产品图标，不混用多套图标库

## 7. Animation

- 标准 Transition：`180ms ease`
- Hover：轻微改变颜色、边框或背景
- Pressed：仅主操作允许最多 `1px` 位移反馈
- Loading：只使用简洁旋转或三点状态
- 不使用复杂入场动画、弹跳、霓虹发光或大幅缩放

## 8. Product Principles

- 阅读区始终是视觉中心。
- 左侧用于资料组织，右侧用于 AI 辅助，不与论文正文争夺注意力。
- Citation 必须表现为可追溯证据，而不是营销标签。
- 通过留白、层级和一致性提供专业感，不依赖装饰效果。
- 吸收 NotebookLM 的资料分区、Notion 的排版秩序、Linear 的交互一致性和 ChatGPT 的对话节奏，但保持 PaperMind 自己的论文阅读定位。
