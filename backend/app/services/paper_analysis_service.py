from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.paper import Paper
from app.schemas.paper_analysis import PaperAnalysisResponse
from app.services.llm_service import generate_json
from app.services.paper_analysis_record_service import create_analysis_record
from app.services.paper_service import get_paper


ANALYSIS_FIELDS = (
    "purpose",
    "research_question",
    "value",
    "method",
    "keywords",
    "research_design",
    "findings",
    "logic",
    "variables",
    "application_value",
)


def build_analysis_prompt(paper: Paper) -> str:
    content = (paper.content or "").strip()[:12000]
    title = paper.title.strip() or "未命名论文"

    return f"""
你是一位严谨的论文阅读助手。

请只依据下面提供的论文内容，分析这篇论文的结构化信息。
如果某一项在论文内容中找不到明确依据，请填写“论文中没有找到相关内容。”

请返回 JSON object，字段必须完全包含：
- purpose：研究目的
- research_question：研究问题
- value：研究价值
- method：研究方法，尤其说明实证方法、样本、模型、数据来源等
- keywords：关键词
- research_design：研究设计
- findings：核心发现
- logic：组织逻辑
- variables：研究变量与变量关系。必须尽可能完整识别并分层说明：
  1. 被解释变量/因变量：列出变量名称、含义、度量方式。
  2. 解释变量/自变量：列出变量名称、含义、度量方式。
  3. 中介变量：如有，列出名称、机制路径、在关系中的作用。
  4. 调节变量：如有，列出名称、调节方向或边界条件。
  5. 控制变量：列出所有控制变量，并说明控制目的。
  6. 工具变量、代理变量、替代变量、稳健性变量：如有，分别列出并说明用途。
  7. 变量关系：用清晰文字说明变量之间的因果/相关关系、作用路径、模型逻辑。例如“解释变量 X 影响被解释变量 Y，中介变量 M 解释 X 到 Y 的机制，调节变量 Z 改变 X 对 Y 的影响强度”。
  如果论文没有明确给出某类变量，请写“论文中没有找到相关内容。”，不要编造。
- application_value：应用价值

论文标题：
{title}

论文内容：
{content}
""".strip()


def normalize_analysis_value(data: dict[str, Any], field: str) -> str:
    value = data.get(field)
    if value is None:
        return "论文中没有找到相关内容。"
    if isinstance(value, list):
        return "\n".join(str(item).strip() for item in value if str(item).strip())
    if isinstance(value, dict):
        return "\n".join(
            f"{key}: {item}" for key, item in value.items() if str(item).strip()
        )
    text = str(value).strip()
    return text or "论文中没有找到相关内容。"


def analyze_paper(paper: Paper) -> PaperAnalysisResponse:
    if not paper.content or not paper.content.strip():
        empty_analysis = {
            field: "论文尚未解析出全文，请先导入或上传 PDF。"
            for field in ANALYSIS_FIELDS
        }
        return PaperAnalysisResponse(
            paper_id=paper.id,
            title=paper.title,
            **empty_analysis,
        )

    data = generate_json(build_analysis_prompt(paper))
    analysis = {
        field: normalize_analysis_value(data, field)
        for field in ANALYSIS_FIELDS
    }
    return PaperAnalysisResponse(
        paper_id=paper.id,
        title=paper.title,
        **analysis,
    )


def analyze_papers(db: Session, paper_ids: list[int]) -> list[PaperAnalysisResponse]:
    results: list[PaperAnalysisResponse] = []
    for paper_id in paper_ids:
        paper = get_paper(db, paper_id)
        if paper is not None:
            analysis = analyze_paper(paper)
            record = create_analysis_record(db, analysis)
            results.append(PaperAnalysisResponse.model_validate(record))
    return results
