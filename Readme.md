# EasyTools 工具箱项目说明

## 项目简介

EasyTools 是一个通过ai生成的轻量级的在线工具集合平台，旨在提供便捷、实用的常用开发及日常工具。平台通过 `index.html` 作为主入口，利用 `tools.json` 配置文件动态加载各类工具页面，支持快速扩展工具类型，无需修改主页面代码即可新增功能模块。

## 项目结构

plaintext

```plaintext
D:.
│  index.html          # 项目主页面（工具入口）
│  Readme.md           # 项目说明文档
│  tools.json          # 工具配置文件（控制工具加载）
│
├─.github/workflows
│          deplay.yaml # GitHub Actions 自动化部署配置文件
│
├─icon
│      easytools.ico   # 项目图标文件
│
├─import
│      CNAME           # 自定义域名配置文件（用于 GitHub Pages 等部署）
│
├─json格式化工具
│      json-formatter.html # JSON 格式化工具页面
│
├─XML格式化工具
│      xml-formatter.html  # XML 格式化工具页面
│
├─图片工具
│      base64toimg.html    # Base64 转图片工具页面
│
└─网络工具
        webservice-tester.html # WebService 接口测试工具页面
```

## 核心文件说明

### 1. index.html（主页面）

- **功能定位**：平台入口，负责展示所有工具列表并提供工具访问入口。
- **核心逻辑**：页面加载时读取 `tools.json` 配置，动态生成工具导航菜单，点击工具后跳转至对应工具页面。
- **使用方式**：直接在浏览器中打开 `index.html` 即可进入工具箱主界面，无需额外依赖。

### 2. tools.json（工具配置文件）

- **功能定位**：管理所有工具的配置信息，是实现 “动态加载工具” 的核心文件。

- **配置格式**：采用 JSON 格式，每个工具对应一个配置项，包含工具名称、工具路径、工具描述等关键信息。

- 示例配置：json

  ```json
  [
      {
          "title": "base64转图片",
          "description": "base64转图片，支持多种格式",
          "icon": "fa-image",
          "link": "图片工具/base64toimg.html",
          "tags": ["图片", "转换", "base64"]
      },
      {
          "title": "json格式化",
          "description": "json格式化工具，支持格式化、压缩、美化等操作",
          "icon": "fa-exchange",
          "link": "json格式化工具/json-formatter.html",
          "tags": ["json", "格式化", "转换"]
      },
      {
          "title": "XML格式化工具",
          "description": "XML格式化工具，支持格式化、压缩、美化等操作",
          "icon": "fa-crop",
          "link": "XML格式化工具/xml-formatter.html",
          "tags": ["xml", "格式化", "转换"]
      },
      {
          "title": "webservice调试",
          "description": "webservice调试工具，支持多种协议和格式",
          "icon": "fa-crop",
          "link": "网络工具/webservice-tester.html",
          "tags": ["webservice", "调试", "测试"]
      }
  ]
  ```

## 快速新增工具

无需修改主页面代码，仅需两步即可新增工具：

1. **创建工具页面**：

   - 在项目根目录下新建工具文件夹（如 “时间戳工具”），并在文件夹内创建工具 HTML 文件（如 “timestamp-converter.html”）。
   - 开发工具功能（需确保工具页面独立可运行，无需依赖主页面额外逻辑）。

2. **更新 tools.json 配置**：

   - 打开

     ```
     tools.json
     ```

     文件，在数组中新增一个工具配置对象，包含以下必填字段：

     - `title`：工具名称（将显示在主页面导航中）。
     - `link`：工具页面的相对路径（如 “时间戳工具 /timestamp-converter.html”）。
     - `description`：工具功能描述（可选，用于主页面工具说明）。
     - `icon`：图标，使用**Font Awesome 4.7.0 版本**开源组件库
     - `tags`：标签

   - 保存 `tools.json` 后，刷新 `index.html` 即可在主页面看到新增的工具。

## 部署说明

项目支持通过 GitHub Pages 快速部署，核心依赖 `.github/workflows/deplay.yaml` 自动化部署配置：

1. 配置自定义域名（可选）

   ：

   - 在 `import/CNAME` 文件中填写自定义域名（如 “[tools.example.com](https://tools.example.com/)”），确保域名已解析至 GitHub Pages 服务器。

2. 触发部署

   ：

   - 将项目代码推送到 GitHub 仓库后，GitHub Actions 会自动执行 `deplay.yaml` 中的部署流程，将项目部署到 GitHub Pages。

3. 访问方式

   ：

   - 部署完成后，通过 GitHub Pages 默认域名（如 “用户名.github.io/ 仓库名”）或自定义域名访问工具箱。

## 工具功能清单

| 工具名称            | 功能描述                                                     | 访问路径                             |
| ------------------- | ------------------------------------------------------------ | ------------------------------------ |
| JSON 格式化工具     | 格式化、压缩 JSON 字符串，校验 JSON 语法，支持一键复制结果   | json 格式化工具 /json-formatter.html |
| XML 格式化工具      | 美化、压缩 XML 代码，自定义缩进格式，支持 XML 语法检查       | XML 格式化工具 /xml-formatter.html   |
| Base64 转图片       | 输入 Base64 编码生成预览图片，支持 JPG/PNG 格式转换，提供图片下载功能 | 图片工具 /base64toimg.html           |
| WebService 接口测试 | 输入 WebService 接口地址与参数，发送请求并展示响应结果，支持参数格式校验 | 网络工具 /webservice-tester.html     |

## 技术栈说明

- **前端框架**：原生 HTML/CSS/JavaScript（无第三方框架依赖，轻量易扩展）。
- **配置文件**：JSON（简洁易维护，便于动态加载）。
- **部署工具**：GitHub Actions（自动化部署，无需手动操作）。

## 注意事项

1. 新增工具页面时，建议保持与现有工具页面一致的设计风格，提升用户体验。
2. 工具页面路径需填写正确的相对路径，避免因路径错误导致工具无法访问。
3. 部署前需确保 `deplay.yaml` 中的配置与 GitHub 仓库信息匹配，避免部署失败。
4. 若需添加工具图标，可将图标文件放入 `icon` 文件夹，并在 `tools.json` 中扩展 `icon` 字段（需同步修改 `index.html` 图标渲染逻辑）。

## 更新内容

> 20250903

通过classify.json增加分类，tools.json标签增加字段category选择分类，可以进行快速的筛选分类