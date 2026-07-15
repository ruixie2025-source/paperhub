export type PaperAnalysis = {
  id: number | null
  paper_id: number
  title: string
  purpose: string
  research_question: string
  value: string
  method: string
  keywords: string
  research_design: string
  findings: string
  logic: string
  variables: string
  application_value: string
  created_at: string | null
}

const PAPER_ANALYSIS_ENDPOINT = "/papers/analyze"
const PAPER_ANALYSIS_RECORDS_ENDPOINT = "/paper-analyses"

export async function analyzePapers(paperIds: number[]): Promise<PaperAnalysis[]> {
  const response = await fetch(PAPER_ANALYSIS_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ paper_ids: paperIds }),
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `请求失败，状态码 ${response.status}`)
  }

  return response.json() as Promise<PaperAnalysis[]>
}

export async function getLatestPaperAnalyses(paperIds: number[]): Promise<PaperAnalysis[]> {
  const response = await fetch(`${PAPER_ANALYSIS_RECORDS_ENDPOINT}/latest`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ paper_ids: paperIds }),
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `请求失败，状态码 ${response.status}`)
  }

  return response.json() as Promise<PaperAnalysis[]>
}

export async function cleanupOldPaperAnalyses(days = 30): Promise<number> {
  const response = await fetch(`${PAPER_ANALYSIS_RECORDS_ENDPOINT}/cleanup?days=${days}`, {
    method: "DELETE",
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `请求失败，状态码 ${response.status}`)
  }

  const data = (await response.json()) as { deleted_count: number }
  return data.deleted_count
}
