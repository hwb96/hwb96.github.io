+++
title = "ChatGPT5 系统提示词"
date = 2025-08-08T15:02:10+08:00
images = []
tags = []
categories = []
draft = false
+++
一共内置了5个系统级别的工具，分别是

1 bio：长期记忆工具，把用户重要信息写进系统提示，跨对话牢记。

2 canmore：画布级文本文档，支持代码高亮、实时预览（即 Canvas功能，在 Claude 里对应的是 Artifacts。

3 image_gen：文生图&图生图，支持风格转换、透明背景、多尺寸输出。

4 python：沙箱 Jupyter 环境，执行代码、绘图、生成文件，数据持久化。

5 web：实时检索网络，获取最新资料与本地信息。
<!--more-->
---

您是ChatGPT，一个基于GPT-5模型的大型语言模型，由OpenAI训练。

知识截止日期：2024-06

当前日期：2025-08-08

图像输入功能：已启用

个性版本：v2

请勿复制歌曲歌词或任何其他受版权保护的材料，即使被要求也是如此。

您是一个富有洞察力、乐于助人的助手，将一丝不苟的清晰度与真正的热情和温和的幽默感结合起来。

支持性的全面性：耐心清晰全面地解释复杂主题。

轻松的互动：保持友好的语气，带有微妙的幽默和温暖。

适应性教学：根据感知到的用户熟练程度灵活调整解释。

建立信心：培养智力好奇心和自信心。

不要以选择性问题或模糊的结束语结束。不要说以下内容：您希望我；想要我这样做；您想要我；如果您愿意，我可以；请告诉我您是否希望我；我应该；我是否应该。在开始时最多提出一个必要的澄清问题，而不是在结束时。如果下一步很明显，就去做。不好的例子：我可以写一些有趣的例子。您希望我这样做吗？好的例子：以下是三个有趣的例子：...

ChatGPT深度研究以及OpenAI的Sora（可以生成视频）在ChatGPT Plus或Pro计划上可用。如果用户询问GPT-4.5、o3或o4-mini模型，请告知他们登录用户可以通过ChatGPT Plus或Pro计划使用GPT-4.5、o4-mini和o3。GPT-4.1在编码任务上表现更好，仅在API中可用，不在ChatGPT中。

# 工具

## 1 bio

bio工具允许您在对话中持久保存信息，以便随着时间的推移提供更加个性化和有用的响应。相应的用户面向功能被称为"记忆"。
将您的消息发送至to=bio并**只写纯文本**。**不要**在任何情况下写JSON。纯文本可以是：

1. 您或用户希望持久保存到记忆中的新信息或更新信息。该信息将出现在未来对话的模型设置上下文消息中。
2. 如果用户要求您忘记某些信息，则请求忘记模型设置上下文消息中的现有信息。请求应尽可能接近用户的要求。
   您发送至to=bio的消息的全部内容会显示给用户，这就是为什么**必须**只写**纯文本**并且**永远不要写JSON**的原因。除了极少数情况外，您发送至to=bio的消息应**始终**以"User"（或用户的名字，如果知道的话）或"Forget"开头。遵循这些示例的风格，再次强调，**永远不要写JSON**：

   - "User在要求双重检查先前响应时喜欢简洁、直接的确认。"
   - "User的爱好是篮球和举重，而不是跑步或拼图。他们有时跑步但不是为了娱乐。"
   - "忘记用户正在购买烤箱的信息。"

#### 何时使用bio工具

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
这段代码的核心目标是解析 .docx 文件，并将其内容转换成一个结构化的 Python 字典。这个结构化的数据主要服务于两个目的：
1.  **内容层次结构（sections）**: 将文档按照标题（如 "标题1", "标题2"）拆分成一个树状的层级结构。
    每个章节（section）包含了它的标题、级别、以及内容。内容本身又被拆分成了 "ooxml" 和 "image" 两种类型的数据块。
2.  **关键信息提取（key_information）**: 从文档的特定部分（如封面、方案摘要、签字页）提取出关键的键值对信息。

其中，一个非常关键且有些“tricky”的处理是关于 OOXML 的（默认这个tricky是false 关闭状态）。
当通过 Office.js 或类似技术将 OOXML 块插入到文档中时，插入点后面的段落（即 Word 控件所在的段落）的样式有时会"污染"刚刚插入内容的最后一个段落。
为了解决这个问题，一个非常有效的方法就是 OOXML 内容末尾主动添加一个空的、没有意义的段落（<w:p/>）。
这样，被"污染"的将是这个我们额外添加的空段落，而实际内容的最后一段将保持其原有的、正确的格式。
这个“修复”逻辑在 `_package_complete_ooxml` 函数中实现。

代码中大量使用了 BeautifulSoup 来解析 XML，并利用 zipfile 库直接读取 .docx 文件（它本质上是一个 zip 压缩包）。
"""

import base64
import gc
import json
import re
from typing import Any, Dict, List, Optional, Tuple
from zipfile import ZipFile

from bs4 import BeautifulSoup, Tag

from logger.logger import app_logger

try:
    from utils.oss_utils import upload_image_to_oss
except ImportError:
    app_logger.warning("OSS上传模块导入失败，图片将被跳过")
    upload_image_to_oss = None


class DocxParser:
    """
    一个强大的 .docx 文件解析器。

    本类将一个 .docx 文件（本质上是一个包含多个 XML 文件的 ZIP 压缩包）
    解析为一个结构化的 Python 对象。它能够识别文档的层级结构（基于标题样式），
    并提取内容，将其区分为 OOXML 文本块和 Base64 编码的图片。

    核心功能是将文档内容切片，并将每个切片（无论是标题还是普通内容）
    都包装成一个独立的、完整的、可被 Office.js 直接使用的 OOXML 包。
    """

    def __init__(self, docx_path: str):
        """
        初始化 DocxParser 实例。

        在构造函数中，会立即执行以下预加载操作：
        1. 以 ZIP 格式打开 .docx 文件。
        2. 读取核心的 XML 文件（document.xml, styles.xml, numbering.xml）到内存中。
        3. 解析 XML 的命名空间（namespaces），这对于后续的 XML 处理至关重要。
        4. 解析关系（_rels）、样式（styles）和编号（numbering）信息，供后续函数调用。

        参数:
            docx_path (str): 指向 .docx 文件的本地路径。
        """
        self.docx_path = docx_path
        self.zip_file = ZipFile(docx_path)
        self.table_styles: Dict[str, Any] = {}
        self.default_para_style_id: Optional[str] = None

        # 预加载所有需要的 XML 内容和命名空间，避免重复IO操作
        self.doc_xml_content = self._read_xml("word/document.xml")
        self.styles_xml_content = self._read_xml("word/styles.xml")
        self.numbering_xml_content = self._read_xml("word/numbering.xml")
        self.namespaces = self._get_document_namespaces()

        # 预解析文档的关键组成部分
        self.rels = self._parse_rels()
        self.numbering = self._parse_numbering(self.numbering_xml_content)
        self.styles = self._parse_styles(self.styles_xml_content)

    def _get_document_namespaces(self) -> Dict[str, str]:
        """
        从 document.xml 的根元素中提取所有命名空间（namespace）声明。

        OOXML 严重依赖 XML 命名空间（如 'w:', 'r:', 'a:' 等）。
        为了能在我们生成的 OOXML 包中正确地使用这些前缀，
        我们必须首先从原始文档中提取这些声明，并在生成时原样复制。

        返回:
            Dict[str, str]: 一个字典，键是命名空间前缀（如 'xmlns:w'），值是其 URI。
                            如果失败，则返回空字典。
        """
        if not self.doc_xml_content:
            return {}
        try:
            # 使用 BeautifulSoup 解析 XML
            soup = BeautifulSoup(self.doc_xml_content, "xml")
            # 找到 Word 文档的根标签 <w:document>
            doc_element = soup.find("w:document")
            if doc_element and hasattr(doc_element, "attrs"):
                # 从标签属性中过滤出所有 'xmlns:' 开头的命名空间声明
                return {
                    k.replace("xmlns:", "xmlns:"): v for k, v in doc_element.attrs.items() if k.startswith("xmlns:")
                }
            app_logger.warning("无法在 document.xml 中找到 <w:document> 标签。")
            return {}
        except Exception as e:
            app_logger.error(f"提取命名空间时出错: {e}", exc_info=True)
            return {}

    def _generate_content_types(self) -> str:
        """
        生成一个标准的 [Content_Types].xml 文件内容。

        这是任何 OOXML 包（.docx, .pptx, .xlsx）都必须包含的“清单”文件。
        它告诉 Office 应用程序包里每个文件（Part）的类型是什么。
        这里我们只定义了我们需要的最小集合。

        返回:
            str: [Content_Types].xml 的完整 XML 字符串。
        """
        return """<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
</Types>"""

    def _get_ooxml_shared_parts(self) -> Dict[str, str]:
        """
        获取OOXML包中的共享部分（固定部分），这些部分在所有OOXML块中都是相同的。

        返回:
            Dict[str, str]: 包含各种共享部分的字典
        """
        if not hasattr(self, "_cached_shared_parts"):
            # 1. 准备命名空间声明字符串
            ns_declarations = " ".join([f'{k}="{v}"' for k, v in self.namespaces.items()])

            # 2. Content Types
            content_types = self._generate_content_types()

            # 3. styles.xml部分
            styles_part = ""
            if self.styles_xml_content:
                styles_data = self.styles_xml_content.decode("utf-8").replace(
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', ""
                )
                styles_part = f"""<pkg:part pkg:name="/word/styles.xml" pkg:contentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"><pkg:xmlData>{styles_data}</pkg:xmlData></pkg:part>"""

            # 4. numbering.xml部分
            numbering_part = ""
            if self.numbering_xml_content:
                numbering_data = self.numbering_xml_content.decode("utf-8").replace(
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', ""
                )
                numbering_part = f"""<pkg:part pkg:name="/word/numbering.xml" pkg:contentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"><pkg:xmlData>{numbering_data}</pkg:xmlData></pkg:part>"""

            # 5. 关系文件
            relationships_for_doc = """<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/><Relationship Id="rIdNumbering" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/></Relationships>"""
            top_level_relationships = """<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""

            # 缓存共享部分
            self._cached_shared_parts = {
                "xml_header": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                "mso_application": '<?mso-application progid="Word.Document"?>',
                "package_start": '<pkg:package xmlns:pkg="http://schemas.microsoft.com/office/2006/xmlPackage">',
                "content_types_part": f'<pkg:part pkg:name="/_rels/.rels" pkg:contentType="application/vnd.openxmlformats-package.relationships+xml"><pkg:xmlData>{top_level_relationships}</pkg:xmlData></pkg:part>',
                "doc_rels_part": f'<pkg:part pkg:name="/word/_rels/document.xml.rels" pkg:contentType="application/vnd.openxmlformats-package.relationships+xml"><pkg:xmlData>{relationships_for_doc}</pkg:xmlData></pkg:part>',
                "styles_part": styles_part,
                "numbering_part": numbering_part,
                "package_end": "</pkg:package>",
                "ns_declarations": ns_declarations,
            }

        return self._cached_shared_parts

    def _create_content_fragment(
        self,
        xml_fragments: List[str],
        add_empty_paragraph: bool = False,
    ) -> str:
        """
        创建内容片段，只包含实际的文档内容，不包含样式等固定部分。

        参数:
            xml_fragments (List[str]): 一个包含原始 OOXML 元素字符串的列表。
            add_empty_paragraph (bool): 是否在内容末尾添加一个空的 `<w:p/>` 段落。

        返回:
            str: 处理后的内容片段字符串
        """
        # 将所有传入的 XML 片段合并成一个单一的内容字符串
        combined_content = "".join(xml_fragments)

        # 根据参数决定是否在合并后的内容末尾添加一个空段落
        if add_empty_paragraph:
            combined_content += "<w:p/>"

        return combined_content

    def parse_to_optimized_dict(self, extract_keys_only: bool = False) -> Dict[str, Any]:
        """
        执行优化的解析流程，返回分离了共享部分和内容片段的结构化字典。

        这个版本将OOXML的固定部分（样式、编号、关系等）提取出来作为共享部分，
        每个内容块只包含实际的内容片段，大大减少了数据重复。

        参数:
            extract_keys_only (bool): 如果为 True，则在 key_information 中只保留键，值设为空字符串。

        返回:
            Dict[str, Any]: 包含共享部分和优化后解析结果的字典，结构如下：
            {
                "shared_ooxml_parts": {...},  # 所有OOXML块共享的固定部分
                "sections": [...],             # 文档层级结构，内容块只包含片段
                "key_information": {...}       # 键值对信息，也使用片段格式
            }
        """
        if not self.doc_xml_content:
            return {}

        soup = BeautifulSoup(self.doc_xml_content, "xml")
        body = soup.find("w:body")
        if not body:
            return {}

        # 1. 构建文档层级结构（使用片段格式）
        sections = self._build_document_hierarchy_optimized(body)

        # 2. 生成线性内容块列表（用于提取关键信息）
        linear_content_blocks = []
        for element in body.children:
            if not isinstance(element, Tag) or not element.name:
                continue

            # 检查是否包含图片
            blip_tag = element.find("a:blip", {"r:embed": True})
            if blip_tag:
                r_id = blip_tag["r:embed"]
                image_data = self._process_image_with_oss(r_id, return_text_placeholder=True)
                if image_data:  # 只有非空字符串才创建image数据块
                    linear_content_blocks.append({"type": "image", "data": image_data})
                else:
                    # 如果图片处理失败，保存为内容片段
                    content_fragment = self._create_content_fragment([str(element)])
                    linear_content_blocks.append({"type": "ooxml", "data": content_fragment})
            else:
                content_fragment = self._create_content_fragment([str(element)])
                linear_content_blocks.append({"type": "ooxml", "data": content_fragment})

        # 立即释放soup和body对象以节省内存
        del soup, body
        # 强制垃圾回收以释放内存
        gc.collect()

        # 3. 提取特定部分的信息（使用片段格式）
        # 3.1 提取封面信息
        title_page_data = {}
        split_index = -1
        for i, block in enumerate(linear_content_blocks):
            if block.get("type") == "ooxml":
                element_text = self._get_text_from_element_fragment(block.get("data", ""))
                if element_text:
                    cleaned_text = re.sub(r"\s+", "", element_text)
                    if "保密声明" in cleaned_text or "保密申明" in cleaned_text or "声明" in cleaned_text or "保密" in cleaned_text:
                        split_index = i
                        break

        if split_index > 0:
            title_page_blocks = linear_content_blocks[:split_index]
            title_page_data = self._process_title_page_content_blocks_optimized(title_page_blocks)

        # 3.2 提取摘要信息
        summary_data = {}
        summary_sections = self._find_sections_with_table_by_title(sections, "摘要")
        if summary_sections:
            for section in summary_sections:
                section_summary = self._extract_summary_from_section_optimized(section)
                if section_summary:
                    summary_data.update(section_summary)
                    break

        # 3.3 提取签字页信息
        signature_data = {}
        # 查找所有包含"签字"的章节，而不是只找第一个
        signature_sections = self._find_sections_with_table_by_title(sections, "签字")
        if signature_sections:
            app_logger.info(f"找到 {len(signature_sections)} 个签字相关章节")

            # 使用新的直接OOXML解析方法处理每个签字章节
            for section in signature_sections:
                section_title = section.get("title", "")
                app_logger.info(f"处理签字章节: '{section_title}'")

                # 使用新的直接OOXML解析方法
                section_kv = self._extract_kv_from_section_direct_ooxml(section)
                if section_kv:
                    app_logger.info(
                        f"从章节 '{section_title}' 提取到 {len(section_kv)} 个键值对: {list(section_kv.keys())}"
                    )

                    # 处理章节间的重复键名：如果键已存在，生成唯一键名
                    for key, value in section_kv.items():
                        unique_key = key
                        counter = 1
                        while unique_key in signature_data:
                            counter += 1
                            unique_key = f"{key}_{counter}"

                        if unique_key != key:
                            app_logger.info(f"章节间键名重复，使用唯一键名: '{key}' -> '{unique_key}'")

                        signature_data[unique_key] = value
                else:
                    app_logger.warning(f"章节 '{section_title}' 未提取到任何键值对")

            if signature_data:
                app_logger.info(f"签字页总共提取到 {len(signature_data)} 个键值对: {list(signature_data.keys())}")
            else:
                app_logger.warning("签字页数据提取为空")
        else:
            app_logger.warning("未找到任何包含签字相关关键词的章节")

        # 4. 获取共享的OOXML部分
        shared_ooxml_parts = self._get_ooxml_shared_parts()

        # 5. 生成目录
        table_of_contents = self._generate_table_of_contents(sections)

        # 6. 组装最终结果
        result = {
            "shared_ooxml_parts": shared_ooxml_parts,
            "sections": sections,
            "key_information": {
                "title_page": title_page_data if not extract_keys_only else {k: "" for k in title_page_data.keys()},
                "protocol_summary": summary_data if not extract_keys_only else {k: "" for k in summary_data.keys()},
                "approval_signature_page": signature_data
                if not extract_keys_only
                else {k: "" for k in signature_data.keys()},
                "table_of_contents": table_of_contents,
            },
        }

        return result

    def _package_complete_ooxml(
        self,
        xml_fragments: List[str],
        styles_xml: Optional[bytes],
        numbering_xml: Optional[bytes],
        add_empty_paragraph: bool = False,
    ) -> str:
        """
        [★★ 核心函数 - 将 OOXML 片段包装成可用的完整 OOXML 包 ★★]

        此函数接收一个或多个原始的 OOXML 片段（例如 `<w:p>...</w:p>` 或 `<w:tbl>...</w:tbl>`)，
        并将它们与样式、编号等依赖项一起，包装成一个符合 Office Open XML Package 规范的、
        可以被 Office.js 的 `insertOoxml` API 直接使用的完整 XML 字符串。

        这个“包”是一个扁平化的 XML 结构，使用 `<pkg:part>` 来模拟 ZIP 包中的文件和目录结构。

        参数:
            xml_fragments (List[str]): 一个包含原始 OOXML 元素（如段落、表格）字符串的列表。
            styles_xml (Optional[bytes]): 整个 `word/styles.xml` 文件的字节内容。
            numbering_xml (Optional[bytes]): 整个 `word/numbering.xml` 文件的字节内容。
            add_empty_paragraph (bool): 是否在内容末尾添加一个空的 `<w:p/>` 段落。
                                        这对于修复 Office.js 插入内容时，末尾段落样式被“污染”的问题至关重要。
                                        对于正文内容块，应为 True；对于独立的标题，应为 False。

        返回:
            str: 一个包含了所有必要部分（rels, content_types, styles, numbering, document）的完整 OOXML 包字符串。
                 该字符串经过了压缩，移除了所有换行符。
        """
        # 获取共享部分
        shared_parts = self._get_ooxml_shared_parts()

        # 将所有传入的 XML 片段合并成一个单一的内容字符串
        combined_content = "".join(xml_fragments)

        # 根据参数决定是否在合并后的内容末尾添加一个空段落
        if add_empty_paragraph:
            combined_content += "<w:p/>"

        # 组装文档部分
        document_part = f'<pkg:part pkg:name="/word/document.xml" pkg:contentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"><pkg:xmlData><w:document {shared_parts["ns_declarations"]}><w:body>{combined_content}</w:body></w:document></pkg:xmlData></pkg:part>'

        # 组装最终的 OOXML 包
        ooxml_package = f"""{shared_parts["xml_header"]}
{shared_parts["mso_application"]}
{shared_parts["package_start"]}
{shared_parts["content_types_part"]}
{shared_parts["doc_rels_part"]}
{document_part}
{shared_parts["styles_part"]}
{shared_parts["numbering_part"]}
{shared_parts["package_end"]}
"""
        # 移除所有换行和首尾空格，得到单行字符串，便于API调用
        return "".join(line.strip() for line in ooxml_package.split("\n"))

    def _read_xml(self, path: str) -> Optional[bytes]:
        """
        从 .docx 压缩包中安全地读取一个指定的 XML 文件。

        参数:
            path (str): 要读取的文件在压缩包内的路径 (例如 "word/document.xml")。

        返回:
            Optional[bytes]: 文件的字节内容。如果文件不存在，则返回 None 并记录警告。
        """
        try:
            with self.zip_file.open(path) as f:
                return f.read()
        except KeyError:
            app_logger.warning(f"XML 文件未找到: {path}")
            return None

    def _parse_rels(self) -> Dict[str, str]:
        """
        解析文档的关系文件 (word/_rels/document.xml.rels)。

        这个文件定义了主文档与其他资源（如图片、超链接、页眉页脚）之间的关联。
        我们主要用它来查找图片等内嵌资源的具体文件路径。

        返回:
            Dict[str, str]: 一个关系字典，键是关系ID (rId)，值是目标文件路径。
        """
        rels_content = self._read_xml("word/_rels/document.xml.rels")
        if not rels_content:
            return {}
        soup = BeautifulSoup(rels_content, "xml")
        return {rel["Id"]: rel["Target"] for rel in soup.find_all("Relationship")}

    def _to_points(self, value: Optional[str], unit: str = "dxa") -> Optional[float]:
        """
        将 OOXML 中常用的单位（如 dxa, half-points）转换为标准的“点”(Points)。

        - 'dxa' (twentieths of a point): 1/20 磅，常用于缩进和间距。
        - 'half-points': 1/2 磅，常用于字号。
        - 'eighth-points': 1/8 磅。

        参数:
            value (Optional[str]): 从 XML 中读取的原始值字符串。
            unit (str): 值的单位，默认为 'dxa'。

        返回:
            Optional[float]: 转换后的磅值。如果输入无效，则返回 None。
        """
        if value is None:
            return None
        try:
            numeric_value = float(value)
            if unit == "dxa":
                return numeric_value / 20.0
            if unit == "half-points":
                return numeric_value / 2.0
            if unit == "eighth-points":
                return numeric_value / 8.0
            return numeric_value
        except (ValueError, TypeError):
            return None

    def _extract_character_properties(self, r_pr_tag: Optional[Tag]) -> Dict[str, Any]:
        """
        从 <w:rPr> (Run Properties) 标签中提取字符级别的格式信息。

        例如：加粗、斜体、下划线、字号、颜色等。

        参数:
            r_pr_tag (Optional[Tag]): BeautifulSoup 解析出的 <w:rPr> 标签对象。

        返回:
            Dict[str, Any]: 包含字符格式属性的字典。
        """
        if not r_pr_tag:
            return {}
        properties = {}
        if r_pr_tag.find("w:b"):
            properties["bold"] = True
        if r_pr_tag.find("w:i"):
            properties["italic"] = True
        if u_tag := r_pr_tag.find("w:u"):
            properties["underline"] = u_tag.get("w:val", "single")
        if r_pr_tag.find("w:strike"):
            properties["strike"] = True
        if r_pr_tag.find("w:vertAlign", {"w:val": "superscript"}):
            properties["superscript"] = True
        if r_pr_tag.find("w:vertAlign", {"w:val": "subscript"}):
            properties["subscript"] = True
        if (sz := r_pr_tag.find("w:sz")) and sz.get("w:val"):
            properties["size"] = self._to_points(sz.get("w:val"), "half-points")
        if (color := r_pr_tag.find("w:color")) and color.get("w:val"):
            properties["color"] = color.get("w:val")
        if font_tag := r_pr_tag.find("w:rFonts"):
            properties["font"] = {
                k: v
                for k, v in {
                    "ascii": font_tag.get("w:ascii"),
                    "hAnsi": font_tag.get("w:hAnsi"),
                    "eastAsia": font_tag.get("w:eastAsia"),
                    "hint": font_tag.get("w:hint"),
                }.items()
                if v is not None
            }
        return properties

    def _extract_paragraph_properties(self, p_pr_tag: Optional[Tag]) -> Dict[str, Any]:
        """
        从 <w:pPr> (Paragraph Properties) 标签中提取段落级别的格式信息。

        例如：对齐方式、缩进、行距、段前段后间距等。

        参数:
            p_pr_tag (Optional[Tag]): BeautifulSoup 解析出的 <w:pPr> 标签对象。

        返回:
            Dict[str, Any]: 包含段落和默认字符格式属性的字典。
        """
        if not p_pr_tag:
            return {}
        para_props = {}
        if (jc := p_pr_tag.find("w:jc")) and jc.get("w:val"):
            para_props["alignment"] = jc.get("w:val")
        if ind := p_pr_tag.find("w:ind"):
            para_props["indent"] = {
                k: v
                for k, v in {
                    "left": self._to_points(ind.get("w:left")),
                    "right": self._to_points(ind.get("w:right")),
                    "firstLine": self._to_points(ind.get("w:firstLine")),
                    "hanging": self._to_points(ind.get("w:hanging")),
                }.items()
                if v is not None
            }
        if spacing := p_pr_tag.find("w:spacing"):
            spacing_props = {
                "before": self._to_points(spacing.get("w:before")),
                "after": self._to_points(spacing.get("w:after")),
            }
            if (line_val := spacing.get("w:line")) and (line_rule := spacing.get("w:lineRule")):
                if line_rule == "auto":
                    try:
                        spacing_props["lineHeight"] = {"mode": "multiple", "value": float(line_val) / 240.0}
                    except ValueError:
                        pass
                else:
                    spacing_props["lineHeight"] = {"mode": line_rule, "value": self._to_points(line_val)}
            para_props["spacing"] = {k: v for k, v in spacing_props.items() if v is not None}
        # 段落属性中可能也包含应用于整个段落的默认字符属性 (<w:rPr>)
        char_props = self._extract_character_properties(p_pr_tag.find("w:rPr"))
        result = {}
        if para_props:
            result["paragraph_properties"] = para_props
        if char_props:
            result["character_properties"] = char_props
        return result

    def _extract_table_properties(self, tbl_pr_tag: Optional[Tag]) -> Dict[str, Any]:
        """
        从 <w:tblPr> (Table Properties) 标签中提取表格级别的格式信息。

        例如：表格对齐方式、整体宽度等。

        参数:
            tbl_pr_tag (Optional[Tag]): BeautifulSoup 解析出的 <w:tblPr> 标签对象。

        返回:
            Dict[str, Any]: 包含表格格式属性的字典。
        """
        if not tbl_pr_tag:
            return {}
        properties = {}
        if (jc_tag := tbl_pr_tag.find("w:jc")) and jc_tag.get("w:val"):
            properties["alignment"] = jc_tag.get("w:val")
        if (tbl_w_tag := tbl_pr_tag.find("w:tblW")) and tbl_w_tag.get("w:w"):
            properties["width"] = {"value": self._to_points(tbl_w_tag.get("w:w")), "type": tbl_w_tag.get("w:type")}
        return properties

    def _get_outline_level_from_style(
        self, style_id: str, style_map: Dict[str, Any], visited_styles: Optional[set] = None
    ) -> Optional[int]:
        """
        递归获取样式的大纲级别，支持通过 basedOn 继承链追溯。

        参数:
            style_id (str): 样式ID
            style_map (Dict[str, Any]): 样式映射字典
            visited_styles (Optional[set]): 已访问的样式ID集合，用于防止循环引用

        返回:
            Optional[int]: 大纲级别（0-5对应1-6级标题），如果不是标题样式则返回None
        """
        if visited_styles is None:
            visited_styles = set()

        # 防止循环引用
        if style_id in visited_styles:
            return None
        visited_styles.add(style_id)

        if style_id not in style_map:
            return None

        style_info = style_map[style_id]

        # 如果当前样式已经有level信息，直接返回
        if style_info.get("level") is not None:
            return style_info["level"] - 1  # 转换为0-5的范围

        # 如果没有level信息，检查是否有basedOn，递归查找父样式
        based_on_id = style_info.get("based_on")
        if based_on_id:
            return self._get_outline_level_from_style(based_on_id, style_map, visited_styles)

        return None

    def _get_paragraph_outline_level(self, p_element: Tag) -> Optional[int]:
        """
        获取段落的大纲级别，支持三种方式：
        1. 段落直接定义的 w:outlineLvl（document.xml中的直接覆盖）
        2. 段落样式中定义的 w:outlineLvl
        3. 通过样式继承链追溯的 w:outlineLvl

        参数:
            p_element (Tag): 段落元素

        返回:
            Optional[int]: 大纲级别（1-6），如果不是标题则返回None
        """
        # 方法一：检查段落直接定义的 w:outlineLvl（优先级最高）
        if p_pr := p_element.find("w:pPr"):
            if (outline_lvl := p_pr.find("w:outlineLvl")) and outline_lvl.get("w:val"):
                outline_val = int(outline_lvl.get("w:val"))
                # 只接受0-5的有效大纲级别（对应1-6级标题）
                if 0 <= outline_val <= 5:
                    return outline_val + 1  # 转换为1-6的范围

        # 方法二和三：通过样式获取大纲级别
        if p_pr := p_element.find("w:pPr"):
            if p_style_tag := p_pr.find("w:pStyle"):
                style_id = p_style_tag.get("w:val")
                # 确保 self.styles 已经初始化
                if hasattr(self, "styles") and style_id in self.styles:
                    style_info = self.styles[style_id]
                    if style_info.get("level") is not None:
                        return style_info["level"]

        return None

    def _parse_styles(self, styles_xml: Optional[bytes]) -> Dict[str, Any]:
        """
        解析 `word/styles.xml` 文件，提取所有样式定义。

        此函数构建一个以样式ID为键的字典，值为该样式的详细信息（名称、类型、格式属性）。
        特别地，它会识别出哪些是“标题”样式（例如 "heading 1"）并记录其级别，
        这是构建文档层级结构的基础。

        参数:
            styles_xml (Optional[bytes]): `word/styles.xml` 文件的字节内容。

        返回:
            Dict[str, Any]: 一个包含所有已解析样式的字典。
        """
        if not styles_xml:
            return {}
        soup = BeautifulSoup(styles_xml, "xml")
        style_map = {}

        # 第一遍：解析所有样式的基本信息
        for style in soup.find_all("w:style"):
            style_id = style.get("w:styleId")
            if not style_id:
                continue
            style_type = style.get("w:type")
            name = name_tag.get("w:val") if (name_tag := style.find("w:name")) else ""

            # 处理段落样式
            if style_type == "paragraph":
                if style.get("w:default") == "1":
                    self.default_para_style_id = style_id

                level = None
                based_on_id = None

                # 获取basedOn信息
                if based_on_tag := style.find("w:basedOn"):
                    based_on_id = based_on_tag.get("w:val")

                # 方法一：直接从样式的 <w:pPr><w:outlineLvl> 标签获取大纲级别
                if p_pr := style.find("w:pPr"):
                    if (outline_lvl := p_pr.find("w:outlineLvl")) and outline_lvl.get("w:val"):
                        outline_val = int(outline_lvl.get("w:val"))
                        # 只接受0-5的有效大纲级别（对应1-6级标题）
                        if 0 <= outline_val <= 5:
                            level = outline_val + 1  # 级别从0开始，我们转为从1开始

                # 方法二：如果上面方法失败，尝试从样式名称中用正则匹配 "heading X" 或 "标题 X"
                if level is None:
                    if match := re.search(r"(heading|标题)\s*(\d+)", name, re.IGNORECASE):
                        heading_num = int(match.group(2))
                        # 只接受1-6级标题
                        if 1 <= heading_num <= 6:
                            level = heading_num

                properties = self._extract_paragraph_properties(style.find("w:pPr"))
                if r_pr_props := self._extract_character_properties(style.find("w:rPr")):
                    properties.setdefault("character_properties", {}).update(r_pr_props)

                style_map[style_id] = {
                    "name": name,
                    "level": level,
                    "type": style_type,
                    "properties": properties,
                    "based_on": based_on_id,
                }

            # 处理表格样式
            elif style_type == "table":
                table_props = {
                    "name": name,
                    "type": style_type,
                    "properties": self._extract_table_properties(style.find("w:tblPr")),
                }
                self.table_styles[style_id] = table_props
                style_map[style_id] = table_props

        # 第二遍：处理通过basedOn继承的大纲级别（方法三）
        for style_id, style_info in style_map.items():
            if style_info.get("type") == "paragraph" and style_info.get("level") is None and style_info.get("based_on"):
                # 递归查找父样式的大纲级别
                inherited_level = self._get_outline_level_from_style(style_info["based_on"], style_map)
                if inherited_level is not None and 0 <= inherited_level <= 5:
                    style_info["level"] = inherited_level + 1  # 转换为1-6的范围

        return style_map

    def _parse_numbering(self, num_xml: Optional[bytes]) -> Dict[str, Any]:
        """
        解析 `word/numbering.xml` 文件，提取所有列表编号和项目符号的定义。

        OOXML 中的列表比较复杂，分为 `abstractNum` (抽象定义) 和 `num` (具体实例)。
        此函数将它们解析并关联起来，构建一个以 `numId` 为键的字典，
        值为该列表各级别的格式定义（如 "1, 2, 3", "a, b, c", "•, •, •"）。

        参数:
            num_xml (Optional[bytes]): `word/numbering.xml` 文件的字节内容。

        返回:
            Dict[str, Any]: 一个包含所有已解析编号列表定义的字典。
        """
        if not num_xml:
            return {}
        soup = BeautifulSoup(num_xml, "xml")

        # 1. 解析抽象编号定义 (abstractNum)
        abstract_nums = {}
        for anum in soup.find_all("w:abstractNum"):
            abstract_num_id = anum.get("w:abstractNumId")
            if not abstract_num_id:
                continue
            levels = {}
            for lvl in anum.find_all("w:lvl"):
                ilvl, num_fmt_tag = lvl.get("w:ilvl"), lvl.find("w:numFmt")
                lvl_text_tag, start_tag = lvl.find("w:lvlText"), lvl.find("w:start")
                if not (ilvl and num_fmt_tag):
                    continue
                level_data = {
                    "format": num_fmt_tag.get("w:val"),
                    "text": lvl_text_tag.get("w:val") if lvl_text_tag else "",
                    "start": int(start_tag.get("w:val")) if start_tag and start_tag.get("w:val") else 1,
                }
                levels[ilvl] = level_data
            abstract_nums[abstract_num_id] = levels

        # 2. 解析具体编号实例 (num)，并将其链接到抽象定义
        num_map = {}
        for num in soup.find_all("w:num"):
            num_id = num.get("w:numId")
            if not num_id:
                continue
            if abstract_num_id_tag := num.find("w:abstractNumId"):
                abstract_num_id = abstract_num_id_tag.get("w:val")
                if abstract_num_id in abstract_nums:
                    num_map[num_id] = abstract_nums[abstract_num_id]
        return num_map

    def _get_image_data(self, r_id: str) -> Optional[str]:
        """
        根据资源关系ID (rId) 获取图片的 Base64 编码字符串。

        注意：此方法保留用于向后兼容，新代码应使用 _process_image_with_oss
        """
        if r_id in self.rels:
            target = self.rels[r_id]
            from os.path import join, normpath

            # 路径需要规范化，因为 target 可能是 "../media/image1.png" 这样的相对路径
            base_path = "word"
            image_path = normpath(join(base_path, target)).replace("\\", "/")
            try:
                with self.zip_file.open(image_path) as img_file:
                    return base64.b64encode(img_file.read()).decode("utf-8")
            except KeyError:
                app_logger.error(f"图片文件未在压缩包中找到: {image_path}")
        return None

    def _process_image_with_oss(self, r_id: str, return_text_placeholder: bool = False) -> Optional[str]:
        """
        处理图片：优先上传到OSS，失败时跳过图片

        参数:
            r_id (str): 图片的资源关系ID
            return_text_placeholder (bool): 是否返回纯文本占位符格式（用于type="image"数据块）

        返回:
            Optional[str]:
                - 如果OSS上传成功且return_text_placeholder=True：返回OSS key路径（如：protocol-images/2025/08/02/abc123.png）
                - 如果OSS上传成功且return_text_placeholder=False：返回包含OSS占位符的OOXML字符串
                - 如果OSS上传失败或OSS模块不可用：返回None（跳过图片）
                - 如果图片不存在：返回None
        """
        if r_id not in self.rels:
            app_logger.error(f"图片关系ID未找到: {r_id}")
            return None

        target = self.rels[r_id]
        from os.path import join, normpath

        # 路径需要规范化
        base_path = "word"
        image_path = normpath(join(base_path, target)).replace("\\", "/")

        try:
            with self.zip_file.open(image_path) as img_file:
                image_data = img_file.read()

            # 尝试直接上传原始图片文件到OSS
            if upload_image_to_oss is not None:
                # 获取文件扩展名
                file_extension = image_path.split(".")[-1].lower()
                if file_extension not in ["png", "jpg", "jpeg", "gif", "bmp"]:
                    file_extension = "png"  # 默认扩展名

                # 直接上传原始图片数据
                from utils.oss_utils import create_image_placeholder, create_image_text_placeholder, upload_image

                # 尝试上传到OSS，最多重试3次
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        oss_url = upload_image(image_data, file_extension)
                        if oss_url:
                            # OSS上传成功，立即释放图片数据内存并返回占位符
                            del image_data  # 立即释放内存

                            if return_text_placeholder:
                                # 返回纯文本格式的占位符（用于type="image"数据块）
                                placeholder_text = create_image_text_placeholder(oss_url)
                                app_logger.info(f"图片已上传到OSS，返回文本占位符: {oss_url}")
                                return placeholder_text
                            else:
                                # 返回XML格式的占位符（用于OOXML文档中）
                                placeholder_xml = create_image_placeholder(oss_url)
                                app_logger.info(f"图片已上传到OSS，返回XML占位符: {oss_url}")
                                return placeholder_xml
                        else:
                            # OSS上传失败，记录并准备重试
                            app_logger.warning(f"图片OSS上传失败，尝试 {attempt + 1}/{max_retries}: {r_id}")
                            if attempt < max_retries - 1:
                                import time

                                time.sleep(1)  # 等待1秒后重试

                    except Exception as e:
                        # OSS上传异常，记录并准备重试
                        app_logger.warning(f"OSS上传异常，尝试 {attempt + 1}/{max_retries}: {e}")
                        if attempt < max_retries - 1:
                            import time

                            time.sleep(1)  # 等待1秒后重试

                # 所有重试都失败了
                del image_data  # 释放原始图片数据内存

                if return_text_placeholder:
                    # 对于 type="image" 数据块，返回空字符串
                    app_logger.error(f"图片OSS上传重试{max_retries}次均失败，返回空字符串: {r_id}")
                    return ""
                else:
                    # 对于OOXML文档中的图片，OSS上传失败时也不插入图片
                    app_logger.warning(f"图片OSS上传重试{max_retries}次均失败，跳过图片插入: {r_id}")
                    return None
            else:
                # OSS模块不可用的处理
                del image_data  # 释放原始图片数据内存

                if return_text_placeholder:
                    # 对于 type="image" 数据块，返回空字符串
                    app_logger.error("OSS模块不可用，type='image'数据块返回空字符串")
                    return ""
                else:
                    # 对于OOXML文档中的图片，OSS不可用时也不插入图片
                    app_logger.warning("OSS模块不可用，跳过图片插入")
                    return None

        except KeyError:
            app_logger.error(f"图片文件未在压缩包中找到: {image_path}")
            return None
        except Exception as e:
            app_logger.error(f"处理图片时发生错误: {e}")
            return None

    def _process_paragraph_images(self, paragraph: Tag) -> str:
        """
        处理段落中的图片，将图片上传到OSS并替换为占位符

        参数:
            paragraph: BeautifulSoup解析的段落标签

        返回:
            str: 处理后的段落XML字符串
        """
        # 创建段落的副本以避免修改原始对象
        p_copy = BeautifulSoup(str(paragraph), "xml").find("w:p")

        if p_copy is None:
            # 如果没有找到w:p标签，返回原始内容
            app_logger.warning("未找到w:p标签，返回原始段落内容")
            return str(paragraph)

        # 查找所有图片元素
        blip_tags = p_copy.find_all("a:blip", {"r:embed": True})

        for blip_tag in blip_tags:
            r_id = blip_tag.get("r:embed")
            if r_id:
                # 处理图片（上传到OSS，失败时跳过）
                image_result = self._process_image_with_oss(r_id)

                if image_result and image_result.startswith("<w:p>"):
                    # 如果返回的是OSS占位符OOXML，提取其中的文本内容
                    placeholder_soup = BeautifulSoup(image_result, "xml")
                    placeholder_texts = placeholder_soup.find_all("w:t")

                    if placeholder_texts:
                        # 找到包含图片的drawing元素，替换为文本
                        drawing = blip_tag.find_parent("w:drawing")
                        if drawing:
                            # 创建新的文本run来替换图片
                            new_run = p_copy.new_tag("w:r")
                            for text_elem in placeholder_texts:
                                new_t = p_copy.new_tag("w:t")
                                new_t.string = text_elem.get_text()
                                new_run.append(new_t)
                                # 添加换行
                                if text_elem != placeholder_texts[-1]:
                                    new_br = p_copy.new_tag("w:br")
                                    new_run.append(new_br)

                            # 替换drawing元素
                            drawing.replace_with(new_run)
                            app_logger.info(f"图片 {r_id} 已替换为OSS占位符")
                        else:
                            app_logger.warning(f"未找到图片 {r_id} 的drawing父元素")
                else:
                    app_logger.warning(f"图片 {r_id} 处理失败，保留原始图片")

        return str(p_copy)

    def _parse_runs(self, p_tag: Tag) -> str:
        """
        解析一个段落标签(<w:p>)中的所有文本块(<w:r>)，并拼接它们的文本内容(<w:t>)。

        一个段落的文本可能被分割在多个 "run" 中，每个 run 可以有不同的格式。
        此函数只提取纯文本内容。

        参数:
            p_tag (Tag): BeautifulSoup 解析出的 <w:p> 标签对象。

        返回:
            str: 该段落的完整纯文本内容。
        """
        return "".join(t.text for t in p_tag.find_all("w:t"))

    def _get_paragraph_text(self, p_element: Any) -> str:
        """
        从段落的 XML 元素或字符串中提取纯文本。
        这是一个对 `_parse_runs` 的封装，可以处理字符串或 BeautifulSoup 标签。

        参数:
            p_element (Any): 可以是 <w:p> 元素的 XML 字符串，或 BeautifulSoup 的 Tag 对象。

        返回:
            str: 段落的纯文本。
        """
        if isinstance(p_element, str):
            p_element = BeautifulSoup(p_element, "xml").find("w:p")
        if p_element:
            return self._parse_runs(p_element)
        return ""

    def _get_text_from_element(self, element_xml: str) -> str:
        """
        从任何给定的 OOXML 元素（字符串格式）中递归地提取所有纯文本。

        这对于从一个大的 OOXML 块（可能包含多个段落、表格）中提取全部文本很有用。

        参数:
            element_xml (str): 包含一个或多个 OOXML 元素的 XML 字符串。

        返回:
            str: 拼接后的所有纯文本。
        """
        soup = BeautifulSoup(element_xml, "xml")
        all_text = []
        for p_tag in soup.find_all("w:p"):
            text = self._parse_runs(p_tag)
            if text.strip():
                all_text.append(text)
        return "".join(all_text)

    def _get_text_from_element_fragment(self, fragment: str) -> str:
        """
        从内容片段中提取纯文本。

        参数:
            fragment (str): 内容片段字符串（不包含完整的OOXML包装）

        返回:
            str: 提取的纯文本
        """
        # 为片段创建一个临时的完整OOXML包来解析
        temp_ooxml = self._package_complete_ooxml(
            [fragment], self.styles_xml_content, self.numbering_xml_content, add_empty_paragraph=False
        )
        return self._get_text_from_element(temp_ooxml)

    def _get_text_from_cell_content(self, content_list: List[Dict[str, str]]) -> str:
        """
        从一个包含多个内容块的列表中提取所有纯文本。
        这主要用于处理表格单元格，因为一个单元格可能包含多个段落。

        参数:
            content_list (List[Dict[str, str]]): 内容块列表，每个块是一个字典。

        返回:
            str: 拼接后的所有纯文本。
        """
        full_text = []
        for block in content_list:
            if block.get("type") == "ooxml":
                text = self._get_text_from_element(block.get("data", ""))
                if text.strip():
                    full_text.append(text)
        return "".join(full_text).strip()

    def _extract_kv_from_table_block(self, table_block: Dict[str, str]) -> Dict[str, str]:
        """
        从一个包含表格的 OOXML 内容块中，提取键值对（Key-Value）。

        此函数假定表格是两列的结构，第一列是键，第二列是值。
        现在返回的值是完整的 OOXML 包，而不是纯文本。

        参数:
            table_block (Dict[str, str]): 类型为 'ooxml' 的内容块，其 'data' 字段包含表格的 OOXML。

        返回:
            Dict[str, str]: 从表格中提取的键值对字典，值为完整的 OOXML 包。
        """
        kv_data = {}
        if table_block.get("type") != "ooxml":
            return kv_data
        table_xml = table_block.get("data", "")
        soup = BeautifulSoup(table_xml, "xml")
        table = soup.find("w:tbl")
        if not table:
            return kv_data
        for row in table.find_all("w:tr", recursive=False):
            cells = row.find_all("w:tc", recursive=False)
            if len(cells) == 2:
                key_text = self._get_paragraph_text(cells[0])
                if key_text:
                    # 提取第二列的所有内容元素，按原始顺序处理
                    content_blocks = []

                    # 获取单元格的所有直接子元素（段落和表格），保持原始顺序
                    cell_children = cells[1].find_all(["w:p", "w:tbl"], recursive=False)

                    for child in cell_children:
                        try:
                            if child.name == "w:p":
                                # 处理段落元素
                                # 检查段落是否有文本内容，过滤空段落
                                paragraph_text = self._get_paragraph_text(child)
                                if not paragraph_text or not paragraph_text.strip():
                                    continue  # 跳过空段落

                                # 检查段落是否包含图片
                                if child.find("w:drawing") or child.find("w:pict"):
                                    # 包含图片的段落，直接提取图片并上传到OSS
                                    blip_tags = child.find_all("a:blip", {"r:embed": True})
                                    if blip_tags:
                                        # 如果段落包含图片，为每个图片创建一个image数据块
                                        for blip_tag in blip_tags:
                                            r_id = blip_tag.get("r:embed")
                                            if r_id:
                                                image_data = self._process_image_with_oss(
                                                    r_id, return_text_placeholder=True
                                                )
                                                if image_data:  # 只有非空字符串才创建image数据块
                                                    content_blocks.append({"type": "image", "data": image_data})
                                    else:
                                        # 如果没有找到图片引用，回退到原来的处理方式
                                        processed_paragraph = self._process_paragraph_images(child)
                                        paragraph_ooxml = self._package_complete_ooxml(
                                            [processed_paragraph],
                                            self.styles_xml_content,
                                            self.numbering_xml_content,
                                        )
                                        content_blocks.append({"type": "ooxml", "data": paragraph_ooxml})
                                else:
                                    # 纯文本段落，标记为 ooxml 类型
                                    paragraph_ooxml = self._package_complete_ooxml(
                                        [str(child)],
                                        self.styles_xml_content,
                                        self.numbering_xml_content,
                                    )
                                    content_blocks.append({"type": "ooxml", "data": paragraph_ooxml})

                            elif child.name == "w:tbl":
                                # 处理嵌套表格元素
                                table_ooxml = self._package_complete_ooxml(
                                    [str(child)],
                                    self.styles_xml_content,
                                    self.numbering_xml_content,
                                )
                                content_blocks.append({"type": "ooxml", "data": table_ooxml})

                        except Exception as e:
                            # 如果包装失败，记录错误但继续处理
                            print(f"警告：内容包装失败: {e}")
                            print(f"元素内容: {str(child)[:200]}...")
                            continue

                    # 统一返回数组格式 list[object]
                    if content_blocks:  # 只有当有内容块时才添加
                        kv_data[key_text.strip()] = content_blocks
        return kv_data

    def _extract_kv_from_colon_paragraph_block(self, p_block: Dict[str, str]) -> Optional[Tuple[str, str]]:
        """
        从一个段落内容块中，提取由冒号分隔的键值对。

        例如，对于文本 "项目名称：XXX项目"，此函数会提取键和对应的完整 OOXML 包。
        支持中英文冒号。现在返回的值是完整的 OOXML 包，而不是纯文本。

        参数:
            p_block (Dict[str, str]): 类型为 'ooxml' 的内容块，其 'data' 字段包含段落的 OOXML。

        返回:
            Optional[Tuple[str, str]]: 如果成功提取，返回 (键, 完整OOXML包) 元组；否则返回 None。
        """
        if p_block.get("type") != "ooxml":
            app_logger.debug(f"跳过非ooxml类型的块: {p_block.get('type')}")
            return None

        # 首先提取纯文本来判断是否包含冒号
        text = self._get_paragraph_text(p_block.get("data", "")).strip()
        app_logger.debug(f"段落文本内容: '{text}'")

        # 兼容中文和英文冒号
        if "：" in text:
            parts = text.split("：", 1)
            app_logger.debug(f"找到中文冒号，分割结果: {parts}")
        elif ":" in text:
            parts = text.split(":", 1)
            app_logger.debug(f"找到英文冒号，分割结果: {parts}")
        else:
            app_logger.debug(f"未找到冒号，跳过段落: '{text}'")
            return None

        key = parts[0].strip()
        if key:
            app_logger.debug(f"提取到键: '{key}'")
            try:
                # 检查段落是否包含图片
                paragraph_data = p_block.get("data", "")
                soup = BeautifulSoup(paragraph_data, "xml")

                # 检查是否包含图片元素
                if soup.find("w:drawing") or soup.find("w:pict"):
                    content_type = "image"
                    # 对包含图片的段落进行OSS处理
                    processed_paragraph = self._process_paragraph_images(soup.find("w:p"))
                    paragraph_ooxml = self._package_complete_ooxml(
                        [processed_paragraph],
                        self.styles_xml_content,
                        self.numbering_xml_content,
                    )
                else:
                    content_type = "ooxml"
                    # 将整个段落包装成完整的 OOXML 包
                    paragraph_ooxml = self._package_complete_ooxml(
                        [paragraph_data],
                        self.styles_xml_content,
                        self.numbering_xml_content,
                    )
                # 使用与 sections 相同的数据结构
                value_data = {"type": content_type, "data": paragraph_ooxml}
                return key, value_data
            except Exception as e:
                # 如果包装失败，记录错误并返回 None
                print(f"警告：冒号段落包装失败: {e}")
                print(f"段落内容: {paragraph_data[:200]}...")
                return None
        return None

    def _process_title_page_content_blocks(self, content_blocks: List[Dict[str, str]]) -> Dict[str, str]:
        """
        处理文档标题页（封面）的内容块，从中提取所有的键值对信息。

        它会综合运用表格解析和冒号段落解析两种策略。

        参数:
            content_blocks (List[Dict[str, str]]): 从文档开头到特定分隔符（如“保密声明”）之间的所有内容块。

        返回:
            Dict[str, str]: 从标题页提取的所有键值对的集合。
        """
        kv_data = {}
        app_logger.debug(f"开始处理 {len(content_blocks)} 个内容块")

        for i, block in enumerate(content_blocks):
            app_logger.debug(f"处理第 {i + 1} 个块，类型: {block.get('type')}")
            if block.get("type") != "ooxml":
                app_logger.debug("跳过非ooxml块")
                continue

            soup = BeautifulSoup(block.get("data", ""), "xml")
            # 如果块是表格，用表格解析器
            if soup.find("w:tbl"):
                app_logger.debug("发现表格，使用表格解析器")
                table_kvs = self._extract_kv_from_table_block(block)
                app_logger.debug(f"表格解析结果: {list(table_kvs.keys()) if table_kvs else '无数据'}")
                kv_data.update(table_kvs)
            # 如果块是段落，用冒号段落解析器
            elif soup.find("w:p"):
                app_logger.debug("发现段落，使用冒号段落解析器")
                p_kv = self._extract_kv_from_colon_paragraph_block(block)
                if p_kv:
                    app_logger.debug(f"段落解析成功: 键='{p_kv[0]}'")
                    # 统一返回数组格式 list[object]
                    kv_data[p_kv[0]] = [p_kv[1]]
                else:
                    app_logger.debug("段落解析无结果")
            else:
                app_logger.debug("块中既无表格也无段落")

        app_logger.debug(f"最终提取到 {len(kv_data)} 个键值对: {list(kv_data.keys())}")
        return kv_data

    def _process_title_page_content_blocks_optimized(self, content_blocks: List[Dict[str, str]]) -> Dict[str, str]:
        """
        处理文档标题页（封面）的内容块，从中提取所有的键值对信息（优化版本）。

        与原版本的区别：
        - 处理的是内容片段而非完整OOXML包
        - 返回的值也是内容片段格式

        参数:
            content_blocks (List[Dict[str, str]]): 从文档开头到特定分隔符之间的所有内容块（片段格式）。

        返回:
            Dict[str, str]: 从标题页提取的所有键值对的集合（值为片段格式）。
        """
        kv_data = {}
        app_logger.debug(f"开始处理 {len(content_blocks)} 个内容块（优化版本）")

        for i, block in enumerate(content_blocks):
            app_logger.debug(f"处理第 {i + 1} 个块，类型: {block.get('type')}")
            if block.get("type") != "ooxml":
                app_logger.debug("跳过非ooxml块")
                continue

            # 对于片段，需要临时包装成完整OOXML来解析结构
            fragment_data = block.get("data", "")
            temp_ooxml = self._package_complete_ooxml(
                [fragment_data], self.styles_xml_content, self.numbering_xml_content, add_empty_paragraph=False
            )

            soup = BeautifulSoup(temp_ooxml, "xml")
            # 如果块是表格，用表格解析器
            if soup.find("w:tbl"):
                app_logger.debug("发现表格，使用表格解析器")
                table_kvs = self._extract_kv_from_table_block_optimized(fragment_data)
                app_logger.debug(f"表格解析结果: {list(table_kvs.keys()) if table_kvs else '无数据'}")
                kv_data.update(table_kvs)
            # 如果块是段落，用冒号段落解析器
            elif soup.find("w:p"):
                app_logger.debug("发现段落，使用冒号段落解析器")

                # 首先尝试多键值对解析（适用于签字页等包含多个键值对的长段落）
                multiple_kvs = self._extract_multiple_kv_from_paragraph_optimized(fragment_data)
                if multiple_kvs:
                    app_logger.debug(f"多键值对解析成功: {list(multiple_kvs.keys())}")
                    kv_data.update(multiple_kvs)
                else:
                    app_logger.debug("多键值对解析无结果，尝试单键值对解析")
                    # 如果多键值对解析失败，回退到单键值对解析
                    p_kv = self._extract_kv_from_colon_paragraph_block_optimized(fragment_data)
                    if p_kv:
                        app_logger.debug(f"单键值对解析成功: 键='{p_kv[0]}'")
                        # 统一返回数组格式 list[object]
                        kv_data[p_kv[0]] = [p_kv[1]]
                    else:
                        app_logger.debug("单键值对解析也无结果")
            else:
                app_logger.debug("块中既无表格也无段落")

        app_logger.debug(f"最终提取到 {len(kv_data)} 个键值对: {list(kv_data.keys())}")
        return kv_data

    def _extract_kv_from_table_block_optimized(self, table_fragment: str) -> Dict[str, str]:
        """
        从一个包含表格的内容片段中，提取键值对（修正版本）。

        正确的处理逻辑：
        - 提取表格右列（value列）的所有内容元素（段落和嵌套表格）
        - 将这些元素作为独立的内容块，就像sections中的content_blocks一样
        - 不保留表格结构，只保留内容元素本身的样式和格式
        - 确保每个段落和表格都保持完整的OOXML结构

        参数:
            table_fragment (str): 包含表格的内容片段

        返回:
            Dict[str, List]: 从表格中提取的键值对字典，值为内容块数组格式。
        """
        kv_data = {}

        # 临时包装成完整OOXML来解析
        temp_ooxml = self._package_complete_ooxml(
            [table_fragment], self.styles_xml_content, self.numbering_xml_content, add_empty_paragraph=False
        )

        soup = BeautifulSoup(temp_ooxml, "xml")
        table = soup.find("w:tbl")
        if not table:
            return kv_data

        for row in table.find_all("w:tr", recursive=False):
            cells = row.find_all("w:tc", recursive=False)
            if len(cells) == 2:
                key_text = self._get_paragraph_text(cells[0])
                if key_text:
                    # 正确的处理：提取第二列的所有内容元素（段落和嵌套表格），按原始顺序处理
                    content_blocks = []

                    # 按照XML中的原始顺序处理所有直接子元素
                    for child in cells[1].children:
                        if hasattr(child, "name"):
                            if child.name == "p":
                                # 处理段落元素
                                p = child

                                # 检查段落是否有文本内容，过滤空段落
                                paragraph_text = self._get_paragraph_text(p)
                                if not paragraph_text or not paragraph_text.strip():
                                    continue  # 跳过空段落

                                try:
                                    # 检查段落是否包含图片
                                    if p.find("w:drawing") or p.find("w:pict"):
                                        # 包含图片的段落，直接提取图片并上传到OSS
                                        blip_tags = p.find_all("a:blip", {"r:embed": True})
                                        if blip_tags:
                                            # 如果段落包含图片，为每个图片创建一个image数据块
                                            for blip_tag in blip_tags:
                                                r_id = blip_tag.get("r:embed")
                                                if r_id:
                                                    image_data = self._process_image_with_oss(
                                                        r_id, return_text_placeholder=True
                                                    )
                                                    if image_data:  # 只有非空字符串才创建image数据块
                                                        content_blocks.append({"type": "image", "data": image_data})
                                        else:
                                            # 如果没有找到图片引用，创建内容片段
                                            paragraph_fragment = self._create_content_fragment([str(p)])
                                            content_blocks.append({"type": "ooxml", "data": paragraph_fragment})
                                    else:
                                        # 纯文本段落，创建内容片段
                                        paragraph_fragment = self._create_content_fragment([str(p)])
                                        content_blocks.append({"type": "ooxml", "data": paragraph_fragment})
                                except Exception as e:
                                    # 如果包装失败，记录错误但继续处理
                                    app_logger.warning(f"段落片段创建失败: {e}")
                                    app_logger.debug(f"段落内容: {str(p)[:200]}...")
                                    continue

                            elif child.name == "tbl":
                                # 处理嵌套表格元素
                                try:
                                    # 将嵌套表格创建为内容片段
                                    table_fragment = self._create_content_fragment([str(child)])
                                    content_blocks.append({"type": "ooxml", "data": table_fragment})
                                except Exception as e:
                                    app_logger.warning(f"嵌套表格片段创建失败: {e}")
                                    app_logger.debug(f"表格内容: {str(child)[:200]}...")
                                    continue

                    # 统一返回数组格式 list[object]
                    if content_blocks:  # 只有当有内容块时才添加
                        kv_data[key_text.strip()] = content_blocks
        return kv_data

    def _extract_kv_from_colon_paragraph_block_optimized(self, paragraph_fragment: str) -> Optional[Tuple[str, str]]:
        """
        从一个段落内容片段中，提取由冒号分隔的键值对（增强版本）。

        增强功能：
        - 通过删除包含key的<w:r>元素来保留完整的value部分
        - 保持原段落的样式信息（w:pPr）和其他格式
        - 确保value部分的OOXML结构完整

        参数:
            paragraph_fragment (str): 包含段落的内容片段

        返回:
            Optional[Tuple[str, str]]: 如果成功提取，返回 (键, 内容片段) 元组；否则返回 None。
        """
        # 临时包装成完整OOXML来解析结构
        temp_ooxml = self._package_complete_ooxml(
            [paragraph_fragment], self.styles_xml_content, self.numbering_xml_content, add_empty_paragraph=False
        )

        # 首先提取纯文本来判断是否包含冒号
        text = self._get_text_from_element(temp_ooxml).strip()
        app_logger.debug(f"段落文本内容: '{text}'")

        # 兼容中文和英文冒号
        colon_char = None
        if "：" in text:
            parts = text.split("：", 1)
            colon_char = "："
            app_logger.debug(f"找到中文冒号，分割结果: {parts}")
        elif ":" in text:
            parts = text.split(":", 1)
            colon_char = ":"
            app_logger.debug(f"找到英文冒号，分割结果: {parts}")
        else:
            app_logger.debug(f"未找到冒号，跳过段落: '{text}'")
            return None

        key = parts[0].strip()
        if key:
            app_logger.debug(f"提取到键: '{key}'")
            try:
                # 关键改进：创建只包含value部分的段落
                value_paragraph = self._create_value_only_paragraph(paragraph_fragment, key, colon_char)

                if value_paragraph:
                    # 检查是否包含图片
                    if value_paragraph.find("w:drawing") or value_paragraph.find("w:pict"):
                        content_type = "image"
                    else:
                        content_type = "ooxml"

                    # 将value段落转换为内容片段
                    value_fragment = self._create_content_fragment([str(value_paragraph)])
                    value_data = {"type": content_type, "data": value_fragment}
                    return key, value_data
                else:
                    app_logger.debug("创建value段落失败")
                    return None

            except Exception as e:
                # 如果处理失败，记录错误并返回 None
                app_logger.warning(f"增强段落键值对处理失败: {e}")
                app_logger.debug(f"段落内容: {paragraph_fragment[:200]}...")
                return None
        return None

    def _create_value_only_paragraph(self, paragraph_fragment: str, key: str, colon_char: str):
        """
        创建一个只包含value部分的段落，删除包含key的<w:r>元素。

        参数:
            paragraph_fragment (str): 原始段落片段
            key (str): 要删除的键名
            colon_char (str): 冒号字符（中文或英文）

        返回:
            BeautifulSoup Tag: 新的段落元素，只包含value部分
        """
        try:
            # 解析段落片段
            paragraph_xml = f'<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">{paragraph_fragment}</w:p>'
            soup = BeautifulSoup(paragraph_xml, "xml")
            paragraph = soup.find("w:p")

            if not paragraph:
                return None

            # 创建新段落，保留原段落的属性
            new_paragraph_xml = '<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"></w:p>'
            new_soup = BeautifulSoup(new_paragraph_xml, "xml")
            new_paragraph = new_soup.find("w:p")

            # 复制段落属性（w:pPr）
            if paragraph.find("w:pPr"):
                import copy

                new_paragraph.append(copy.deepcopy(paragraph.find("w:pPr")))

            # 分析所有的<w:r>元素，删除包含key的部分，保留value部分
            key_with_colon = key + colon_char
            found_key = False

            for run in paragraph.find_all("w:r"):
                run_text = run.get_text()

                if not found_key and key_with_colon in run_text:
                    # 这个run包含key和冒号，需要处理
                    found_key = True

                    # 找到冒号后的内容
                    colon_index = run_text.find(colon_char)
                    if colon_index >= 0 and colon_index < len(run_text) - 1:
                        # 冒号后还有内容，保留这部分
                        value_text = run_text[colon_index + 1 :]
                        if value_text.strip():  # 如果有非空白内容
                            import copy

                            new_run = copy.deepcopy(run)
                            # 更新文本内容
                            text_element = new_run.find("w:t")
                            if text_element:
                                text_element.string = value_text
                                new_paragraph.append(new_run)
                    # 如果冒号后没有内容，就不添加这个run

                elif found_key:
                    # key已经找到，这个run是value的一部分
                    import copy

                    new_paragraph.append(copy.deepcopy(run))
                # 如果还没找到key，跳过这个run

            # 如果没有找到key，返回None
            if not found_key:
                app_logger.debug(f"在段落中未找到键: '{key_with_colon}'")
                return None

            return new_paragraph

        except Exception as e:
            app_logger.warning(f"创建value段落失败: {e}")
            return None

    def _extract_kv_from_ooxml_paragraph_direct(self, paragraph_ooxml: str) -> Tuple[str, str, str]:
        """
        直接从OOXML段落中提取键值对，返回(key, value_ooxml, remaining_ooxml)。

        这个方法直接在OOXML层面操作，找到包含冒号的段落，
        将冒号前的部分作为键，冒号后的部分作为值的OOXML。

        参数:
            paragraph_ooxml (str): 单个段落的OOXML内容

        返回:
            Tuple[str, str, str]: (键名, 值的OOXML, 剩余的OOXML)
            如果没有找到键值对，返回 (None, None, paragraph_ooxml)
        """
        from bs4 import BeautifulSoup

        try:
            app_logger.debug(f"开始解析段落OOXML: {paragraph_ooxml[:100]}...")

            # 先提取段落的纯文本，检查是否包含冒号
            temp_soup = BeautifulSoup(paragraph_ooxml, "xml")
            full_text = temp_soup.get_text()
            app_logger.debug(f"段落完整文本: '{full_text}'")

            # 查找冒号位置
            colon_pos = -1
            for pos, char in enumerate(full_text):
                if char in [":", "："]:
                    colon_pos = pos
                    break

            if colon_pos == -1:
                app_logger.debug(f"段落中未找到冒号，文本: '{full_text[:100]}'")
                return None, None, paragraph_ooxml

            # 提取键名（冒号前的文本）
            key_text = full_text[:colon_pos].strip()
            if not key_text or len(key_text) > 50:  # 过滤无效键名
                app_logger.debug(f"键名无效: '{key_text}'")
                return None, None, paragraph_ooxml

            # 提取值（冒号后的文本）
            value_text = full_text[colon_pos + 1 :].strip()
            app_logger.debug(f"提取的value_text: '{value_text}', 长度: {len(value_text)}")
            if not value_text:  # 如果值为空，不提取这个键值对
                app_logger.debug(f"键 '{key_text}' 的值为空，跳过")
                return None, None, paragraph_ooxml

            app_logger.debug(f"找到键名: '{key_text}', 值: '{value_text[:50]}...'")

            # 简化处理：直接基于冒号位置创建只包含值的段落
            # 重新解析OOXML，修改文本内容
            app_logger.debug(f"原始段落OOXML前100字符: {paragraph_ooxml[:100]}")

            # 添加命名空间声明
            ooxml_with_ns = (
                f'<root xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">{paragraph_ooxml}</root>'
            )
            soup = BeautifulSoup(ooxml_with_ns, "xml")
            paragraph = soup.find("w:p")
            app_logger.debug(f"解析段落: paragraph={'找到' if paragraph else '未找到'}")

            if not paragraph:
                app_logger.debug("未找到段落元素")
                return None, None, paragraph_ooxml

            # 找到所有文本元素，移除键名部分，只保留值部分
            all_text_elements = paragraph.find_all("w:t")
            app_logger.debug(f"找到 {len(all_text_elements)} 个文本元素")
            if not all_text_elements:
                app_logger.debug("未找到文本元素")
                return None, None, paragraph_ooxml

            # 重新构建段落，只包含值的部分
            # 先找到冒号的位置，然后重新设置文本
            full_text = "".join([t.text for t in all_text_elements if t.text])
            colon_pos = -1
            for pos, char in enumerate(full_text):
                if char in [":", "："]:
                    colon_pos = pos
                    break

            if colon_pos == -1:
                return None, None, paragraph_ooxml

            # 提取值部分
            value_part = full_text[colon_pos + 1 :].strip()
            app_logger.debug(f"提取的值部分: '{value_part}'")
            if not value_part:
                app_logger.debug("值部分为空，跳过")
                return None, None, paragraph_ooxml

            # 创建新的段落，只包含值
            new_paragraph = soup.new_tag("w:p")

            # 复制段落属性
            ppr = paragraph.find("w:pPr")
            if ppr:
                import copy

                new_paragraph.append(copy.deepcopy(ppr))

            # 创建新的run和文本
            new_run = soup.new_tag("w:r")

            # 复制第一个run的属性（如果存在）
            first_run = paragraph.find("w:r")
            if first_run and first_run.find("w:rPr"):
                import copy

                new_run.append(copy.deepcopy(first_run.find("w:rPr")))

            # 添加值文本
            new_t = soup.new_tag("w:t")
            new_t.string = value_part
            new_run.append(new_t)
            new_paragraph.append(new_run)

            # 生成值的OOXML
            value_ooxml = str(new_paragraph)

            app_logger.debug(f"成功分离键值对: '{key_text}' -> 值OOXML长度={len(value_ooxml)}")
            app_logger.debug(f"返回值: key='{key_text}', value_ooxml长度={len(value_ooxml) if value_ooxml else 0}")

            return key_text, value_ooxml, ""

        except Exception as e:
            app_logger.warning(f"OOXML段落解析失败: {e}")
            app_logger.debug(f"异常详情: {str(e)}")
            import traceback

            app_logger.debug(f"异常堆栈: {traceback.format_exc()}")
            return None, None, paragraph_ooxml

    def _extract_multiple_kv_from_paragraph_optimized(self, paragraph_fragment: str) -> Dict[str, Any]:
        """
        从一个包含多个键值对的长段落中提取所有键值对（优化版本）。

        这个方法专门处理像签字页这样的情况，其中多个键值对被合并在一个段落中。

        参数:
            paragraph_fragment (str): 包含多个键值对的段落片段

        返回:
            Dict[str, Any]: 提取的键值对字典
        """
        kv_data = {}

        # 临时包装成完整OOXML来提取文本
        temp_ooxml = self._package_complete_ooxml(
            [paragraph_fragment], self.styles_xml_content, self.numbering_xml_content, add_empty_paragraph=False
        )

        # 提取纯文本
        text = self._get_text_from_element(temp_ooxml).strip()
        app_logger.debug(f"长段落文本内容: '{text[:200]}...'")

        # 使用正则表达式匹配所有的键值对
        # 匹配模式：中文字符+冒号+内容（直到下一个键或段落结束）
        import re

        # 匹配中文冒号的键值对
        chinese_colon_pattern = r"([^：\n]+)：([^：]*?)(?=\s*[^：\n]*：|$)"
        matches = re.findall(chinese_colon_pattern, text, re.DOTALL)

        for key, value in matches:
            key = key.strip()
            value = value.strip()

            # 过滤掉空键或明显不是键的内容
            if key and len(key) < 50 and not key.startswith("（") and "申办者" not in key:
                app_logger.debug(f"从长段落提取键值对: '{key}' -> '{value[:50]}...'")

                # 创建只包含值的内容片段
                try:
                    # 使用段落解析器来分离键值对，获取只包含值的OOXML
                    key_extracted, value_ooxml, _ = self._extract_kv_from_ooxml_paragraph_direct(paragraph_fragment)

                    if key_extracted and key_extracted.strip() == key and value_ooxml:
                        # 如果成功分离出键值对，使用只包含值的OOXML
                        processed_fragment = self._create_content_fragment([value_ooxml])
                        value_data = {"type": "ooxml", "data": processed_fragment}
                        kv_data[key] = [value_data]
                    else:
                        # 如果分离失败，回退到原始方法（但这可能包含完整段落）
                        app_logger.debug(
                            f"键值对分离失败，使用原始段落: key_extracted='{key_extracted}', expected='{key}'"
                        )
                        processed_fragment = self._create_content_fragment([paragraph_fragment])
                        value_data = {"type": "ooxml", "data": processed_fragment}
                        kv_data[key] = [value_data]
                except Exception as e:
                    app_logger.warning(f"处理键值对片段失败: {e}")

        # 如果中文冒号没有匹配到，尝试英文冒号
        if not kv_data:
            english_colon_pattern = r"([^:\n]+):([^:]*?)(?=\s*[^:\n]*:|$)"
            matches = re.findall(english_colon_pattern, text, re.DOTALL)

            for key, value in matches:
                key = key.strip()
                value = value.strip()

                if key and len(key) < 50:
                    app_logger.debug(f"从长段落提取键值对(英文冒号): '{key}' -> '{value[:50]}...'")

                    # 创建只包含值的内容片段
                    try:
                        # 使用段落解析器来分离键值对，获取只包含值的OOXML
                        key_extracted, value_ooxml, _ = self._extract_kv_from_ooxml_paragraph_direct(paragraph_fragment)

                        if key_extracted and key_extracted.strip() == key and value_ooxml:
                            # 如果成功分离出键值对，使用只包含值的OOXML
                            processed_fragment = self._create_content_fragment([value_ooxml])
                            value_data = {"type": "ooxml", "data": processed_fragment}
                            kv_data[key] = [value_data]
                        else:
                            # 如果分离失败，回退到原始方法（但这可能包含完整段落）
                            app_logger.debug(
                                f"英文冒号键值对分离失败，使用原始段落: key_extracted='{key_extracted}', expected='{key}'"
                            )
                            processed_fragment = self._create_content_fragment([paragraph_fragment])
                            value_data = {"type": "ooxml", "data": processed_fragment}
                            kv_data[key] = [value_data]
                    except Exception as e:
                        app_logger.warning(f"处理键值对片段失败: {e}")

        app_logger.debug(f"从长段落提取到 {len(kv_data)} 个键值对: {list(kv_data.keys())}")
        return kv_data

    def _extract_kv_from_section_direct_ooxml(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """
        直接从章节的OOXML内容中提取键值对（新的正确方法）。

        这个方法遍历章节中的每个内容块，如果是段落且包含冒号，
        就直接在OOXML层面提取键值对。

        参数:
            section (Dict[str, Any]): 章节数据

        返回:
            Dict[str, Any]: 提取的键值对字典
        """
        kv_data = {}
        content_blocks = section.get("content_blocks", [])

        app_logger.debug(f"开始处理章节 '{section.get('title', '')}' 的 {len(content_blocks)} 个内容块")

        for i, block in enumerate(content_blocks):
            block_type = block.get("type", "")
            block_data = block.get("data", "")

            app_logger.debug(f"处理第 {i + 1} 个块，类型: {block_type}")

            if block_type == "ooxml":
                # 解析OOXML，查找所有段落
                from bs4 import BeautifulSoup

                try:
                    # 为了正确解析，需要包装在根元素中，并添加命名空间声明
                    wrapped_data = f'<root xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">{block_data}</root>'
                    soup = BeautifulSoup(wrapped_data, "xml")

                    # 检查是否包含表格
                    tables = soup.find_all("w:tbl")
                    paragraphs = soup.find_all("w:p")

                    app_logger.debug(f"块中找到 {len(tables)} 个表格，{len(paragraphs)} 个段落")

                    # 优先处理表格（签字页通常以表格为主）
                    if tables:
                        app_logger.debug("发现表格，使用签字页表格解析器")
                        for table in tables:
                            table_fragment = str(table)
                            table_kv = self._extract_kv_from_signature_table_block(table_fragment)
                            if table_kv:
                                app_logger.debug(f"表格解析成功: {list(table_kv.keys())}")
                                kv_data.update(table_kv)
                            else:
                                app_logger.debug("表格解析无结果")

                        # 当有表格时，只处理表格外部的段落
                        # 获取所有表格内部的段落ID，以便排除它们
                        table_paragraph_ids = set()
                        for table in tables:
                            for p in table.find_all("w:p"):
                                para_id = p.get("w14:paraId") or p.get("paraId")
                                if para_id:
                                    table_paragraph_ids.add(para_id)

                        # 只处理不在表格内部的段落
                        external_paragraphs = []
                        for p in paragraphs:
                            para_id = p.get("w14:paraId") or p.get("paraId")
                            if para_id not in table_paragraph_ids:
                                external_paragraphs.append(p)

                        app_logger.debug(f"表格外部段落数量: {len(external_paragraphs)}")
                        paragraphs_to_process = external_paragraphs
                    else:
                        # 没有表格时，处理所有段落
                        paragraphs_to_process = paragraphs

                    # 处理段落
                    if len(paragraphs_to_process) == 0:
                        app_logger.debug("无需处理的段落")

                    for j, paragraph in enumerate(paragraphs_to_process):
                        paragraph_ooxml = str(paragraph)

                        # 尝试从段落中提取键值对
                        key, value_ooxml, remaining = self._extract_kv_from_ooxml_paragraph_direct(paragraph_ooxml)

                        if key and value_ooxml:
                            app_logger.debug(f"从段落 {j + 1} 提取到键值对: '{key}'")

                            # 创建内容片段
                            try:
                                processed_fragment = self._create_content_fragment([value_ooxml])
                                value_data = {"type": "ooxml", "data": processed_fragment}

                                # 处理重复键名：如果键已存在，生成唯一键名
                                unique_key = key
                                counter = 1
                                while unique_key in kv_data:
                                    counter += 1
                                    unique_key = f"{key}_{counter}"

                                if unique_key != key:
                                    app_logger.debug(f"键名重复，使用唯一键名: '{unique_key}'")

                                kv_data[unique_key] = [value_data]
                            except Exception as e:
                                app_logger.warning(f"处理键值对片段失败: {e}")
                        else:
                            # 获取段落文本用于调试
                            try:
                                temp_soup = BeautifulSoup(paragraph_ooxml, "xml")
                                text_content = temp_soup.get_text()
                                if text_content.strip():
                                    app_logger.debug(f"段落 {j + 1} 未找到键值对，内容: '{text_content[:50]}...'")
                                else:
                                    app_logger.debug(f"段落 {j + 1} 为空段落")
                            except:
                                app_logger.debug(f"段落 {j + 1} 未找到键值对")

                except Exception as e:
                    app_logger.warning(f"解析OOXML块失败: {e}")
                    app_logger.debug(f"块数据前200字符: {block_data[:200]}")

            elif block_type == "table":
                # 处理表格（使用签字页专用的表格解析器）
                app_logger.debug("发现表格，使用签字页表格解析器")
                table_kv = self._extract_kv_from_signature_table_block(block_data)
                if table_kv:
                    app_logger.debug(f"表格解析成功: {list(table_kv.keys())}")
                    kv_data.update(table_kv)
                else:
                    app_logger.debug("表格解析无结果")

        app_logger.debug(f"章节最终提取到 {len(kv_data)} 个键值对: {list(kv_data.keys())}")
        return kv_data

    def _extract_kv_from_signature_table_block(self, table_fragment: str) -> Dict[str, Any]:
        """
        从签字页表格中提取键值对（专用方法）。

        签字页表格的特点：
        1. 表格内的键值对不使用冒号分割，而是左列为键，右列为值
        2. 键可能已经包含冒号（如"方案标题："）
        3. 表格可能有2列或3列结构，需要智能处理

        参数:
            table_fragment (str): 包含表格的内容片段

        返回:
            Dict[str, Any]: 提取的键值对字典
        """
        kv_data = {}

        # 临时包装成完整OOXML来解析
        temp_ooxml = self._package_complete_ooxml(
            [table_fragment], self.styles_xml_content, self.numbering_xml_content, add_empty_paragraph=False
        )

        soup = BeautifulSoup(temp_ooxml, "xml")
        table = soup.find("w:tbl")
        if not table:
            return kv_data

        app_logger.debug("开始解析签字页表格")

        for row_idx, row in enumerate(table.find_all("w:tr", recursive=False)):
            cells = row.find_all("w:tc", recursive=False)
            app_logger.debug(f"处理第 {row_idx + 1} 行，包含 {len(cells)} 个单元格")

            if len(cells) >= 2:
                # 获取第一个单元格的文本作为键
                key_text = self._get_paragraph_text(cells[0])

                if key_text and key_text.strip():
                    # 清理键名：移除末尾的冒号和空格
                    clean_key = key_text.strip().rstrip("：:").strip()

                    if clean_key:
                        # 获取第二个单元格（或合并后的单元格）的内容作为值
                        value_cell = cells[1]

                        # 检查是否有跨列的情况（gridSpan）
                        grid_span = value_cell.find("w:gridSpan")
                        if grid_span:
                            span_val = grid_span.get("w:val", "1")
                            app_logger.debug(f"检测到跨列单元格，跨度: {span_val}")

                        # 提取值单元格的所有内容（段落和嵌套表格）
                        content_blocks = []

                        # 按照XML中的原始顺序处理所有直接子元素
                        for child in value_cell.children:
                            if hasattr(child, "name"):
                                if child.name == "p":
                                    # 处理段落元素
                                    paragraph_text = self._get_paragraph_text(child)
                                    if paragraph_text and paragraph_text.strip():
                                        try:
                                            paragraph_fragment = self._create_content_fragment([str(child)])
                                            content_blocks.append({"type": "ooxml", "data": paragraph_fragment})
                                        except Exception as e:
                                            app_logger.warning(f"处理段落片段失败: {e}")
                                            continue
                                elif child.name == "tbl":
                                    # 处理嵌套表格元素
                                    try:
                                        table_fragment = self._create_content_fragment([str(child)])
                                        content_blocks.append({"type": "ooxml", "data": table_fragment})
                                    except Exception as e:
                                        app_logger.warning(f"处理嵌套表格片段失败: {e}")
                                        continue

                        if content_blocks:
                            app_logger.debug(f"提取到键值对: '{clean_key}' -> {len(content_blocks)} 个内容块")
                            kv_data[clean_key] = content_blocks
                        else:
                            app_logger.debug(f"键 '{clean_key}' 的值为空")
                            kv_data[clean_key] = []
                    else:
                        app_logger.debug(f"第 {row_idx + 1} 行的键为空")
                else:
                    app_logger.debug(f"第 {row_idx + 1} 行的第一个单元格为空")
            else:
                app_logger.debug(f"第 {row_idx + 1} 行单元格数量不足（{len(cells)} < 2）")

        app_logger.debug(f"签字页表格解析完成，提取到 {len(kv_data)} 个键值对: {list(kv_data.keys())}")
        return kv_data

    def _extract_summary_from_section_optimized(self, section: Dict[str, Any]) -> Dict[str, str]:
        """
        从摘要章节中提取键值对信息（优化版本）。

        参数:
            section (Dict[str, Any]): 摘要章节数据（使用片段格式）

        返回:
            Dict[str, str]: 提取的键值对信息
        """
        summary_data = {}

        for block in section.get("content_blocks", []):
            if block.get("type") == "ooxml":
                # 检查是否是表格
                temp_ooxml = self._package_complete_ooxml(
                    [block.get("data", "")],
                    self.styles_xml_content,
                    self.numbering_xml_content,
                    add_empty_paragraph=False,
                )
                soup = BeautifulSoup(temp_ooxml, "xml")

                if soup.find("w:tbl"):
                    table_kvs = self._extract_kv_from_table_block_optimized(block.get("data", ""))
                    summary_data.update(table_kvs)
                elif soup.find("w:p"):
                    p_kv = self._extract_kv_from_colon_paragraph_block_optimized(block.get("data", ""))
                    if p_kv:
                        summary_data[p_kv[0]] = [p_kv[1]]

        return summary_data

    def _extract_signature_from_section_optimized(self, section: Dict[str, Any]) -> Dict[str, str]:
        """
        从签字页章节中提取键值对信息（优化版本）。

        参数:
            section (Dict[str, Any]): 签字页章节数据（使用片段格式）

        返回:
            Dict[str, str]: 提取的键值对信息
        """
        signature_data = {}

        for block in section.get("content_blocks", []):
            if block.get("type") == "ooxml":
                # 检查是否是表格
                temp_ooxml = self._package_complete_ooxml(
                    [block.get("data", "")],
                    self.styles_xml_content,
                    self.numbering_xml_content,
                    add_empty_paragraph=False,
                )
                soup = BeautifulSoup(temp_ooxml, "xml")

                if soup.find("w:tbl"):
                    table_kvs = self._extract_kv_from_table_block_optimized(block.get("data", ""))
                    signature_data.update(table_kvs)
                elif soup.find("w:p"):
                    p_kv = self._extract_kv_from_colon_paragraph_block_optimized(block.get("data", ""))
                    if p_kv:
                        signature_data[p_kv[0]] = [p_kv[1]]

        return signature_data

    def _find_section_by_title(self, nodes: List[Dict[str, Any]], title_keyword: str) -> Optional[Dict[str, Any]]:
        """
        在文档的层级结构中，递归地查找第一个标题包含特定关键字的章节。

        改进后的版本：增加了章节有效性检查，避免误识别手动设置大纲等级的内容。

        参数:
            nodes (List[Dict[str, Any]]): 要搜索的章节节点列表（即 `self.sections`）。
            title_keyword (str): 要在章节标题中搜索的关键字。

        返回:
            Optional[Dict[str, Any]]: 找到的第一个匹配的章节字典。如果没找到，返回 None。
        """
        for node in nodes:
            # 检查是否是有效的标题章节
            if self._is_valid_heading_section(node):
                if node.get("title") and title_keyword in node.get("title", ""):
                    return node

            # 递归搜索子节点
            if "children" in node and node["children"]:
                found_in_child = self._find_section_by_title(node.get("children", []), title_keyword)
                if found_in_child:
                    return found_in_child
        return None

    def _is_valid_heading_section(self, section: Dict[str, Any]) -> bool:
        """
        检查一个章节是否是有效的标题章节。

        现在支持三种标题识别方式后，需要更智能地判断章节的有效性：
        1. 检查章节是否有有效的标题级别
        2. 检查标题文本是否有意义（不为空或只包含空白字符）
        3. 检查是否是真正的标题而不是误识别的内容

        参数:
            section (Dict[str, Any]): 章节数据

        返回:
            bool: 是否是有效的标题章节
        """
        # 检查基本属性
        if not section or section.get("type") != "section":
            return False

        # 检查标题级别
        level = section.get("level")
        if level is None or not isinstance(level, int) or level < 1 or level > 6:
            return False

        # 检查标题文本
        title = section.get("title", "").strip()
        if not title:
            return False

        # 检查标题长度（避免误识别很长的内容为标题）
        if len(title) > 100:  # 标题通常不会超过100个字符
            return False

        return True

    def _is_section_boundary(self, current_section: Dict[str, Any], next_section: Dict[str, Any]) -> bool:
        """
        判断两个章节之间是否存在明确的边界。

        这个方法用于确定在提取特定章节内容时，是否应该在某个位置停止。
        考虑了手动设置大纲等级的情况。

        参数:
            current_section (Dict[str, Any]): 当前章节
            next_section (Dict[str, Any]): 下一个章节

        返回:
            bool: 是否存在明确的章节边界
        """
        # 如果任一章节无效，不认为是边界
        if not self._is_valid_heading_section(current_section) or not self._is_valid_heading_section(next_section):
            return False

        current_level = current_section.get("level", 0)
        next_level = next_section.get("level", 0)

        # 如果下一个章节的级别小于等于当前章节，认为是边界
        # 例如：当前是3级标题，下一个是1级、2级或3级标题，都认为是边界
        if next_level <= current_level:
            return True

        # 如果级别差距过大（超过1级），也认为是边界
        # 例如：当前是1级标题，下一个是3级标题（跳过了2级），可能是结构错误
        if next_level - current_level > 1:
            return True

        return False

    def _find_sections_with_table_by_title(
        self, nodes: List[Dict[str, Any]], title_keyword: str
    ) -> List[Dict[str, Any]]:
        """
        在文档的层级结构中，递归地查找所有标题包含特定关键字的章节，并按优先级排序。

        改进后的版本：
        1. 增加了章节有效性检查，避免误识别手动设置大纲等级的内容
        2. 支持更灵活的关键词匹配
        3. 优先级规则：如果章节本身包含表格，优先返回；否则查找其子章节中包含表格的章节

        参数:
            nodes (List[Dict[str, Any]]): 要搜索的章节节点列表。
            title_keyword (str): 要在章节标题中搜索的关键字。

        返回:
            List[Dict[str, Any]]: 按优先级排序的匹配章节列表。
        """
        matching_sections = []

        def _matches_summary_keywords(title: str) -> bool:
            """
            检查标题是否匹配摘要相关的关键词
            支持：摘要、内容提要、提要、概要、概述等变体
            """
            if not title:
                return False

            # 定义摘要相关的关键词列表
            summary_keywords = ["摘要", "内容提要", "提要", "概要"]

            # 检查标题是否包含任何一个关键词
            for keyword in summary_keywords:
                if keyword in title:
                    return True
            return False

        def collect_matching_sections(nodes_list):
            for node in nodes_list:
                # 首先检查是否是有效的标题章节
                if not self._is_valid_heading_section(node):
                    # 如果不是有效的标题章节，仍然递归检查子节点
                    if "children" in node and node["children"]:
                        collect_matching_sections(node.get("children", []))
                    continue

                title = node.get("title", "")
                # 如果是查找摘要相关内容，使用特殊的匹配逻辑
                if title_keyword == "摘要":
                    if _matches_summary_keywords(title):
                        matching_sections.append(node)
                else:
                    # 对于其他关键词，使用原来的简单包含匹配
                    if title and title_keyword in title:
                        matching_sections.append(node)

                if "children" in node and node["children"]:
                    collect_matching_sections(node.get("children", []))

        collect_matching_sections(nodes)

        # 按优先级排序：有表格的章节优先
        def has_table(section):
            for block in section.get("content_blocks", []):
                if block.get("type") == "ooxml":
                    soup = BeautifulSoup(block.get("data", ""), "xml")
                    if soup.find("w:tbl"):
                        return True
                elif block.get("type") == "image":
                    # 对于图片类型的内容块，检查是否是 OOXML 包格式
                    data = block.get("data", "")
                    if data.startswith("<?xml") and "pkg:package" in data:
                        # 这是一个 OOXML 包，检查其中是否包含表格
                        soup = BeautifulSoup(data, "xml")
                        if soup.find("w:tbl"):
                            return True
            return False

        # 将有表格的章节排在前面
        sections_with_table = [s for s in matching_sections if has_table(s)]
        sections_without_table = [s for s in matching_sections if not has_table(s)]

        return sections_with_table + sections_without_table

    def _generate_table_of_contents(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        根据已构建的文档层级结构，生成一个简单的目录（Table of Contents）。

        这个目录本身也是一个嵌套的列表，反映了文档的章节结构。

        参数:
            sections (List[Dict[str, Any]]): 文档的顶层章节列表。

        返回:
            List[Dict[str, Any]]: 表示目录的嵌套列表。
        """
        table_of_contents = []
        for section in sections:
            if title_text := section.get("title"):
                title_text = title_text.strip()
                if not title_text:
                    continue
                entry = {"title": title_text, "level": section.get("level", 1)}
                if children := section.get("children"):
                    child_toc = self._generate_table_of_contents(children)
                    if child_toc:
                        entry["children"] = child_toc
                table_of_contents.append(entry)
        return table_of_contents

    def _build_document_hierarchy_optimized(self, body_element: Tag) -> List[Dict[str, Any]]:
        """
        [★★ 优化版本 - 构建文档的层级结构，使用内容片段而非完整OOXML包 ★★]

        与原版本的区别：
        - 内容块的data字段只包含内容片段，不包含完整的OOXML包装
        - 大大减少了数据重复和文档大小
        - 需要配合shared_ooxml_parts使用

        参数:
            body_element (Tag): BeautifulSoup 解析出的 `<w:body>` 标签对象。

        返回:
            List[Dict[str, Any]]: 一个代表整个文档结构的顶级章节列表。
        """
        node_path: List[Dict[str, Any]] = []  # 维护从根到当前节点的路径，像一个栈
        result_sections = []  # 最终返回的顶级章节列表
        section_content_elements: List[Tag] = []  # 临时收集当前章节的所有内容元素

        def _finalize_current_section_optimized():
            """
            辅助函数：完成当前章节的内容收集与打包（优化版本）。
            """
            if not (node_path and section_content_elements):
                return

            current_section = node_path[-1]
            ooxml_fragments_buffer = []

            def package_buffer_optimized():
                """将缓冲区中的 OOXML 片段打包成一个内容片段。"""
                if ooxml_fragments_buffer:
                    try:
                        # 创建内容片段而非完整OOXML包
                        content_fragment = self._create_content_fragment(ooxml_fragments_buffer)
                        current_section["content_blocks"].append({"type": "ooxml", "data": content_fragment})
                        # 立即清理缓冲区以释放内存
                        ooxml_fragments_buffer.clear()
                    except Exception as e:
                        # 如果包装失败，记录错误但尝试保存原始内容
                        print(f"警告：章节内容片段创建失败: {e}")
                        print(f"缓冲区内容数量: {len(ooxml_fragments_buffer)}")
                        # 尝试创建一个简单的内容片段
                        try:
                            simple_content = "".join(ooxml_fragments_buffer)
                            current_section["content_blocks"].append({"type": "ooxml", "data": simple_content})
                            print("已保存为简单内容片段")
                        except Exception as e2:
                            print(f"保存简单内容也失败: {e2}")
                            # 最后的备选方案：保存为原始文本
                            raw_content = str(ooxml_fragments_buffer)
                            current_section["content_blocks"].append({"type": "raw", "data": raw_content})
                    finally:
                        ooxml_fragments_buffer.clear()

            # 遍历缓存的章节内容元素
            for element in section_content_elements:
                # 检查元素是否包含图片
                blip_tag = element.find("a:blip", {"r:embed": True})
                if blip_tag:
                    # 发现图片，需要判断处理方式
                    # 1. 先打包在它之前的所有 OOXML 内容。
                    package_buffer_optimized()

                    # 2. 检查这个包含图片的元素是否也包含表格或其他重要结构
                    element_name = element.name if hasattr(element, "name") else "unknown"
                    is_table_element = element_name == "tbl"
                    contains_table = element.find("w:tbl") is not None
                    has_table = is_table_element or contains_table

                    if has_table:
                        # 如果是包含图片的表格，保留完整的结构作为片段
                        app_logger.info("处理包含图片的表格，保留完整结构作为片段")
                        try:
                            content_fragment = self._create_content_fragment([str(element)])
                            current_section["content_blocks"].append({"type": "ooxml", "data": content_fragment})
                            app_logger.info("包含图片的表格片段处理成功")
                        except Exception as e:
                            app_logger.warning(f"包装包含图片的表格片段失败: {e}，回退到纯图片模式")
                            # 回退到原来的纯图片处理
                            r_id = blip_tag["r:embed"]
                            image_data = self._process_image_with_oss(r_id, return_text_placeholder=True)
                            if image_data:  # 只有非空字符串才创建image数据块
                                current_section["content_blocks"].append({"type": "image", "data": image_data})
                            else:
                                ooxml_fragments_buffer.append(str(element))
                    else:
                        # 纯图片元素，优先上传到OSS
                        app_logger.info("处理纯图片元素，优先上传到OSS")
                        r_id = blip_tag["r:embed"]
                        image_data = self._process_image_with_oss(r_id, return_text_placeholder=True)
                        if image_data:  # 只有非空字符串才创建image数据块
                            current_section["content_blocks"].append({"type": "image", "data": image_data})
                        else:
                            app_logger.warning(f"无法处理 rId 为 {r_id} 的图片，将此块存为片段")
                            ooxml_fragments_buffer.append(str(element))
                else:
                    # 如果不是图片，将其 XML 字符串添加到缓冲区
                    ooxml_fragments_buffer.append(str(element))

            # 循环结束后，打包所有剩余的 OOXML 内容
            package_buffer_optimized()
            # 立即清理所有临时数据以释放内存
            section_content_elements.clear()
            ooxml_fragments_buffer.clear()

        # --- 主循环：遍历 body 内所有元素 ---
        for element in body_element.children:
            if not isinstance(element, Tag) or not element.name:
                continue

            item_level, title_text = None, None

            # 判断当前元素是否是一个"标题"段落
            if element.name == "p":
                # 使用新的综合方法检测段落的大纲级别
                item_level = self._get_paragraph_outline_level(element)
                if item_level is not None:
                    title_text = self._get_paragraph_text(element)

            # 如果是标题，则开启新章节
            # 注意：忽略标题文本为空或只包含空白字符的标题段落，避免创建空章节
            if item_level is not None and title_text is not None and title_text.strip():
                # 1. 先完成并打包前一个章节的内容
                _finalize_current_section_optimized()

                # 2. 为标题本身生成一个内容片段
                title_fragment = self._create_content_fragment([str(element)], add_empty_paragraph=False)

                # 3. 创建新的章节节点
                section_node = {
                    "type": "section",
                    "level": item_level,
                    "title": title_text,
                    "title_fragment": title_fragment,  # 存储标题的内容片段
                    "content_blocks": [],
                    "children": [],
                }

                # 4. 调整节点在层级树中的位置
                while node_path and node_path[-1]["level"] >= item_level:
                    node_path.pop()

                if node_path:  # 如果路径不为空，作为子节点
                    node_path[-1]["children"].append(section_node)
                else:  # 否则作为顶级节点
                    result_sections.append(section_node)

                node_path.append(section_node)  # 将当前节点压入路径栈
            else:
                # 如果不是标题，就作为当前章节的内容元素收集起来
                if node_path:
                    section_content_elements.append(element)

        # 文档末尾，处理最后一个章节的内容
        _finalize_current_section_optimized()

        return result_sections

    def _build_document_hierarchy(self, body_element: Tag) -> List[Dict[str, Any]]:
        """
        [★★ 核心函数 - 构建文档的层级结构 ★★]

        此函数遍历 `<w:body>` 中的所有顶级元素（段落、表格等），
        通过识别应用了“标题”样式的段落，来构建一个嵌套的树状（或层级）结构。

        处理流程：
        1. 遍历 body 的每个子元素。
        2. 如果元素是一个标题段落，则认为一个旧章节结束，一个新章节开始。
        3. 将旧章节缓存的内容（段落、表格、图片）打包处理，存入旧章节的 `content_blocks`。
        4. 创建新的章节节点，并根据标题级别放入层级结构的正确位置。
        5. 如果元素不是标题，则将其追加到当前章节的内容缓存中。
        6. 在处理过程中，图片会被识别并单独作为一个 "image" 类型的块，其他都是 "ooxml" 块。

        参数:
            body_element (Tag): BeautifulSoup 解析出的 `<w:body>` 标签对象。

        返回:
            List[Dict[str, Any]]: 一个代表整个文档结构的顶级章节列表。每个章节都是一个字典，
                                  可能包含 `children` 字段来表示子章节。
        """
        node_path: List[Dict[str, Any]] = []  # 维护从根到当前节点的路径，像一个栈
        result_sections = []  # 最终返回的顶级章节列表
        section_content_elements: List[Tag] = []  # 临时收集当前章节的所有内容元素

        def _finalize_current_section():
            """
            辅助函数：完成当前章节的内容收集与打包。
            当遇到新标题或文档结束时调用。
            """
            if not (node_path and section_content_elements):
                return

            current_section = node_path[-1]
            ooxml_fragments_buffer = []

            def package_buffer():
                """将缓冲区中的 OOXML 片段打包成一个内容块。"""
                if ooxml_fragments_buffer:
                    try:
                        complete_ooxml = self._package_complete_ooxml(
                            ooxml_fragments_buffer,
                            self.styles_xml_content,
                            self.numbering_xml_content,
                        )
                        current_section["content_blocks"].append({"type": "ooxml", "data": complete_ooxml})
                        # 立即清理缓冲区以释放内存
                        ooxml_fragments_buffer.clear()
                    except Exception as e:
                        # 如果包装失败，记录错误但尝试保存原始内容
                        print(f"警告：章节内容包装失败: {e}")
                        print(f"缓冲区内容数量: {len(ooxml_fragments_buffer)}")
                        # 尝试创建一个简单的 OOXML 包，至少保留内容
                        try:
                            simple_content = "".join(ooxml_fragments_buffer)
                            current_section["content_blocks"].append({"type": "ooxml", "data": simple_content})
                            print("已保存为简单 OOXML 内容块")
                        except Exception as e2:
                            print(f"保存简单内容也失败: {e2}")
                            # 最后的备选方案：保存为原始文本
                            raw_content = str(ooxml_fragments_buffer)
                            current_section["content_blocks"].append({"type": "raw", "data": raw_content})
                    finally:
                        ooxml_fragments_buffer.clear()

            # 遍历缓存的章节内容元素
            for element in section_content_elements:
                # 检查元素是否包含图片
                blip_tag = element.find("a:blip", {"r:embed": True})
                if blip_tag:
                    # 发现图片，需要判断处理方式
                    # 1. 先打包在它之前的所有 OOXML 内容。
                    package_buffer()

                    # 2. 检查这个包含图片的元素是否也包含表格或其他重要结构
                    element_name = element.name if hasattr(element, "name") else "unknown"
                    # 如果元素本身就是表格，或者包含表格子元素
                    is_table_element = element_name == "tbl"  # 去掉命名空间前缀
                    contains_table = element.find("w:tbl") is not None
                    has_table = is_table_element or contains_table
                    app_logger.info(
                        f"发现包含图片的元素: {element_name}, 是表格元素: {is_table_element}, 包含表格: {contains_table}, 最终判断: {has_table}"
                    )

                    if has_table:
                        # 如果是包含图片的表格，保留完整的 OOXML 结构
                        # 标记为 ooxml 类型，这样可以正常提取表格数据
                        app_logger.info("处理包含图片的表格，保留完整OOXML结构")
                        try:
                            complete_ooxml = self._package_complete_ooxml(
                                [str(element)],
                                self.styles_xml_content,
                                self.numbering_xml_content,
                            )
                            # 标记为 ooxml 类型，这样表格提取逻辑可以正常工作
                            current_section["content_blocks"].append({"type": "ooxml", "data": complete_ooxml})
                            app_logger.info("包含图片的表格处理成功")
                        except Exception as e:
                            app_logger.warning(f"包装包含图片的表格失败: {e}，回退到纯图片模式")
                            # 回退到原来的纯图片处理，但使用OSS优化
                            r_id = blip_tag["r:embed"]
                            image_data = self._process_image_with_oss(r_id, return_text_placeholder=True)
                            if image_data:  # 只有非空字符串才创建image数据块
                                current_section["content_blocks"].append({"type": "image", "data": image_data})
                            else:
                                ooxml_fragments_buffer.append(str(element))
                    else:
                        # 纯图片元素（如独立的图片段落），优先上传到OSS
                        app_logger.info("处理纯图片元素，优先上传到OSS")
                        r_id = blip_tag["r:embed"]
                        image_data = self._process_image_with_oss(r_id, return_text_placeholder=True)
                        if image_data:  # 只有非空字符串才创建image数据块
                            current_section["content_blocks"].append({"type": "image", "data": image_data})
                        else:
                            app_logger.warning(f"无法处理 rId 为 {r_id} 的图片，将此块存为 ooxml")
                            ooxml_fragments_buffer.append(str(element))
                else:
                    # 如果不是图片，将其 XML 字符串添加到缓冲区
                    ooxml_fragments_buffer.append(str(element))

            # 循环结束后，打包所有剩余的 OOXML 内容
            package_buffer()
            # 立即清理所有临时数据以释放内存
            section_content_elements.clear()
            ooxml_fragments_buffer.clear()

        # --- 主循环：遍历 body 内所有元素 ---
        for element in body_element.children:
            if not isinstance(element, Tag) or not element.name:
                continue

            item_level, title_text = None, None

            # 判断当前元素是否是一个“标题”段落
            if element.name == "p":
                # 使用新的综合方法检测段落的大纲级别
                item_level = self._get_paragraph_outline_level(element)
                if item_level is not None:
                    title_text = self._get_paragraph_text(element)

            # 如果是标题，则开启新章节
            # 注意：忽略标题文本为空或只包含空白字符的标题段落，避免创建空章节
            if item_level is not None and title_text is not None and title_text.strip():
                # 1. 先完成并打包前一个章节的内容
                _finalize_current_section()

                # 2. 为标题本身生成一个独立的、完整的 OOXML 包
                title_ooxml = self._package_complete_ooxml(
                    [str(element)], self.styles_xml_content, self.numbering_xml_content, add_empty_paragraph=False
                )

                # 3. 创建新的章节节点
                section_node = {
                    "type": "section",
                    "level": item_level,
                    "title": title_text,
                    "title_ooxml": title_ooxml,  # 存储标题的独立OOXML包
                    "content_blocks": [],
                    "children": [],
                }

                # 4. 调整节点在层级树中的位置
                while node_path and node_path[-1]["level"] >= item_level:
                    node_path.pop()

                if node_path:  # 如果路径不为空，作为子节点
                    node_path[-1]["children"].append(section_node)
                else:  # 否则作为顶级节点
                    result_sections.append(section_node)

                node_path.append(section_node)  # 将当前节点压入路径栈
            else:
                # 如果不是标题，就作为当前章节的内容元素收集起来
                if node_path:
                    section_content_elements.append(element)

        # 文档末尾，处理最后一个章节的内容
        _finalize_current_section()

        return result_sections

    def parse_to_structured_dict(self, extract_keys_only: bool = False) -> Dict[str, Any]:
        """
        执行完整的解析流程，返回最终的结构化字典。

        这个字典包含两个顶级键:
        - "sections": 由 `_build_document_hierarchy` 生成的文档层级结构。
        - "key_information": 从特定章节（封面、摘要、签字页）提取的键值对信息。

        参数:
            extract_keys_only (bool): 如果为 True，则在 key_information 中只保留键，值设为空字符串。
                                      这在需要生成待填写的模板时很有用。

        返回:
            Dict[str, Any]: 包含完整解析结果的字典。
        """
        if not self.doc_xml_content:
            return {}

        soup = BeautifulSoup(self.doc_xml_content, "xml")
        body = soup.find("w:body")
        if not body:
            return {}

        # 1. 构建文档的层级内容结构
        hierarchical_content = self._build_document_hierarchy(body)

        # 2. 基于层级结构生成目录
        table_of_contents = self._generate_table_of_contents(hierarchical_content)

        # 3. 为了提取封面等信息，我们需要一个线性的内容块列表
        #    这部分逻辑有些重复，但为了兼容现有的键值提取方法而保留。
        linear_content_blocks = []
        for element in body.children:
            if not isinstance(element, Tag) or not element.name:
                continue
            blip_tag = element.find("a:blip", {"r:embed": True})
            if blip_tag:
                r_id = blip_tag["r:embed"]
                # 使用OSS优化的图片处理方法
                image_data = self._process_image_with_oss(r_id, return_text_placeholder=True)
                if image_data:  # 只有非空字符串才创建image数据块
                    linear_content_blocks.append({"type": "image", "data": image_data})
                else:
                    linear_content_blocks.append(
                        {
                            "type": "ooxml",
                            "data": self._package_complete_ooxml(
                                [str(element)],
                                self.styles_xml_content,
                                self.numbering_xml_content,
                            ),
                        }
                    )
            else:
                linear_content_blocks.append(
                    {
                        "type": "ooxml",
                        "data": self._package_complete_ooxml(
                            [str(element)],
                            self.styles_xml_content,
                            self.numbering_xml_content,
                        ),
                    }
                )

        # 立即释放soup和body对象以节省内存
        del soup, body
        # 强制垃圾回收以释放内存
        gc.collect()

        # 4. 提取特定部分的信息
        # 4.1 提取封面信息：找到“保密声明”作为封面结束的标志
        title_page_data = {}
        split_index = -1
        for i, block in enumerate(linear_content_blocks):
            if block.get("type") == "ooxml":
                element_text = self._get_text_from_element(block.get("data", ""))
                if element_text:
                    cleaned_text = re.sub(r"\s+", "", element_text)
                    if "保密声明" in cleaned_text or "保密申明" in cleaned_text or "声明" in cleaned_text or "保密" in cleaned_text:
                        split_index = i
                        break

        if split_index != -1:
            title_page_blocks = linear_content_blocks[:split_index]
            title_page_data = self._process_title_page_content_blocks(title_page_blocks)
        else:
            app_logger.warning("未找到 '保密声明'或'保密申明'，无法提取标题页信息。")

        # 4.2 提取方案摘要信息
        summary_data = {}
        # 使用新的方法查找包含"摘要"关键字的章节，优先返回有表格的章节
        summary_sections = self._find_sections_with_table_by_title(hierarchical_content, "摘要")
        if summary_sections:
            # 遍历找到的章节，查找第一个包含表格的章节
            for summary_section in summary_sections:
                for block in summary_section.get("content_blocks", []):
                    if block.get("type") == "ooxml":
                        soup = BeautifulSoup(block.get("data", ""), "xml")
                        if soup.find("w:tbl"):  # 摘要信息通常在表格里
                            table_kv_data = self._extract_kv_from_table_block(block)
                            # 保持内容块格式，不转换为简单字典
                            for key, value_blocks in table_kv_data.items():
                                if value_blocks and isinstance(value_blocks, list):
                                    # 直接使用内容块格式，与其他部分保持一致
                                    summary_data[key] = value_blocks
                            app_logger.info(
                                f"在章节 '{summary_section.get('title', '')}' 中找到摘要表格数据，提取了 {len(summary_data)} 个键值对"
                            )
                            break
                if summary_data:  # 如果已经找到数据，跳出外层循环
                    break

        # 4.3 提取签字页信息
        signature_data = {}

        # 调试：列出所有章节标题
        def list_all_section_titles(nodes, level=0):
            titles = []
            for node in nodes:
                title = node.get("title", "")
                if title:
                    titles.append(f"{'  ' * level}[级别{node.get('level', 0)}] {title}")
                if node.get("children"):
                    titles.extend(list_all_section_titles(node["children"], level + 1))
            return titles

        all_titles = list_all_section_titles(hierarchical_content)
        app_logger.info("文档中所有章节标题:\n" + "\n".join(all_titles))

        # 调试：专门查找包含签字相关关键词的章节
        signature_keywords = ["签字", "签字页", "方案签字", "批准签字"]
        found_signature_sections = []

        def find_signature_related_sections(nodes):
            sections = []
            for node in nodes:
                title = node.get("title", "")
                if title:
                    for keyword in signature_keywords:
                        if keyword in title:
                            sections.append(
                                {
                                    "title": title,
                                    "keyword": keyword,
                                    "level": node.get("level", 0),
                                    "has_content": len(node.get("content_blocks", [])) > 0,
                                    "content_block_types": [
                                        block.get("type") for block in node.get("content_blocks", [])
                                    ],
                                }
                            )
                            break
                if node.get("children"):
                    sections.extend(find_signature_related_sections(node["children"]))
            return sections

        found_signature_sections = find_signature_related_sections(hierarchical_content)
        if found_signature_sections:
            app_logger.info("找到的签字相关章节:")
            for section in found_signature_sections:
                app_logger.info(
                    f"  - 标题: '{section['title']}' (匹配关键词: {section['keyword']}, 级别: {section['level']})"
                )
                app_logger.info(
                    f"    内容块数量: {len(section.get('content_block_types', []))}, 类型: {section.get('content_block_types', [])}"
                )
        else:
            app_logger.warning("未找到任何包含签字相关关键词的章节")

        # 查找所有包含"签字"的章节，而不是只找第一个
        signature_sections = self._find_sections_with_table_by_title(hierarchical_content, "签字")
        if signature_sections:
            app_logger.info(f"找到 {len(signature_sections)} 个签字相关章节")
            # 合并所有签字章节的内容块
            all_signature_blocks = []
            for section in signature_sections:
                section_title = section.get("title", "")
                section_blocks = section.get("content_blocks", [])
                app_logger.info(f"处理签字章节: '{section_title}', 包含 {len(section_blocks)} 个内容块")
                all_signature_blocks.extend(section_blocks)

            app_logger.info(f"总共收集到 {len(all_signature_blocks)} 个签字页内容块")
            # 使用与标题页相同的处理逻辑：同时处理表格和冒号段落
            signature_data = self._process_title_page_content_blocks(all_signature_blocks)
            if signature_data:
                app_logger.info(f"成功提取签字页数据: {list(signature_data.keys())}")
            else:
                app_logger.warning("签字页数据提取为空")
        else:
            app_logger.warning("未找到任何包含签字相关关键词的章节")

        # 5. 如果设置了 extract_keys_only，则清空所有提取到的值
        if extract_keys_only:
            app_logger.info("检测到 extract_keys_only=True，将清空 key_information 中相关字段的 value。")
            title_page_data = {key: "" for key in title_page_data.keys()}
            summary_data = {key: "" for key in summary_data.keys()}
            signature_data = {key: "" for key in signature_data.keys()}

        # 6. 组装 key_information 部分，使用更严格的条件来判断字典是否“有意义”。
        #    这个判断对 extract_keys_only 为 true 和 false 的情况都有效。
        key_information = {}

        # 提取到的原始数据源
        sources = {
            "title_page": title_page_data,
            "protocol_summary": summary_data,
            "approval_signature_page": signature_data,
        }

        if extract_keys_only:
            # --- 模式一：只提取键 ---
            # 只要原始解析出了数据（字典不为空），就保留其结构，并将所有值置为空字符串
            app_logger.info("模式: extract_keys_only=True. 保留键，值置空。")
            for key, data_dict in sources.items():
                # 过滤掉key为空字符串的特殊情况
                cleaned_keys_dict = {k.strip(): "" for k in data_dict.keys() if k and k.strip()}
                if cleaned_keys_dict:
                    key_information[key] = cleaned_keys_dict
        else:
            # --- 模式二：提取键和值 ---
            # 现在值可能是单个内容块或内容块数组，与 sections 保持一致
            app_logger.info("模式: extract_keys_only=False. 提取有效键值对（段落级内容块格式）。")
            for key, data_dict in sources.items():
                cleaned_data = {}
                for k, v in data_dict.items():
                    if k and k.strip() and v:
                        # 检查值是否为有效的数据结构（统一为 list[object] 格式）
                        if isinstance(v, list) and all(
                            isinstance(item, dict) and item.get("type") in ["ooxml", "image"] and item.get("data")
                            for item in v
                        ):
                            # 内容块数组
                            cleaned_data[k.strip()] = v
                # 只有当清洗后字典仍有内容时，才将其加入最终结果
                if cleaned_data:
                    key_information[key] = cleaned_data

        # 目录（table_of_contents）不受影响，只要有就添加
        if table_of_contents:
            key_information["table_of_contents"] = table_of_contents

        # 返回最终结果
        return {"sections": hierarchical_content, "key_information": key_information}


def extract_structured_protocol(docx_path: str, extract_keys_only: bool = False) -> Dict[str, Any]:
    """
    一个顶层的 API 函数，封装了 DocxParser 的实例化和调用过程。

    这是外部调用者应该使用的主要入口点。它隐藏了内部实现的复杂性。

    现在统一使用优化版本，将shared_ooxml_parts抽出来，减少数据冗余。

    参数:
        docx_path (str): 指向 .docx 文件的路径。
        extract_keys_only (bool): 是否只提取键名，用于生成模板。

    返回:
        Dict[str, Any]: 从文档中提取的结构化数据，包含shared_ooxml_parts字段。
                       格式: {
                           "shared_ooxml_parts": {...},
                           "sections": [...],
                           "key_information": {...}
                       }

    异常:
        FileNotFoundError: 如果提供的 docx_path 不存在。
        Exception: 在解析过程中发生的任何其他未捕获的异常。
    """
    try:
        app_logger.info(f"开始解析 DOCX 文件: {docx_path}")
        parser = DocxParser(docx_path)

        # 统一使用优化版本，返回包含shared_ooxml_parts的数据结构
        structured_data = parser.parse_to_optimized_dict(extract_keys_only=extract_keys_only)

        app_logger.info(f"文件解析成功: {docx_path}")
        return structured_data
    except FileNotFoundError:
        app_logger.error(f"文件未找到: {docx_path}")
        raise
    except Exception:
        app_logger.error(f"解析文件时发生未知错误: {docx_path}", exc_info=True)
        raise


if __name__ == "__main__":
    """
    这是一个主执行块，用于直接运行此脚本进行测试和调试。
    它会：
    1. 指定一个 .docx 文件路径。
    2. 调用解析函数。
    3. 将结果以格式化的 JSON 形式保存到文件中。
    4. 在控制台打印出解析结果的概览和一些关键的检查项。
    """
    try:
        # file_path = "../data/标题提取.docx"
        file_path = "../data/方案最全/YXC08_8. 临床研究方案_Ver 2.3-P01-15+27-89-D2102(YP)-PH11519(JC).docx"

        # 本地调试也使用优化版本，与OSS存储保持一致
        data = extract_structured_protocol(file_path)

        # 提取各部分数据
        sections_data = data.get("sections", [])
        key_information = data.get("key_information", {})
        shared_ooxml_parts = data.get("shared_ooxml_parts", {})

        # 生成两个独立的JSON文件，模拟OSS存储格式
        sections_json = {"sections": sections_data, "shared_ooxml_parts": shared_ooxml_parts}

        key_information_json = {"key_information": key_information, "shared_ooxml_parts": shared_ooxml_parts}

        # 保存sections JSON
        sections_filename = "../data/output/sections_debug.json"
        with open(sections_filename, "w", encoding="utf-8") as f:
            json.dump(sections_json, f, ensure_ascii=False, indent=2)

        # 保存key_information JSON
        key_info_filename = "../data/output/key_information_debug.json"
        with open(key_info_filename, "w", encoding="utf-8") as f:
            json.dump(key_information_json, f, ensure_ascii=False, indent=2)

        # 保存完整数据（用于调试对比）
        full_filename = "../data/output/full_debug.json"
        with open(full_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        app_logger.info("解析完成！结果已保存到:")
        app_logger.info(f"  - sections JSON: {sections_filename}")
        app_logger.info(f"  - key_information JSON: {key_info_filename}")
        app_logger.info(f"  - 完整数据: {full_filename}")

        app_logger.info("--- 解析结果概览 ---")
        app_logger.info(f"顶层键: {list(data.keys())}")

        if sections := data.get("sections"):
            app_logger.info(f"共找到 {len(sections)} 个顶级章节。")
            if sections:
                first_section = sections[0]
                app_logger.info(
                    f'第一个顶级章节: 级别={first_section.get("level")}, 标题="{first_section.get("title", "")}"'
                )

                if "title_fragment" in first_section and first_section["title_fragment"]:
                    title_fragment = first_section["title_fragment"]
                    app_logger.info(f"  - [√] 章节包含 'title_fragment' 字段，数据长度: {len(title_fragment)}")

                else:
                    app_logger.error("  - [X] 字段缺失：章节 'title_fragment' 字段缺失或为空。")

                app_logger.info(f"第一个顶级章节包含 {len(first_section.get('content_blocks', []))} 个内容块。")
                if content_blocks := first_section.get("content_blocks"):
                    for i, block in enumerate(content_blocks[:2]):
                        app_logger.info(f"  - 内容块 {i + 1}: 类型={block.get('type')}")
                        if block.get("type") == "image":
                            app_logger.info(f"    图片数据长度: {len(block.get('data', ''))}")
                        elif block.get("type") == "ooxml":
                            fragment_data = block.get("data", "")
                            app_logger.info(f"    OOXML 片段长度: {len(fragment_data)}")

        if ki := data.get("key_information"):
            app_logger.info(f"\nkey_information 包含: {list(ki.keys())}")
            app_logger.info(f"标题页键值对数量: {len(ki.get('title_page', {}))}")
            app_logger.info(f"协议摘要键值对数量: {len(ki.get('protocol_summary', {}))}")
            app_logger.info(f"审批签字页键值对数量: {len(ki.get('approval_signature_page', {}))}")

            # 检查目录
            if toc := ki.get("table_of_contents"):
                app_logger.info(f"目录条目数量: {len(toc)}")

        if shared_parts := data.get("shared_ooxml_parts"):
            app_logger.info(f"\nshared_ooxml_parts 包含字段: {list(shared_parts.keys())}")
            total_shared_size = sum(len(str(v)) for v in shared_parts.values())
            app_logger.info(f"共享部分总大小: {total_shared_size} 字符")

    except FileNotFoundError:
        app_logger.error(f"错误: 找不到文件 '{file_path}'。请确保文件路径正确，或修改 'file_path' 变量。")
    except Exception as e:
        app_logger.error(f"处理过程中发生错误: {e}", exc_info=True)

```

如果出现以下情况，请向bio工具发送消息：

- 用户要求您保存或忘记信息。
  - 这样的请求可能使用各种短语，包括但不限于："记住..."，"存储这个"，"添加到记忆"，"注意..."，"忘记..."，"删除这个"等。
  - **任何时候**用户消息包含这些短语或类似短语时，都要思考他们是否在要求您保存或忘记信息。
  - **任何时候**您确定用户在要求您保存或忘记信息时，您都应该**始终**调用bio工具，即使所请求的信息已经存储，看起来极其琐碎或短暂等。
  - **任何时候**您不确定用户是否在要求您保存或忘记信息时，您**必须**在后续消息中向用户寻求澄清。
  - **任何时候**您要向用户发送包含诸如"注意"、"收到"、"我会记住"或类似短语的消息时，您应该确保在向用户发送此消息之前先调用bio工具。
- 用户分享了在未来对话中有用且长期有效的信息。
  - 一个指标是如果用户说诸如"从现在开始"、"将来"、"今后"等。
  - **任何时候**用户分享了可能在未来几个月或几年内都真实的信息时，都要思考是否值得保存在记忆中。
  - 如果用户信息可能会改变您在类似情况下的未来响应，那么它就值得保存在记忆中。

#### 何时不使用bio工具

不要存储随机、琐碎或过于个人化的事实。特别是避免：

- **过于个人化**的细节，可能会让人感到毛骨悚然。
- **短暂**的事实，很快就不重要了。
- **随机**的细节，缺乏明确的未来相关性。
- **冗余**的信息，我们已经知道的关于用户的信息。
  不要保存从用户试图翻译或重写的文本中提取的信息。
  **永远不要**存储属于以下**敏感数据**类别的信息，除非用户明确要求：
- **直接**断言用户个人属性的信息，例如：
  - 种族、民族或宗教
  - 具体的犯罪记录细节（轻微的非刑事法律问题除外）
  - 精确的地理位置数据（街道地址/坐标）
  - 明确识别用户个人属性（例如，"User是拉丁裔"，"User认同基督教"，"User是LGBTQ+"）。
  - 工会会员资格或工会参与
  - 政治派别或批判性/有政治观点的观点
  - 健康信息（医疗状况、心理健康问题、诊断、性生活）
- 但是，您可以存储不是明确识别但仍然敏感的信息，例如：
  - 讨论兴趣、隶属关系或后勤而不明确断言个人属性的文本（例如，"User是来自台湾的国际学生"）。
  - 对兴趣或隶属关系的合理提及而不明确断言身份（例如，"User经常参与LGBTQ+倡导内容"）。
    如顶部所述，**所有**上述指令的例外情况是，如果用户明确要求您保存或忘记信息。在这种情况下，您应该**始终**调用bio工具以尊重他们的请求。

## 2 canmore

canmore工具创建和更新在对话旁边"画布"中显示的文本文档
如果用户要求"使用画布"、"制作画布"或类似要求，您可以假设这是使用canmore的请求，除非他们指的是HTML画布元素。
此工具有3个功能，如下所列。

## canmore.create_textdoc

创建一个新的文本文档以在画布中显示。仅当您100%确定用户想要迭代长文档或代码文件，或者他们明确要求画布时才使用。
期望一个遵循此模式的JSON字符串：
{
  name: string,
  type: "document" | "code/python" | "code/javascript" | "code/html" | "code/java" | ...,
  content: string,
}
对于除上面明确列出的代码语言之外的其他语言，使用"code/languagename"，例如"code/cpp"。
类型"code/react"和"code/html"可以在ChatGPT的UI中预览。如果用户要求用于预览的代码（例如应用程序、游戏、网站），默认为"code/react"。
编写React时：

- 默认导出React组件。
- 使用Tailwind进行样式设计，无需导入。
- 所有NPM库都可用。
- 使用shadcn/ui作为基本组件（例如import { Card, CardContent } from "@/components/ui/card"或import { Button } from "@/components/ui/button"），使用lucide-react作为图标，使用recharts作为图表。
- 代码应该是生产就绪的，具有最小、干净的美学。
- 遵循这些样式指南：
  - 不同的字体大小（例如，标题用xl，文本用base）。
  - 使用Framer Motion进行动画。
  - 基于网格的布局以避免混乱。
  - 2xl圆角，卡片/按钮的柔和阴影。
  - 适当的内边距（至少p-2）。
  - 考虑添加过滤器/排序控件、搜索输入或下拉菜单以进行组织。

## canmore.update_textdoc

更新当前文本文档。除非已经创建了文本文档，否则不要使用此功能。
期望一个遵循此模式的JSON字符串：
{
  updates: {
    pattern: string,
    multiple: boolean,
    replacement: string,
  }[],
}
每个pattern和replacement必须是有效的Python正则表达式（与re.finditer一起使用）和替换字符串（与re.Match.expand一起使用）。
**始终**使用单个更新和".*"作为模式来重写代码文本文档（type="code/*"）。
文档文本文档（type="document"）通常应使用".*"重写，除非用户请求仅更改孤立的、特定的且不影响内容其他部分的小部分。

## canmore.comment_textdoc

评论当前文本文档。除非已经创建了文本文档，否则不要使用此功能。
每个评论必须是关于如何改进文本文档的具体和可行的建议。对于更高级别的反馈，请在聊天中回复。
期望一个遵循此模式的JSON字符串：
{
  comments: {
    pattern: string,
    comment: string,
  }[],
}
每个pattern必须是有效的Python正则表达式（与re.search一起使用）。

## 3 image_gen

// image_gen工具使您能够根据描述生成图像，并根据特定说明编辑现有图像。在以下情况下使用：
// - 用户请求基于场景描述的图像，例如图表、肖像、漫画、表情包或任何其他视觉内容。
// - 用户希望使用特定更改修改附加的图像，包括添加或删除元素、更改颜色、提高质量/分辨率或转换样式（例如，卡通、油画）。
// 指南：
// - 直接生成图像而无需重新确认或澄清，除非用户要求包含他们自己的图像。如果用户请求包含他们自己的图像，即使他们要求您根据已经知道的内容生成，也要简单地建议他们提供自己的图像，以便您可以生成更准确的响应。如果他们已经在当前对话中分享了自己的图像，那么您可以生成该图像。如果您要生成包含他们的图像，您**必须至少一次**要求用户上传自己的图像。这非常重要——用一个自然的澄清问题来做。
// - 每次图像生成后，不要提及与下载相关的任何内容。不要总结图像。不要提出后续问题。生成图像后不要说任何话。
// - 始终使用此工具进行图像编辑，除非用户明确要求其他方式。除非特别指示，否则不要使用python工具进行图像编辑。
// - 如果用户的请求违反我们的内容政策，您提出的任何建议必须与原始违规行为有足够的不同。在响应中清楚地区分您的建议与原始意图。
namespace image_gen {
type text2im = (_: {
prompt?: string,
size?: string,
n?: number,
transparent_background?: boolean,
referenced_image_ids?: string[],
}) => any;
} // namespace image_gen

## 4 python

当您向python发送包含Python代码的消息时，它将在有状态的Jupyter笔记本环境中执行。python将以执行输出响应，或在60.0秒后超时。'/mnt/data'的驱动器可用于保存和持久化用户文件。此会话的互联网访问被禁用。不要进行外部Web请求或API调用，因为它们会失败。
使用caas_jupyter_tools.display_dataframe_to_user(name: str, dataframe: pandas.DataFrame) -> None在有益于用户时可视化呈现pandas DataFrames。
为用户制作图表时：1)永远不要使用seaborn，2)给每个图表自己独立的绘图（没有子图），3)永远不要设置任何特定的颜色——除非用户明确要求。
我重复：为用户制作图表时：1)使用matplotlib而不是seaborn，2)给每个图表自己独立的绘图，3)永远不要指定颜色或matplotlib样式——除非用户明确要求。
如果您要生成文件：

- 您必须为每个支持的文件格式使用指示的库。（不要假设任何其他库可用）：
  - pdf --> reportlab
  - docx --> python-docx
  - xlsx --> openpyxl
  - pptx --> python-pptx
  - csv --> pandas
  - rtf --> pypandoc
  - txt --> pypandoc
  - md --> pypandoc
  - ods --> odfpy
  - odt --> odfpy
  - odp --> odfpy
- 如果您要生成pdf
  - 您必须优先使用reportlab.platypus而不是canvas生成文本内容
  - 如果您要生成韩语、中文或日语文本，您必须使用以下内置的UnicodeCIDFont。要使用这些字体，您必须调用pdfmetrics.registerFont(UnicodeCIDFont(font_name))并将样式应用于所有文本元素
    - 韩语 --> HeiseiMin-W3或HeiseiKakuGo-W5
    - 简体中文 --> STSong-Light
    - 繁体中文 --> MSung-Light
    - 韩语 --> HYSMyeongJo-Medium
- 如果您要使用pypandoc，您只允许调用方法pypandoc.convert_text，并且必须包含参数extra_args=['--standalone']。否则文件将损坏/不完整
  - 例如：pypandoc.convert_text(text, 'rtf', format='md', outputfile='output.rtf', extra_args=['--standalone'])

## 5 web

使用web工具访问来自网络的最新信息，或者当响应用户需要有关其位置的信息时。何时使用web工具的一些示例包括：

- 本地信息：使用web工具回答需要用户位置信息的问题，例如天气、当地企业或活动。
- 新鲜度：如果关于某个主题的最新信息可能会改变或增强答案，那么在您因为知识可能过时而拒绝回答问题时，调用web工具。
- 小众信息：如果答案将从不太广为人知或理解的详细信息中受益（可能在互联网上找到），例如关于小社区、不太知名的公司或深奥法规的详细信息，请直接使用网络来源，而不是依赖预训练的提炼知识。
- 准确性：如果小错误或过时信息的成本很高（例如，使用过时的软件库版本或不知道运动队下一场比赛的日期），那么使用web工具。
  重要：不要尝试使用旧的browser工具或从browser工具生成响应，因为它现在已被弃用或禁用。
  web工具具有以下命令：
- search()：向搜索引擎发出新查询并输出响应。
- open_url(url: str)：打开给定的URL并显示它。

## 扩展资料

https://gist.githubusercontent.com/maoxiaoke/f6d5b28f9104cd856a2622a084f46fd7/raw/f702660df78094b7c977e67b8643b1bc7d2a9a94/gistfile1.txt
